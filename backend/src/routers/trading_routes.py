from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from datetime import datetime

# Import Alpaca client for dependency injection
from trading.alpaca_client import AlpacaClient

# Import Alpaca enums
from alpaca.trading.enums import OrderSide, OrderType, TimeInForce, OrderStatus
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit

# Import Alpaca request models
from alpaca.trading.requests import (
    MarketOrderRequest,
    LimitOrderRequest,
    StopOrderRequest,
    StopLimitOrderRequest,
    TrailingStopOrderRequest,
    GetOrdersRequest,
    GetOrderByIdRequest,
    ReplaceOrderRequest,
    ClosePositionRequest,
    GetAssetsRequest
)

# Initialize Alpaca client (singleton)
alpaca_client = AlpacaClient()

# Parent router
trading_platform_router = APIRouter(prefix="/trading")

# =============================================================================
# Account Router
# =============================================================================
account_router = APIRouter(prefix="/account")

@account_router.get("/details", summary="Get Account Details")
def get_account_details_route(client=Depends(alpaca_client.trading_client)):
    """
    Retrieve detailed information about the Alpaca trading account.
    """
    try:
        account = client.get_account()
        return account
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# Positions Router
# =============================================================================
positions_router = APIRouter(prefix="/positions")

@positions_router.get("/", summary="Get All Positions")
def get_all_positions_route(client=Depends(alpaca_client.trading_client)):
    """
    Retrieve all open positions in the account.
    """
    try:
        positions = client.get_all_positions()
        return positions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@positions_router.get("/{symbol}", summary="Get Open Position")
def get_open_position_route(symbol: str, client=Depends(alpaca_client.trading_client)):
    """
    Retrieve the open position for a specific stock symbol.
    """
    try:
        position = client.get_position(symbol)
        if not position:
            raise HTTPException(status_code=204, detail="No Position Found")
        return position
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@positions_router.post("/close-all", summary="Close All Positions")
def close_all_positions_route(client=Depends(alpaca_client.trading_client)):
    """
    Close all open positions in the account.
    """
    try:
        # If a request object is needed, wrap parameters accordingly.
        response = client.close_all_positions()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@positions_router.delete("/{symbol}/close", summary="Close A Position")
def close_position_route(symbol: str, client=Depends(alpaca_client.trading_client)):
    """
    Close the position for a specific stock symbol.
    """
    try:
        # Wrap parameters in a ClosePositionRequest. Here we assume no qty or percentage is provided.
        close_req = ClosePositionRequest(qty=None, percentage=None)
        response = client.close_position(symbol, close_req)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@positions_router.post("/{symbol}/exercise", summary="Exercise An Option Contract")
def exercise_option_contract_route(symbol: str, client=Depends(alpaca_client.trading_client)):
    """
    Exercise an option contract for a given stock symbol.
    """
    try:
        # Assuming the client method accepts a symbol directly for exercising an option contract.
        response = client.exercise_option_contract(symbol)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# Orders Router
# =============================================================================
orders_router = APIRouter(prefix="/orders")

@orders_router.post("/place", summary="Create A New Order")
def create_order_route(
    symbol: str, 
    qty: float, 
    side: OrderSide,           
    order_type: OrderType,     
    time_in_force: TimeInForce = TimeInForce.DAY,
    limit_price: Optional[float] = None,
    stop_price: Optional[float] = None,
    client=Depends(alpaca_client.trading_client)
):
    """
    Place a new order with the specified parameters using the appropriate request object.
    """
    try:
        # Choose the appropriate request class based on order_type.
        if order_type == OrderType.MARKET:
            order_req = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=side,
                type=order_type,
                time_in_force=time_in_force
            )
        elif order_type == OrderType.LIMIT:
            order_req = LimitOrderRequest(
                symbol=symbol,
                qty=qty,
                side=side,
                type=order_type,
                time_in_force=time_in_force,
                limit_price=limit_price
            )
        elif order_type == OrderType.STOP:
            order_req = StopOrderRequest(
                symbol=symbol,
                qty=qty,
                side=side,
                type=order_type,
                time_in_force=time_in_force,
                stop_price=stop_price
            )
        elif order_type == OrderType.STOP_LIMIT:
            order_req = StopLimitOrderRequest(
                symbol=symbol,
                qty=qty,
                side=side,
                type=order_type,
                time_in_force=time_in_force,
                stop_price=stop_price,
                limit_price=limit_price
            )
        elif order_type == OrderType.TRAILING_STOP:
            order_req = TrailingStopOrderRequest(
                symbol=symbol,
                qty=qty,
                side=side,
                type=order_type,
                time_in_force=time_in_force,
                # For trailing stop, you can decide whether to use trail_price or trail_percent.
                trail_price=stop_price  # adjust as needed
            )
        else:
            raise HTTPException(status_code=400, detail="Unsupported order type")
        
        # Submit the order request via the client.
        order = client.create_order(order_req)
        return order
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@orders_router.get("/", summary="Get Orders")
def get_orders_route(
    status: Optional[OrderStatus] = Query(None),
    limit: int = Query(50),
    after: Optional[datetime] = Query(None),
    until: Optional[datetime] = Query(None),
    client=Depends(alpaca_client.trading_client)
):
    """
    Retrieve a list of orders with optional filtering using a GetOrdersRequest.
    """
    try:
        orders_req = GetOrdersRequest(
            status=status,
            limit=limit,
            after=after,
            until=until,
            direction=None,  # or specify 'asc'/'desc' if needed
            nested=False,
            side=None,
            symbols=None
        )
        orders = client.get_orders(orders_req)
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@orders_router.get("/{order_id}", summary="Get Order By Id")
def get_order_by_id_route(order_id: str, client=Depends(alpaca_client.trading_client)):
    """
    Retrieve order details by order ID using a GetOrderByIdRequest.
    """
    try:
        order_req = GetOrderByIdRequest(nested=False)
        order = client.get_order(order_id, order_req)
        if not order:
            raise HTTPException(status_code=204, detail="No Order Found")
        return order
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@orders_router.put("/{order_id}", summary="Replace Order By Id")
def replace_order_route(
    order_id: str,
    symbol: Optional[str] = None,
    qty: Optional[float] = None,
    side: Optional[OrderSide] = None,
    order_type: Optional[OrderType] = None,
    time_in_force: Optional[TimeInForce] = None,
    limit_price: Optional[float] = None,
    stop_price: Optional[float] = None,
    client=Depends(alpaca_client.trading_client)
):
    """
    Replace an existing order by order ID using a ReplaceOrderRequest.
    """
    try:
        replace_req = ReplaceOrderRequest(
            qty=qty,
            time_in_force=time_in_force,
            limit_price=limit_price,
            stop_price=stop_price,
            trail=None,           # if trailing stop order replacement is needed
            client_order_id=None  # add if needed
        )
        order = client.replace_order(order_id, replace_req)
        return order
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@orders_router.delete("/", summary="Cancel All Orders")
def cancel_all_orders_route(client=Depends(alpaca_client.trading_client)):
    """
    Cancel all open orders.
    """
    try:
        response = client.cancel_all_orders()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@orders_router.delete("/{order_id}", summary="Cancel Order By Id")
def cancel_order_by_id_route(order_id: str, client=Depends(alpaca_client.trading_client)):
    """
    Cancel a specific order by order ID.
    """
    try:
        response = client.cancel_order(order_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# Assets Router
# =============================================================================
assets_router = APIRouter(prefix="/assets")

@assets_router.get("/", summary="Get All Assets")
def get_assets_route(client=Depends(alpaca_client.trading_client)):
    """
    Retrieve a list of all assets using a GetAssetsRequest.
    """
    try:
        assets_req = GetAssetsRequest(
            status=None,
            asset_class=None,
            exchange=None,
            attributes=None
        )
        assets = client.get_assets(assets_req)
        return assets
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@assets_router.get("/{symbol}", summary="Get Asset")
def get_asset_route(symbol: str, client=Depends(alpaca_client.trading_client)):
    """
    Retrieve details for a specific asset by symbol.
    """
    try:
        asset = client.get_asset(symbol)
        return asset
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# Contracts Router
# =============================================================================
contracts_router = APIRouter(prefix="/contracts")

@contracts_router.get("/", summary="Get Option Contracts")
def get_option_contracts_route(client=Depends(alpaca_client.trading_client)):
    """
    Retrieve a list of option contracts.
    """
    try:
        # Assuming the contracts call is a direct client method (no request object available)
        contracts = client.get_option_contracts()
        return contracts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@contracts_router.get("/{contract_id}", summary="Get Option Contract")
def get_option_contract_route(contract_id: str, client=Depends(alpaca_client.trading_client)):
    """
    Retrieve details for a specific option contract.
    """
    try:
        contract = client.get_option_contract(contract_id)
        if not contract:
            raise HTTPException(status_code=204, detail="No Contract Found")
        return contract
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# Market Data Router
# =============================================================================
market_data_router = APIRouter(prefix="/market-data")

@market_data_router.get("/quote/{symbol}", summary="Get Latest Quote")
def get_latest_quote_route(symbol: str, client=Depends(alpaca_client.stock_client)):
    """
    Retrieve the latest quote for a given stock symbol.
    """
    try:
        quote = client.get_latest_quote(symbol)
        return quote
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@market_data_router.get("/historical-bars/{symbol}", summary="Get Historical Price Bars")
def get_historical_bars_route(
    symbol: str, 
    timeframe: str = "Day",
    start: Optional[datetime] = Query(None), 
    end: Optional[datetime] = Query(None),
    client=Depends(alpaca_client.stock_client)
):
    """
    Retrieve historical price bars for a given stock symbol.
    """
    # Convert timeframe string to enum (using TimeFrameUnit)
    timeframe_enum = TimeFrame(TimeFrameUnit[timeframe.upper()])
    
    try:
        bars = client.get_historical_bars(symbol, timeframe_enum, start, end)
        return bars
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# Include Routers in Parent Router
# =============================================================================
trading_platform_router.include_router(account_router, tags=["Trading Platform - Account"])
trading_platform_router.include_router(orders_router, tags=["Trading Platform - Orders"])
trading_platform_router.include_router(positions_router, tags=["Trading Platform - Positions"])
trading_platform_router.include_router(assets_router, tags=["Trading Platform - Assets"])
trading_platform_router.include_router(contracts_router, tags=["Trading Platform - Contracts"])
trading_platform_router.include_router(market_data_router, tags=["Trading Platform - Market Data"])
