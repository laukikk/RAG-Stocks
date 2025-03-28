from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime

# Alpaca client and models imports
from trading.alpaca_client import AlpacaClient
from trading.calls import (
    get_account,
    place_order,
    get_orders,
    get_positions,
    get_position,
    get_assets,
    get_asset_by_symbol,
    get_latest_quote,
    get_historical_bars
)

from trading.models import (
    AlpacaTimeFrame,
    AlpacaOrderRequest, 
    AlpacaOrderType, 
    AlpacaOrderSide, 
    AlpacaTimeInForce,
    AlpacaOrderStatus
)

# Initialize Alpaca client (singleton)
alpaca_client = AlpacaClient()

# Parent router
trading_platform_router = APIRouter(prefix="/trading")

# =============================================================================
# Account Router
# =============================================================================
account_router = APIRouter(prefix="/account")

@account_router.get("/details", summary="Get Alpaca account details")
def get_account_details_route(client=Depends(alpaca_client.trading_client)):
    """
    Retrieve detailed information about the Alpaca trading account.
    """
    try:
        account = get_account(client)
        return account
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# Orders Router
# =============================================================================
orders_router = APIRouter(prefix="/orders")

@orders_router.post("/place", summary="Place a new order")
def place_order_route(
    symbol: str, 
    qty: float, 
    side: AlpacaOrderSide, 
    order_type: AlpacaOrderType,
    time_in_force: AlpacaTimeInForce = AlpacaTimeInForce.DAY,
    limit_price: Optional[float] = None,
    stop_price: Optional[float] = None,
    client=Depends(alpaca_client.trading_client)
):
    """
    Place a new order with specified parameters.
    """
    try:
        order_request = AlpacaOrderRequest(
            symbol=symbol,
            qty=qty,
            side=side,
            type=order_type,
            time_in_force=time_in_force,
            limit_price=limit_price,
            stop_price=stop_price
        )
        order = place_order(client, order_request)
        return order
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@orders_router.get("/", summary="Get list of orders")
def get_orders_route(
    status: Optional[List[AlpacaOrderStatus]] = Query(None),
    limit: int = Query(50),
    after: Optional[datetime] = Query(None),
    until: Optional[datetime] = Query(None),
    client=Depends(alpaca_client.trading_client)
):
    """
    Retrieve a list of orders with optional filtering.
    """
    try:
        orders = get_orders(
            client, 
            status=status, 
            limit=limit, 
            after=after, 
            until=until
        )
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# Positions Router
# =============================================================================
positions_router = APIRouter(prefix="/positions")

@positions_router.get("/", summary="Get all open positions")
def get_positions_route(client=Depends(alpaca_client.trading_client)):
    """
    Retrieve all open positions in the account.
    """
    try:
        positions = get_positions(client)
        return positions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@positions_router.get("/{symbol}", summary="Get position for a specific symbol")
def get_position_route(symbol: str, client=Depends(alpaca_client.trading_client)):
    """
    Retrieve position details for a specific stock symbol.
    """
    try:
        position = get_position(client, symbol)
        if position is None:
            raise HTTPException(status_code=204, detail="No Postions Found")
        return position
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# Assets Router
# =============================================================================
assets_router = APIRouter(prefix="/assets")

@assets_router.get("/", summary="Get list of assets")
def get_assets_route(client=Depends(alpaca_client.trading_client)):
    """
    Retrieve a list of assets with optional filtering.
    """
    try:
        assets = get_assets(client)
        return assets
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@assets_router.get("/{symbol}", summary="Get asset details by symbol")
def get_asset_by_symbol_route(symbol: str, client=Depends(alpaca_client.trading_client)):
    """
    Retrieve asset details by stock symbol.
    """
    try:
        asset = get_asset_by_symbol(client, symbol)
        return asset
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# Market Data Router
# =============================================================================
market_data_router = APIRouter(prefix="/market-data")

@market_data_router.get("/quote/{symbol}", summary="Get latest quote for a symbol")
def get_latest_quote_route(symbol: str, client=Depends(alpaca_client.stock_client)):
    """
    Retrieve the latest quote for a given stock symbol.
    """
    try:
        quote = get_latest_quote(client, symbol)
        return quote
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@market_data_router.get("/historical-bars/{symbol}", summary="Get historical price bars")
def get_historical_bars_route(
    symbol: str, 
    timeframe: AlpacaTimeFrame = AlpacaTimeFrame.DAY,
    start: Optional[datetime] = None, 
    end: Optional[datetime] = None,
    client=Depends(alpaca_client.stock_client)
):
    """
    Retrieve historical price bars for a given stock symbol.
    """
    try:
        alpaca_timeframe = timeframe.to_timeframe()
        bars = get_historical_bars(
            client, 
            symbol, 
            alpaca_timeframe, 
            start, 
            end
        )
        return bars
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Add routers to parent router
trading_platform_router.include_router(account_router, tags=["Trading Platform - Account"])
trading_platform_router.include_router(orders_router, tags=["Trading Platform - Orders"])
trading_platform_router.include_router(positions_router, tags=["Trading Platform - Positions"])
trading_platform_router.include_router(assets_router, tags=["Trading Platform - Assets"])
trading_platform_router.include_router(market_data_router, tags=["Trading Platform - Market Data"])
