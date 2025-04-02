from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta, timezone

# Custom library imports
from .models import (
    User, Account, Asset, PortfolioHolding, 
    Order, Transaction, Watchlist, 
    WatchlistItem, FinancialStatement, 
    Dividend, AssetDailyPrice,
    DailyPortfolioSnapshot, IntradayPortfolioSnapshot,
    AccountType, OrderType, OrderStatusLookup, OrderStatus,
    # Pydantic models
    UserCreate, AccountCreate, AssetCreate, AssetBase,
    PortfolioHoldingCreate, OrderCreate, TransactionCreate,
    AssetDailyPriceCreate, WatchlistCreate, WatchlistItemCreate
)
from utils.security import generate_account_number


# ===============================================================================
# Lookup Table operations
# ===============================================================================

def get_account_type_by_code(db: Session, type_code: str) -> Optional[AccountType]:
    """Get account type by its code."""
    return db.query(AccountType).filter(AccountType.type_code == type_code).first()


def get_account_type_by_id(db: Session, type_id: int) -> Optional[AccountType]:
    """Get account type by ID."""
    return db.query(AccountType).get(type_id)


def get_all_account_types(db: Session) -> List[AccountType]:
    """Get all available account types."""
    return db.query(AccountType).order_by(AccountType.type_code).all()


def get_order_type_by_code(db: Session, type_code: str) -> Optional[OrderType]:
    """Get order type by its code."""
    return db.query(OrderType).filter(OrderType.type_code == type_code).first()


def get_order_type_by_id(db: Session, type_id: int) -> Optional[OrderType]:
    """Get order type by ID."""
    return db.query(OrderType).get(type_id)


def get_all_order_types(db: Session) -> List[OrderType]:
    """Get all available order types."""
    return db.query(OrderType).order_by(OrderType.type_code).all()


def get_order_status_by_code(db: Session, status_code: str) -> Optional[OrderStatusLookup]:
    """Get order status by its code."""
    return db.query(OrderStatusLookup).filter(OrderStatusLookup.status_code == status_code).first()


def get_order_status_by_id(db: Session, status_id: int) -> Optional[OrderStatusLookup]:
    """Get order status by ID."""
    return db.query(OrderStatusLookup).get(status_id)


def get_all_order_statuses(db: Session) -> List[OrderStatusLookup]:
    """Get all available order statuses."""
    return db.query(OrderStatusLookup).order_by(OrderStatusLookup.display_order).all()


# ===============================================================================
# User operations
# ===============================================================================

def create_user(db: Session, user_data: UserCreate) -> User:
    """
    Create a new user in the database.
    
    Args:
        db: Database session
        user_data: Validated user data from Pydantic model
        
    Returns:
        The created User object
    """
    try:
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=user_data.password,  # Note: This should be hashed before reaching here
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            date_of_birth=user_data.date_of_birth,
            phone_number=user_data.phone_number
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        db.rollback()
        raise e


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get a user by their email address."""
    try:
        return db.query(User).filter(User.email == email).first()
    except Exception as e:
        db.rollback()
        raise e


# ===============================================================================
# Account operations
# ===============================================================================

def create_account(db: Session, account_data: AccountCreate, user_id: int) -> Account:
    """
    Create a new account for a user.
    
    Args:
        db: Database session
        account_data: Validated account data from Pydantic model
        user_id: ID of the user who owns this account
        
    Returns:
        The created Account object
    """
    try:
        # Get the account type to generate an appropriate account number
        account_type = get_account_type_by_id(db, account_data.account_type_id)
        if not account_type:
            raise ValueError(f"Account type with ID {account_data.account_type_id} not found")
            
        account_number = generate_account_number(user_id, account_type.type_code)
        
        new_account = Account(
            user_id=user_id,
            account_type_id=account_data.account_type_id,
            account_number=account_number,
            currency=account_data.currency
        )
        db.add(new_account)
        db.commit()
        db.refresh(new_account)
        return new_account
    except Exception as e:
        db.rollback()
        raise e


# ===============================================================================
# Asset operations
# ===============================================================================

def create_asset(db: Session, asset_data: AssetCreate) -> Asset:
    """
    Create a new asset record.
    
    Args:
        db: Database session
        asset_data: Validated asset data from Pydantic model
        
    Returns:
        The created Asset object
    """
    try:
        if not verify_asset_exists(db, asset_data.symbol):
            new_asset = Asset(
                symbol=asset_data.symbol,
                company_name=asset_data.company_name,
                exchange=asset_data.exchange,
                sector=asset_data.sector,
                industry=asset_data.industry
            )
            db.add(new_asset)
            db.commit()
            db.refresh(new_asset)
            return new_asset
        else:
            raise ValueError(f"Asset with symbol {asset_data.symbol} already exists")
    except Exception as e:
        db.rollback()
        raise e


def get_assets(db: Session, symbol: str = None) -> List[Asset]:
    """Get assets, optionally filtered by symbol."""
    try:
        query = db.query(Asset)
        if symbol:
            query = query.filter(Asset.symbol == symbol)
        return query.all()
    except Exception as e:
        db.rollback()
        raise e


def get_asset_by_symbol(db: Session, symbol: str) -> Optional[Asset]:
    """Get an asset by its symbol."""
    try:
        return db.query(Asset).filter(Asset.symbol == symbol).first()
    except Exception as e:
        db.rollback()
        raise e


def get_asset_by_id(db: Session, asset_id: int) -> Optional[Asset]:
    """Get an asset by its ID."""
    try:
        return db.query(Asset).get(asset_id)
    except Exception as e:
        db.rollback()
        raise e


def verify_asset_exists(db: Session, symbol: str) -> bool:
    """Check if an asset with the given symbol exists."""
    try:
        return db.query(Asset).filter(Asset.symbol == symbol).count() > 0
    except Exception as e:
        db.rollback()
        raise e


# ===============================================================================
# Portfolio operations
# ===============================================================================

def add_portfolio_holding(db: Session, holding_data: PortfolioHoldingCreate) -> PortfolioHolding:
    """
    Add a stock holding to a user's portfolio.
    
    Args:
        db: Database session
        holding_data: Validated holding data from Pydantic model
        
    Returns:
        The created PortfolioHolding object
    """
    try:
        new_holding = PortfolioHolding(
            account_id=holding_data.account_id,
            asset_id=holding_data.asset_id,
            quantity=holding_data.quantity,
            average_purchase_price=holding_data.average_purchase_price
        )
        db.add(new_holding)
        db.commit()
        db.refresh(new_holding)
        return new_holding
    except Exception as e:
        db.rollback()
        raise e


def get_portfolio_holdings(db: Session, account_id: int) -> List[PortfolioHolding]:
    """Get all holdings for an account."""
    try:
        return db.query(PortfolioHolding).filter(
            PortfolioHolding.account_id == account_id
        ).options(
            joinedload(PortfolioHolding.asset)
        ).all()
    except Exception as e:
        db.rollback()
        raise e


# ===============================================================================
# Order operations
# ===============================================================================

def create_order(db: Session, order_data: OrderCreate) -> Order:
    """
    Create a new order for buying or selling an asset.
    
    Args:
        db: Database session
        order_data: Validated order data from Pydantic model
        
    Returns:
        The created Order object
    """
    try:
        # Get default "new" status
        new_status = get_order_status_by_code(db, OrderStatus.NEW)
        if not new_status:
            # Fallback to ID 4 (should be "new" according to our schema setup)
            new_status_id = 4
        else:
            new_status_id = new_status.id
            
        new_order = Order(
            account_id=order_data.account_id,
            asset_id=order_data.asset_id,
            order_type_id=order_data.order_type_id,
            transaction_type=order_data.transaction_type,
            quantity=order_data.quantity,
            price=order_data.price,
            stop_price=order_data.stop_price,
            notes=order_data.notes,
            order_status_id=new_status_id
        )
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        return new_order
    except Exception as e:
        db.rollback()
        raise e


def update_order_status(db: Session, order_id: int, status_code: str) -> Order:
    """Update an order's status by status code."""
    try:
        order = db.query(Order).get(order_id)
        if not order:
            raise ValueError(f"Order with ID {order_id} not found")
            
        status = get_order_status_by_code(db, status_code)
        if not status:
            raise ValueError(f"Order status with code {status_code} not found")
            
        order.order_status_id = status.id
        
        # If the new status is 'filled', update executed_at timestamp
        if status_code == OrderStatus.FILLED:
            order.executed_at = datetime.now(timezone.utc)
            
        db.commit()
        db.refresh(order)
        return order
    except Exception as e:
        db.rollback()
        raise e


def get_orders_by_status(db: Session, account_id: int, status_code: str = None) -> List[Order]:
    """Get orders filtered by account and optionally by status."""
    try:
        query = db.query(Order).filter(Order.account_id == account_id)
        
        # Include related entities for more complete responses
        query = query.options(
            joinedload(Order.asset),
            joinedload(Order.order_type),
            joinedload(Order.order_status)
        )
        
        # If status is 'all', return all orders
        if status_code and status_code != OrderStatus.ALL:
            status = get_order_status_by_code(db, status_code)
            if status:
                query = query.filter(Order.order_status_id == status.id)
                
        return query.order_by(desc(Order.placed_at)).all()
    except Exception as e:
        db.rollback()
        raise e


def get_active_orders(db: Session, account_id: int) -> List[Order]:
    """Get all active orders (those with 'open' status)."""
    try:
        open_status = get_order_status_by_code(db, OrderStatus.OPEN)
        if not open_status:
            return []
            
        return db.query(Order).filter(
            Order.account_id == account_id,
            Order.order_status_id == open_status.id
        ).options(
            joinedload(Order.asset),
            joinedload(Order.order_type),
            joinedload(Order.order_status)
        ).all()
    except Exception as e:
        db.rollback()
        raise e


# ===============================================================================
# Transaction operations
# ===============================================================================

def record_transaction(db: Session, transaction_data: TransactionCreate) -> Transaction:
    """
    Record a new transaction in the system.
    
    Args:
        db: Database session
        transaction_data: Validated transaction data from Pydantic model
        
    Returns:
        The created Transaction object
    """
    try:
        # Use the total_amount from the model if provided
        total_amount = transaction_data.total_amount
        
        new_transaction = Transaction(
            order_id=transaction_data.order_id,
            account_id=transaction_data.account_id,
            asset_id=transaction_data.asset_id,
            transaction_type=transaction_data.transaction_type,
            quantity=transaction_data.quantity,
            price=transaction_data.price,
            commission=transaction_data.commission,
            total_amount=total_amount
        )
        db.add(new_transaction)
        
        # If linked to an order, update order status to 'filled'
        if transaction_data.order_id:
            order = db.query(Order).get(transaction_data.order_id)
            if order:
                filled_status = get_order_status_by_code(db, OrderStatus.FILLED)
                if filled_status:
                    order.order_status_id = filled_status.id
                    order.executed_at = datetime.now(timezone.utc)
                    order.filled_quantity = transaction_data.quantity
        
        db.commit()
        db.refresh(new_transaction)
        return new_transaction
    except Exception as e:
        db.rollback()
        raise e


# ===============================================================================
# Watchlist operations
# ===============================================================================

def create_watchlist(db: Session, watchlist_data: WatchlistCreate, user_id: int) -> Watchlist:
    """
    Create a new watchlist for a user.
    
    Args:
        db: Database session
        watchlist_data: Validated watchlist data from Pydantic model
        user_id: ID of the user who owns this watchlist
        
    Returns:
        The created Watchlist object
    """
    try:
        new_watchlist = Watchlist(
            user_id=user_id,
            name=watchlist_data.name
        )
        db.add(new_watchlist)
        db.commit()
        db.refresh(new_watchlist)
        return new_watchlist
    except Exception as e:
        db.rollback()
        raise e


def add_watchlist_item(db: Session, watchlist_item_data: WatchlistItemCreate, watchlist_id: int) -> WatchlistItem:
    """
    Add an asset to a watchlist.
    
    Args:
        db: Database session
        watchlist_item_data: Validated watchlist item data from Pydantic model
        watchlist_id: ID of the watchlist to add the item to
        
    Returns:
        The created WatchlistItem object
    """
    try:
        new_item = WatchlistItem(
            watchlist_id=watchlist_id,
            asset_id=watchlist_item_data.asset_id
        )
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item
    except Exception as e:
        db.rollback()
        raise e


# ===============================================================================
# Asset price operations
# ===============================================================================

def record_asset_daily_price(db: Session, price_data: AssetDailyPriceCreate) -> AssetDailyPrice:
    """
    Record the daily price for an asset.
    
    Args:
        db: Database session
        price_data: Validated price data from Pydantic model
        
    Returns:
        The created AssetDailyPrice object
    """
    try:
        new_daily_price = AssetDailyPrice(
            asset_id=price_data.asset_id,
            date=price_data.date,
            open_price=price_data.open_price,
            high_price=price_data.high_price,
            low_price=price_data.low_price,
            close_price=price_data.close_price,
            volume=price_data.volume
        )
        db.add(new_daily_price)
        db.commit()
        db.refresh(new_daily_price)
        return new_daily_price
    except Exception as e:
        db.rollback()
        raise e


def get_asset_price_history(db: Session, asset_id: int, 
                            start_date: date = None, 
                            end_date: date = None) -> List[AssetDailyPrice]:
    """Get historical price data for an asset."""
    try:
        query = db.query(AssetDailyPrice).filter(AssetDailyPrice.asset_id == asset_id)
        if start_date:
            query = query.filter(AssetDailyPrice.date >= start_date)
        if end_date:
            query = query.filter(AssetDailyPrice.date <= end_date)
        return query.order_by(AssetDailyPrice.date).all()
    except Exception as e:
        db.rollback()
        raise e


def get_asset_performance(db: Session, asset_id: int, days: int = 30) -> Dict[str, Any]:
    """Calculate performance metrics for an asset over a specified period."""
    try:
        # Get the most recent date in the daily prices
        latest_date = db.query(func.max(AssetDailyPrice.date)).filter(
            AssetDailyPrice.asset_id == asset_id
        ).scalar()

        if not latest_date:
            return None

        start_date = latest_date - timedelta(days=days)

        # Fetch price history
        prices = db.query(AssetDailyPrice).filter(
            AssetDailyPrice.asset_id == asset_id,
            AssetDailyPrice.date >= start_date
        ).order_by(AssetDailyPrice.date).all()

        if not prices:
            return None

        return {
            'start_price': prices[0].close_price,
            'end_price': prices[-1].close_price,
            'performance_percentage': ((prices[-1].close_price - prices[0].close_price) / prices[0].close_price) * 100,
            'highest_price': max(price.high_price for price in prices if price.high_price is not None),
            'lowest_price': min(price.low_price for price in prices if price.low_price is not None),
            'total_volume': sum(price.volume or 0 for price in prices)
        }
    except Exception as e:
        db.rollback()
        raise e


# ===============================================================================
# Portfolio snapshot operations
# ===============================================================================

def create_daily_portfolio_snapshot(
    db: Session, 
    account_id: int, 
    snapshot_date: date,
    portfolio_value: float, 
    cash_balance: float = None,
    unrealized_pnl: float = None, 
    unrealized_pnl_percent: float = None
) -> DailyPortfolioSnapshot:
    """Create a daily snapshot of a portfolio's value and performance."""
    try:
        new_snapshot = DailyPortfolioSnapshot(
            account_id=account_id,
            snapshot_date=snapshot_date,
            portfolio_value=portfolio_value,
            cash_balance=cash_balance,
            unrealized_intraday_pnl=unrealized_pnl,
            unrealized_intraday_pnl_percent=unrealized_pnl_percent
        )
        db.add(new_snapshot)
        db.commit()
        db.refresh(new_snapshot)
        return new_snapshot
    except Exception as e:
        db.rollback()
        raise e


def create_intraday_portfolio_snapshot(
    db: Session, 
    account_id: int, 
    portfolio_value: float
) -> IntradayPortfolioSnapshot:
    """Create an intraday snapshot of a portfolio's current value."""
    try:
        new_snapshot = IntradayPortfolioSnapshot(
            account_id=account_id,
            record_timestamp=datetime.now(timezone.utc),
            portfolio_value=portfolio_value
        )
        db.add(new_snapshot)
        db.commit()
        db.refresh(new_snapshot)
        return new_snapshot
    except Exception as e:
        db.rollback()
        raise e


# ===============================================================================
# Portfolio summary operation
# ===============================================================================

def get_user_portfolio_summary(db: Session, user_id: int) -> Dict[str, Any]:
    """Get a summary of a user's portfolio across all their accounts."""
    try:
        # Get all accounts for the user
        accounts = db.query(Account).filter(Account.user_id == user_id).all()
        
        total_portfolio_value = 0
        holdings_details = []

        for account in accounts:
            # Get portfolio holdings with asset details
            holdings = db.query(PortfolioHolding).filter(
                PortfolioHolding.account_id == account.id
            ).options(joinedload(PortfolioHolding.asset)).all()

            for holding in holdings:
                # Get latest asset price
                latest_price = db.query(AssetDailyPrice).filter(
                    AssetDailyPrice.asset_id == holding.asset_id
                ).order_by(desc(AssetDailyPrice.date)).first()

                current_value = holding.quantity * (latest_price.close_price if latest_price else holding.average_purchase_price)
                total_portfolio_value += current_value

                holdings_details.append({
                    'symbol': holding.asset.symbol,
                    'company_name': holding.asset.company_name,
                    'quantity': holding.quantity,
                    'average_price': holding.average_purchase_price,
                    'current_price': latest_price.close_price if latest_price else None,
                    'current_value': current_value,
                    'total_gain_loss': current_value - (holding.quantity * holding.average_purchase_price)
                })

        return {
            'total_portfolio_value': total_portfolio_value,
            'holdings': holdings_details
        }
    except Exception as e:
        db.rollback()
        raise e