from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

# Custom imports
from database.calls import (
    create_user, get_user_by_email, get_user_portfolio_summary,
    create_account, create_asset, record_asset_daily_price,
    get_asset_price_history, get_asset_performance,
    add_portfolio_holding, get_portfolio_holdings,
    create_order, update_order, record_transaction,
    get_orders_by_status, get_active_orders, get_orders_by_date_range,
    create_watchlist, add_watchlist_item,
    create_daily_portfolio_snapshot, create_intraday_portfolio_snapshot,
    get_account_type_by_code, get_all_account_types,
    get_order_type_by_code, get_all_order_types,
    get_order_status_by_code, get_all_order_statuses
)
from database.models import (
    AssetBase, AssetCreate, AccountCreate, 
    OrderCreate, OrderUpdate, TransactionCreate, PortfolioHoldingCreate,
    WatchlistCreate, WatchlistItemCreate, AssetDailyPriceCreate,
    UserCreate, OrderStatus, TransactionType
)
from database.neon_client import NeonClient
from utils.security import hash_password

neon_client = NeonClient()

# Parent router
database_router = APIRouter(prefix="/database")

# =============================================================================
# Lookup Tables Routers
# =============================================================================
lookup_router = APIRouter(prefix="/lookup")

@lookup_router.get("/account-types", summary="Get all account types")
def get_account_types_route(db: Session = Depends(neon_client.get_db_session)):
    """
    Retrieve all available account types.
    """
    try:
        account_types = get_all_account_types(db)
        return account_types
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@lookup_router.get("/order-types", summary="Get all order types")
def get_order_types_route(db: Session = Depends(neon_client.get_db_session)):
    """
    Retrieve all available order types.
    """
    try:
        order_types = get_all_order_types(db)
        return order_types
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@lookup_router.get("/order-statuses", summary="Get all order statuses")
def get_order_statuses_route(db: Session = Depends(neon_client.get_db_session)):
    """
    Retrieve all available order statuses.
    """
    try:
        order_statuses = get_all_order_statuses(db)
        return order_statuses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Users Router
# =============================================================================
users_router = APIRouter(prefix="/users")

@users_router.post("/create", summary="Create a new user")
def create_user_route(
    username: str, 
    email: str, 
    password: str, 
    first_name: Optional[str] = None, 
    last_name: Optional[str] = None, 
    date_of_birth: Optional[date] = None, 
    phone_number: Optional[str] = None, 
    db: Session = Depends(neon_client.get_db_session)
):
    """
    Create a new user in the database.
    """
    try:
        # Create Pydantic model from parameters
        user_data = UserCreate(
            username=username,
            email=email,
            password=hash_password(password),
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            phone_number=phone_number
        )
        
        # Pass to database function
        new_user = create_user(db, user_data)
        return new_user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@users_router.get("/by_email", summary="Get user by email")
def get_user_by_email_route(email: str, db: Session = Depends(neon_client.get_db_session)):
    """
    Retrieve a user using their email address.
    """
    user = get_user_by_email(db, email)
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")


@users_router.get("/{user_id}/portfolio", summary="Get user portfolio summary")
def get_user_portfolio_summary_route(user_id: int, db: Session = Depends(neon_client.get_db_session)):
    """
    Get a detailed summary of a user's portfolio across all accounts.
    """
    portfolio = get_user_portfolio_summary(db, user_id)
    if portfolio:
        return portfolio
    raise HTTPException(status_code=404, detail="Portfolio summary not found")


# =============================================================================
# Accounts Router
# =============================================================================
accounts_router = APIRouter(prefix="/accounts")

@accounts_router.post("/create", summary="Create a new account")
def create_account_route(
    user_id: int, 
    account_type: str,  # Accept account type code string (e.g., "cash", "margin")
    currency: str = "USD", 
    db: Session = Depends(neon_client.get_db_session)
):
    """
    Create a new account for a user.
    
    Parameters:
    - user_id: ID of the user who owns this account
    - account_type: Type of account (e.g., "cash", "margin", "retirement", "business")
    - currency: Three-letter currency code (default: "USD")
    """
    try:
        # First, get the account type ID from the code
        account_type_obj = get_account_type_by_code(db, account_type)
        if not account_type_obj:
            raise HTTPException(status_code=404, detail=f"Account type '{account_type}' not found")
            
        # The account number would be generated in the database function
        account_data = AccountCreate(
            account_type_id=account_type_obj.id,
            currency=currency
        )
        
        # Pass to database function with user_id
        account = create_account(db, account_data, user_id)
        return account
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Assets Router
# =============================================================================
assets_router = APIRouter(prefix="/assets")

@assets_router.post("/create", summary="Create a new asset entry")
def create_asset_route(
    symbol: str, 
    company_name: str, 
    exchange: str, 
    sector: Optional[str] = None, 
    industry: Optional[str] = None, 
    db: Session = Depends(neon_client.get_db_session)
):
    """
    Create a new asset record in the database.
    """
    try:
        # Create Pydantic model from parameters
        asset_data = AssetCreate(
            symbol=symbol,
            company_name=company_name,
            exchange=exchange,
            sector=sector,
            industry=industry
        )
        
        # Pass to database function
        asset = create_asset(db, asset_data)
        return asset
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@assets_router.post("/{asset_id}/daily_price", summary="Record asset daily price")
def record_asset_daily_price_route(
    asset_id: int, 
    date: date, 
    close_price: float, 
    open_price: Optional[float] = None, 
    high_price: Optional[float] = None, 
    low_price: Optional[float] = None, 
    volume: Optional[int] = None,
    db: Session = Depends(neon_client.get_db_session)
):
    """
    Record the daily price for an asset.
    """
    try:
        # Create Pydantic model from parameters
        price_data = AssetDailyPriceCreate(
            asset_id=asset_id,
            date=date,
            close_price=close_price,
            open_price=open_price,
            high_price=high_price,
            low_price=low_price,
            volume=volume
        )
        
        # Pass to database function
        daily_price = record_asset_daily_price(db, price_data)
        return daily_price
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@assets_router.get("/{asset_id}/price_history", summary="Get asset price history")
def get_asset_price_history_route(
    asset_id: int, 
    start_date: Optional[date] = None, 
    end_date: Optional[date] = None, 
    db: Session = Depends(neon_client.get_db_session)
):
    """
    Retrieve the historical price data for a given asset.
    """
    history = get_asset_price_history(db, asset_id, start_date, end_date)
    if history:
        return history
    raise HTTPException(status_code=404, detail="Price history not found")


@assets_router.get("/{asset_id}/performance", summary="Get asset performance")
def get_asset_performance_route(
    asset_id: int, 
    days: int = 30, 
    db: Session = Depends(neon_client.get_db_session)
):
    """
    Get performance metrics for an asset over a specified number of days.
    """
    performance = get_asset_performance(db, asset_id, days)
    if performance:
        return performance
    raise HTTPException(status_code=404, detail="Performance data not found")


# =============================================================================
# Portfolio Router
# =============================================================================
portfolio_router = APIRouter(prefix="/portfolio")

@portfolio_router.post("/holding/add", summary="Add portfolio holding")
def add_portfolio_holding_route(
    account_id: int, 
    asset_id: int, 
    quantity: int, 
    average_purchase_price: float, 
    db: Session = Depends(neon_client.get_db_session)
):
    """
    Add an asset holding to a user's portfolio.
    """
    try:
        # Create Pydantic model from parameters
        holding_data = PortfolioHoldingCreate(
            account_id=account_id,
            asset_id=asset_id,
            quantity=quantity,
            average_purchase_price=average_purchase_price
        )
        
        # Pass to database function
        holding = add_portfolio_holding(db, holding_data)
        return holding
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@portfolio_router.get("/{account_id}/holdings", summary="Get portfolio holdings")
def get_portfolio_holdings_route(account_id: int, db: Session = Depends(neon_client.get_db_session)):
    """
    Retrieve all asset holdings for a given account.
    """
    holdings = get_portfolio_holdings(db, account_id)
    if holdings:
        return holdings
    raise HTTPException(status_code=404, detail="Holdings not found")


@portfolio_router.post("/{account_id}/daily_snapshot", summary="Create daily portfolio snapshot")
def create_daily_portfolio_snapshot_route(
    account_id: int, 
    snapshot_date: date,
    portfolio_value: float, 
    cash_balance: Optional[float] = None,
    unrealized_pnl: Optional[float] = None, 
    unrealized_pnl_percent: Optional[float] = None,
    db: Session = Depends(neon_client.get_db_session)
):
    """
    Create a daily snapshot of a portfolio's value and performance.
    """
    try:
        snapshot = create_daily_portfolio_snapshot(
            db, account_id, snapshot_date, portfolio_value, 
            cash_balance, unrealized_pnl, unrealized_pnl_percent
        )
        return snapshot
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@portfolio_router.post("/{account_id}/intraday_snapshot", summary="Create intraday portfolio snapshot")
def create_intraday_portfolio_snapshot_route(
    account_id: int,
    portfolio_value: float,
    db: Session = Depends(neon_client.get_db_session)
):
    """
    Create an intraday snapshot of a portfolio's current value.
    """
    try:
        snapshot = create_intraday_portfolio_snapshot(db, account_id, portfolio_value)
        return snapshot
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Orders Router
# =============================================================================
orders_router = APIRouter(prefix="/orders")

@orders_router.post("/create", summary="Create a new order")
def create_order_route(
    account_id: int, 
    asset_id: int, 
    order_type_id: int, 
    transaction_type: TransactionType, 
    quantity: int, 
    price: Optional[float] = None, 
    stop_price: Optional[float] = None, 
    notes: Optional[str] = None,
    db: Session = Depends(neon_client.get_db_session)
):
    """
    Create a new order for buying or selling an asset.
    """
    try:
        # Create Pydantic model from parameters
        order_data = OrderCreate(
            account_id=account_id,
            asset_id=asset_id,
            order_type_id=order_type_id,
            transaction_type=transaction_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
            notes=notes
        )
        
        # Pass to database function
        order = create_order(db, order_data)
        return order
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@orders_router.put("/{order_id}/update", summary="Update an existing order")
def update_order_route(
    order_id: int, 
    status: Optional[OrderStatus] = None, 
    filled_quantity: Optional[int] = None, 
    price: Optional[float] = None, 
    stop_price: Optional[float] = None, 
    notes: Optional[str] = None,
    db: Session = Depends(neon_client.get_db_session)
):
    """
    Update an existing order's details.
    """
    try:
        # Create Pydantic model from parameters
        order_data = OrderUpdate(
            status=status,
            filled_quantity=filled_quantity,
            price=price,
            stop_price=stop_price,
            notes=notes
        )
        
        # Pass to database function
        updated_order = update_order(db, order_id, order_data)
        return updated_order
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@orders_router.get("/{account_id}", summary="Get orders for an account")
def get_orders_route(
    account_id: int, 
    status: Optional[str] = OrderStatus.ALL, 
    db: Session = Depends(neon_client.get_db_session)
):
    """
    Get all orders for an account, optionally filtered by status.
    """
    try:
        orders = get_orders_by_status(db, account_id, status)
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@orders_router.get("/{account_id}/range", summary="Get orders by date range")
def get_orders_by_date_range_route(
    account_id: int, 
    start_date: date, 
    end_date: date, 
    db: Session = Depends(neon_client.get_db_session)
):
    """
    Get all orders for an account within a specific date range.
    """
    try:
        orders = get_orders_by_date_range(db, account_id, start_date, end_date)
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@orders_router.get("/{account_id}/active", summary="Get active orders")
def get_active_orders_route(account_id: int, db: Session = Depends(neon_client.get_db_session)):
    """
    Get all currently active/open orders for an account.
    """
    try:
        orders = get_active_orders(db, account_id)
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Transactions Router
# =============================================================================
transactions_router = APIRouter(prefix="/transactions")

@transactions_router.post("/record", summary="Record a transaction")
def record_transaction_route(
    account_id: int, 
    asset_id: int, 
    transaction_type: TransactionType, 
    quantity: int, 
    price: float, 
    order_id: Optional[int] = None, 
    commission: float = 0.0, 
    total_amount: Optional[float] = None,
    db: Session = Depends(neon_client.get_db_session)
):
    """
    Record a new transaction in the system.
    """
    try:
        # Calculate total_amount if not provided
        if total_amount is None:
            total_amount = quantity * price + commission
            
        # Create Pydantic model from parameters
        transaction_data = TransactionCreate(
            account_id=account_id,
            asset_id=asset_id,
            transaction_type=transaction_type,
            quantity=quantity,
            price=price,
            order_id=order_id,
            commission=commission,
            total_amount=total_amount
        )
        
        # Pass to database function
        transaction = record_transaction(db, transaction_data)
        return transaction
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Watchlists Router
# =============================================================================
watchlists_router = APIRouter(prefix="/watchlists")

@watchlists_router.post("/create", summary="Create a new watchlist")
def create_watchlist_route(
    user_id: int, 
    name: str, 
    db: Session = Depends(neon_client.get_db_session)
):
    """
    Create a new watchlist for a user.
    """
    try:
        # Create Pydantic model from parameters
        watchlist_data = WatchlistCreate(name=name)
        
        # Pass to database function with user_id
        watchlist = create_watchlist(db, watchlist_data, user_id)
        return watchlist
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@watchlists_router.post("/{watchlist_id}/item/add", summary="Add an item to a watchlist")
def add_watchlist_item_route(
    watchlist_id: int, 
    asset_id: int, 
    db: Session = Depends(neon_client.get_db_session)
):
    """
    Add an asset to an existing watchlist.
    """
    try:
        # Create Pydantic model from parameters
        item_data = WatchlistItemCreate(asset_id=asset_id)
        
        # Pass to database function with watchlist_id
        item = add_watchlist_item(db, item_data, watchlist_id)
        return item
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# add routers to parent router
database_router.include_router(lookup_router, tags=["Database - Lookups"])
database_router.include_router(users_router, tags=["Database - Users"])
database_router.include_router(accounts_router, tags=["Database - Accounts"])
database_router.include_router(assets_router, tags=["Database - Assets"])
database_router.include_router(portfolio_router, tags=["Database - Portfolio"])
database_router.include_router(orders_router, tags=["Database - Orders"])
database_router.include_router(transactions_router, tags=["Database - Transactions"])
database_router.include_router(watchlists_router, tags=["Database - Watchlists"])