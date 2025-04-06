from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
import logging

# Import the AlpacaClient as in original code
from trading.alpaca_client import AlpacaClient

# Alpaca imports for types and models
from alpaca.trading.requests import GetOrdersRequest, GetAssetsRequest, QueryOrderStatus
from alpaca.trading.enums import OrderStatus, OrderSide, AssetStatus
from alpaca.trading.models import Order as AlpacaOrder
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

from database.calls import (
    add_portfolio_holding,
    create_order, update_order, 
    get_account_by_external_id, get_order_by_external_id,
    record_transaction, record_transaction_from_order, update_order_status,
    create_asset, get_asset_by_symbol as db_get_asset_by_symbol, verify_asset_exists,
    record_asset_daily_price,
    get_portfolio_holdings, close_portfolio_holding, update_portfolio_holding,
)
from database.models import (
    AssetCreate,
    PortfolioHoldingCreate,
    OrderCreate,
    TransactionCreate,
    AssetDailyPriceCreate,
    Asset,
    TransactionType,
    OrderStatus as DBOrderStatus,
    OrderUpdate
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("alpaca_sync.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("alpaca_sync")

# Create clients as global variables to be reused
alpaca = AlpacaClient()
trading_client = alpaca.trading_client()
stock_client = alpaca.stock_client()

def ensure_asset_exists(db: Session, account_id: int, symbol: str, history_sync: bool = True) -> Asset:
    """
    Ensure the asset exists in the database, if not, create it.
    
    Args:
        db: SQLAlchemy database session
        account_id: The ID of the account in the PostgreSQL database
        symbol: The stock symbol
        history_sync: Whether to sync historical data for the asset
        
    Returns:
        The Asset object from the database
    """
    # First check if asset exists in our database
    db_asset = db_get_asset_by_symbol(db, symbol)
    
    if not db_asset:
        logger.info(f"Asset {symbol} not found in database, fetching from Alpaca")
        # Asset doesn't exist, get it from Alpaca
        try:
            alpaca_asset = trading_client.get_asset(symbol)
            
            if alpaca_asset:
                # Convert Alpaca asset to our database model
                asset_create = AssetCreate(
                    symbol=alpaca_asset.symbol,
                    company_name=alpaca_asset.name,
                    exchange=alpaca_asset.exchange.value if hasattr(alpaca_asset.exchange, 'value') else str(alpaca_asset.exchange),
                    external_asset_id=alpaca_asset.id,
                    # We don't have sector/industry from Alpaca, 
                    # would need another data source for this
                )
                
                # Create the asset in our database
                db_asset = create_asset(db, asset_create)
                logger.info(f"Created asset in database: {alpaca_asset.symbol}")
                
                # Optionally fetch historical data for the new asset
                if history_sync:
                    sync_asset_historical_data(db, account_id, symbol)
            else:
                logger.error(f"Asset {symbol} not found in Alpaca")
                raise ValueError(f"Asset {symbol} not found in Alpaca")
            
        except Exception as e:
            logger.error(f"Failed to fetch or create asset {symbol}: {str(e)}")
            raise
    
    return db_asset

def sync_positions(db: Session, account_id: int) -> List[Dict[str, Any]]:
    """
    Sync positions from Alpaca to the database.
    
    Args:
        db: SQLAlchemy database session
        account_id: The ID of the account in the PostgreSQL database
        
    Returns:
        A list of synced positions
    """
    logger.info("Starting position sync")
    
    # Get all positions from Alpaca directly
    alpaca_positions = trading_client.get_all_positions()
    logger.info(f"Found {len(alpaca_positions)} positions in Alpaca")
    
    # Get existing holdings in the database
    db_holdings = get_portfolio_holdings(db, account_id)
    db_holdings_map = {h.asset.symbol: h for h in db_holdings}
    
    results = []
    
    # Process each position from Alpaca
    for position in alpaca_positions:
        symbol = position.symbol
        qty = float(position.qty)
        avg_price = float(position.avg_entry_price)
        
        # Ensure the asset exists in our database
        ensure_asset_exists(db, account_id, symbol)
        
        # Check if we already have this position in our database
        if symbol in db_holdings_map:
            holding = db_holdings_map[symbol]
            
            # If quantities or prices differ significantly, update the holding
            if (abs(holding.quantity - qty) > 0.0001 or 
                abs(float(holding.average_purchase_price) - round(avg_price, 2)) > 0.01):
                
                logger.info(f"Updating position for {symbol}: qty={qty}, avg_price={avg_price}")
                
                # Currently the update is done by creating a new holding
                # which will replace the existing one due to unique constraint
                asset_id = holding.asset_id
                
                holding_data = PortfolioHoldingCreate(
                    account_id=account_id,
                    asset_id=asset_id,
                    quantity=qty,
                    average_purchase_price=avg_price
                )
                
                updated_holding = update_portfolio_holding(db, holding_data)
                results.append({
                    "symbol": symbol,
                    "action": "updated",
                    "qty": qty,
                    "avg_price": avg_price
                })
            else:
                # No changes needed, quantities and prices match
                logger.info(f"Position for {symbol} is already up to date")
        else:
            # New position, need to add it
            logger.info(f"Adding new position for {symbol}: qty={qty}, avg_price={avg_price}")
            
            # Get the asset ID from the database
            asset = db_get_asset_by_symbol(db, symbol)
            
            holding_data = PortfolioHoldingCreate(
                account_id=account_id,
                asset_id=asset.id,
                quantity=qty,
                average_purchase_price=avg_price
            )
            
            new_holding = add_portfolio_holding(db, holding_data)
            results.append({
                "symbol": symbol,
                "action": "added",
                "qty": qty,
                "avg_price": avg_price
            })
    
    # Check for positions in the database that no longer exist in Alpaca
    # (These might have been closed)
    alpaca_symbols = {p.symbol for p in alpaca_positions}
    for symbol, holding in db_holdings_map.items():
        if symbol not in alpaca_symbols:
            logger.info(f"Position for {symbol} exists in database but not in Alpaca, closing it")
            # Closing PortfolioHolding
            holding_data = PortfolioHoldingCreate(
                account_id=account_id,
                asset_id=holding.asset_id,
                quantity=0,  # Not applicable when closing
                average_purchase_price=0  # Not applicable when closing
            )
            close_portfolio_holding(db, holding_data)
            
            logger.info(f"Closed position for {symbol}")
            
    logger.info(f"Position sync completed, processed {len(results)} positions")
    return results

def sync_orders(db: Session, account_id: int, days_back: int = 7) -> List[Dict[str, Any]]:
    """
    Sync orders from Alpaca to the database.
    
    This function will:
    1. Fetch orders from Alpaca for the specified date range
    2. Add new orders that don't exist in the database
    3. Update existing orders if their status or details have changed
    
    Args:
        db: SQLAlchemy database session
        account_id: The ID of the account in the PostgreSQL database
        days_back: Number of days to look back for orders
            
    Returns:
        A list of synced orders with their action (added/updated)
    """
    logger.info(f"Starting order sync for the last {days_back} days")
    
    # Calculate the date range
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days_back)
    
    # Get all orders from Alpaca within the date range using the request object
    request_params = GetOrdersRequest(
        status="all",
        limit=500,
        after=start_date.isoformat(),
        until=end_date.isoformat()
    )
    
    alpaca_orders = trading_client.get_orders(request_params)
    
    logger.info(f"Found {len(alpaca_orders)} orders in Alpaca")
    
    results = []
    
    # Process each order from Alpaca
    for order in alpaca_orders:
        symbol = order.symbol
        external_order_id = order.id
        
        # Ensure the asset exists in our database
        asset = ensure_asset_exists(db, account_id, symbol)
        
        # Check if this order already exists in our database by external_order_id
        existing_order = get_order_by_external_id(db, external_order_id)
        
        # Map Alpaca order status to our database status
        alpaca_status = order.status
        db_status = None
        
        if hasattr(DBOrderStatus, alpaca_status.name):
            db_status = getattr(DBOrderStatus, alpaca_status.name)
        else:
            logger.warning(f"Cannot map Alpaca status {alpaca_status} to DB status")
            # Default to some reasonable status
            db_status = DBOrderStatus.NEW
        
        if existing_order:
            # Order exists, check if it needs to be updated
            if (existing_order.order_status.status_code != db_status or
                abs(existing_order.quantity - float(order.qty)) > 0.0001 or
                (existing_order.filled_quantity is None and order.filled_qty is not None) or
                (existing_order.filled_quantity is not None and 
                order.filled_qty is not None and
                abs(existing_order.filled_quantity - float(order.filled_qty)) > 0.0001)):
                
                logger.info(f"Updating order {external_order_id} with new status {db_status}")
                
                order_data = OrderUpdate(
                    order_status=db_status,
                    filled_quantity=float(order.filled_qty) if order.filled_qty else None,
                    filled_avg_price=float(order.filled_avg_price) if order.filled_avg_price else None
                )
                
                # Update the order
                update_order(
                    db, 
                    existing_order.id, 
                    order_data
                )
                
                results.append({
                    "symbol": symbol,
                    "action": "updated",
                    "external_id": external_order_id,
                    "status": alpaca_status.name,
                    "qty": order.qty,
                    "filled_qty": order.filled_qty,
                    "price": order.limit_price or order.filled_avg_price,
                })
                
                # If order is now filled and wasn't before, create a transaction
                if alpaca_status == OrderStatus.FILLED and order.filled_avg_price and not existing_order.transactions:
                    record_transaction_from_order(existing_order.id, order)
            else:
                # Order exists and is up to date
                logger.info(f"Order {external_order_id} is already up to date")
                results.append({
                    "symbol": symbol,
                    "action": "unchanged",
                    "external_id": external_order_id,
                    "status": alpaca_status.name,
                })
        else:
            # New order, need to add it
            logger.info(f"Adding new order {external_order_id} for {symbol}")
            
            # Map Alpaca order type to our database order type
            # TODO: Implement proper order type mapping
            order_type_id = 1  # Default to market order for now
            
            # Create an order in our database
            order_data = OrderCreate(
                account_id=account_id,
                asset_id=asset.id,
                order_type_id=order_type_id,
                transaction_type=TransactionType.BUY if order.side == OrderSide.BUY else TransactionType.SELL,
                quantity=float(order.qty),
                price=float(order.limit_price) if order.limit_price else None,
                stop_price=float(order.stop_price) if order.stop_price else None,
                external_order_id=external_order_id,
                filled_quantity=float(order.filled_qty) if order.filled_qty else None
            )
            
            # Create the order in our database
            db_order = create_order(db, order_data)
            
            # Update the order status if needed
            if db_status != DBOrderStatus.NEW:
                update_order_status(db, db_order.id, db_status)
            
            results.append({
                "symbol": symbol,
                "action": "added",
                "external_id": external_order_id,
                "status": alpaca_status.name,
                "qty": order.qty,
                "filled_qty": order.filled_qty,
                "price": order.limit_price or order.filled_avg_price,
            })
            
            # If order is filled, create a transaction record
            if alpaca_status == OrderStatus.FILLED and order.filled_avg_price:
                record_transaction_from_order(db_order.id, order)
    
    logger.info(f"Order sync completed, processed {len(results)} orders")
    return results

def sync_assets(db: Session) -> List[Dict[str, Any]]:
    """
    Sync assets from Alpaca to the database.
    
    Args:
        db: SQLAlchemy database session
        account_id: The ID of the account in the PostgreSQL database
        
    Returns:
        A list of synced assets
    """
    logger.info("Starting asset sync")
    
    # Get all assets from Alpaca using the request object
    request_params = GetAssetsRequest(
        status=AssetStatus.ACTIVE
    )
    
    alpaca_assets = trading_client.get_all_assets(request_params)
    
    # Filter for only tradable assets
    tradable_assets = [asset for asset in alpaca_assets if asset.tradable]
    
    logger.info(f"Found {len(tradable_assets)} tradable assets in Alpaca")
    
    results = []
    
    for asset in tradable_assets:
        symbol = asset.symbol
        
        # Check if asset already exists in our database
        if not verify_asset_exists(db, symbol):
            asset_create = AssetCreate(
                symbol=asset.symbol,
                company_name=asset.name,
                exchange=asset.exchange.value if hasattr(asset.exchange, 'value') else str(asset.exchange)
            )
            
            try:
                db_asset = create_asset(db, asset_create)
                results.append({
                    "symbol": symbol,
                    "action": "added",
                    "name": asset.name,
                    "exchange": asset.exchange.value if hasattr(asset.exchange, 'value') else str(asset.exchange)
                })
            except Exception as e:
                logger.error(f"Failed to create asset {symbol}: {str(e)}")
        else:
            # Asset already exists
            results.append({
                "symbol": symbol,
                "action": "exists",
                "name": asset.name,
                "exchange": asset.exchange.value if hasattr(asset.exchange, 'value') else str(asset.exchange)
            })
    
    logger.info(f"Asset sync completed, added {len([r for r in results if r['action'] == 'added'])} new assets")
    return results

def sync_asset_historical_data(db: Session, account_id: int, symbol: str, days: int = 365) -> List[Dict[str, Any]]:
    """
    Sync historical price data for a specific asset.
    
    Args:
        db: SQLAlchemy database session
        account_id: The ID of the account in the PostgreSQL database
        symbol: The stock symbol
        days: Number of days of historical data to sync
        
    Returns:
        A list of price records synced
    """
    logger.info(f"Syncing historical data for {symbol} for the last {days} days")
    
    # Ensure the asset exists
    asset = ensure_asset_exists(db, account_id, symbol, history_sync=False)
    
    # Calculate the date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Get historical bars from Alpaca using the request object
    request_params = StockBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=TimeFrame.Day,
        start=start_date,
        end=end_date
    )
    
    bars_response = stock_client.get_stock_bars(request_params)
    
    # The response is a dictionary with symbols as keys
    if symbol in bars_response:
        bars = bars_response[symbol]
        logger.info(f"Found {len(bars)} historical bars for {symbol}")
    else:
        logger.warning(f"No historical data found for {symbol}")
        return []
    
    results = []
    
    for bar in bars:
        # Create price data
        bar_date = bar.timestamp.date()
        
        price_data = AssetDailyPriceCreate(
            asset_id=asset.id,
            date=bar_date,
            open_price=bar.open,
            high_price=bar.high,
            low_price=bar.low,
            close_price=bar.close,
            volume=bar.volume
        )
        
        try:
            # Record the daily price
            daily_price = record_asset_daily_price(db, price_data)
            results.append({
                "date": bar_date,
                "action": "added",
                "close": bar.close
            })
        except Exception as e:
            # Might fail if price record already exists for this date
            logger.warning(f"Could not add price for {symbol} on {bar_date}: {str(e)}")
            results.append({
                "date": bar_date,
                "action": "failed",
                "error": str(e)
            })
    
    logger.info(f"Historical data sync for {symbol} completed, processed {len(results)} price points")
    return results

def full_sync(db: Session, account_id: int, days_back_for_orders: int = 7) -> Dict[str, Any]:
    """
    Perform a full synchronization of all data from Alpaca.
    
    Args:
        db: SQLAlchemy database session
        account_id: The ID of the account in the PostgreSQL database
        days_back_for_orders: Number of days to look back for orders
        
    Returns:
        A dictionary with the results of each sync operation
    """
    logger.info("Starting full sync from Alpaca")
    
    results = {}
    
    # Sync assets first to ensure we have all assets in our database
    # results["assets"] = sync_assets(db, account_id)
    
    # Sync positions
    results["positions"] = sync_positions(db, account_id)
    
    # Sync orders and transactions
    results["orders"] = sync_orders(db, account_id, days_back=days_back_for_orders)
    
    logger.info("Full sync completed")
    return results