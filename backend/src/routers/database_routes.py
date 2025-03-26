from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import date, timedelta

# Custom imports
from database.calls import (
    create_user, get_user_by_email, get_user_portfolio_summary,
    create_account, create_stock, record_stock_daily_price,
    get_stock_price_history, get_stock_performance,
    add_portfolio_holding, create_order, record_transaction,
    create_watchlist, add_watchlist_item
)
from database.neon_client import NeonClient
from utils.security import hash_password

neon_client = NeonClient()

# Parent router
database_router = APIRouter(prefix="/database")

# =============================================================================
# Users Router
# =============================================================================
users_router = APIRouter(prefix="/users")

@users_router.post("/create", summary="Create a new user")
def create_user_route(username: str, email: str, password: str, 
                first_name: str = None, last_name: str = None, 
                date_of_birth: date = None, phone_number: str = None, 
                db: Session = Depends(neon_client.get_db_session)):
    """
    Create a new user in the database.
    """
    try:
        password_hash = hash_password(password)
        new_user = create_user(
            db, username, email, password_hash, first_name, last_name, date_of_birth, phone_number
        )
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
def create_account_route(user_id: int, account_type: str, currency: str = 'USD', db: Session = Depends(neon_client.get_db_session)):
    """
    Create a new account for a user.
    """
    try:
        account = create_account(db, user_id, account_type, currency)
        return account
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Stocks Router
# =============================================================================
stocks_router = APIRouter(prefix="/stocks")

@stocks_router.post("/create", summary="Create a new stock entry")
def create_stock_route(symbol: str, company_name: str, exchange: str, 
                 sector: str = None, industry: str = None, 
                 db: Session = Depends(neon_client.get_db_session)):
    """
    Create a new stock record in the database.
    """
    try:
        stock = create_stock(db, symbol, company_name, exchange, sector, industry)
        return stock
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@stocks_router.post("/{stock_id}/daily_price", summary="Record stock daily price")
def record_stock_daily_price_route(stock_id: int, date: date, close_price: float, 
                             open_price: float = None, high_price: float = None, 
                             low_price: float = None, volume: int = None,
                             db: Session = Depends(neon_client.get_db_session)):
    """
    Record the daily price for a stock.
    """
    try:
        daily_price = record_stock_daily_price(
            db, stock_id, date, close_price, open_price, high_price, low_price, volume
        )
        return daily_price
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@stocks_router.get("/{stock_id}/price_history", summary="Get stock price history")
def get_stock_price_history_route(stock_id: int, start_date: date = None, end_date: date = None, 
                            db: Session = Depends(neon_client.get_db_session)):
    """
    Retrieve the historical price data for a given stock.
    """
    history = get_stock_price_history(db, stock_id, start_date, end_date)
    if history:
        return history
    raise HTTPException(status_code=404, detail="Price history not found")


@stocks_router.get("/{stock_id}/performance", summary="Get stock performance")
def get_stock_performance_route(stock_id: int, days: int = 30, 
                          db: Session = Depends(neon_client.get_db_session)):
    """
    Get performance metrics for a stock over a specified number of days.
    """
    performance = get_stock_performance(db, stock_id, days)
    if performance:
        return performance
    raise HTTPException(status_code=404, detail="Performance data not found")


# =============================================================================
# Portfolio Router
# =============================================================================
portfolio_router = APIRouter(prefix="/portfolio")

@portfolio_router.post("/holding/add", summary="Add portfolio holding")
def add_portfolio_holding_route(account_id: int, stock_id: int, quantity: int, average_price: float, 
                          db: Session = Depends(neon_client.get_db_session)):
    """
    Add a stock holding to a user's portfolio.
    """
    try:
        holding = add_portfolio_holding(db, account_id, stock_id, quantity, average_price)
        return holding
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Orders Router
# =============================================================================
orders_router = APIRouter(prefix="/orders")

@orders_router.post("/create", summary="Create a new order")
def create_order_route(account_id: int, stock_id: int, order_type: str, transaction_type: str, 
                 quantity: int, price: float = None, stop_price: float = None, 
                 db: Session = Depends(neon_client.get_db_session)):
    """
    Create a new order for buying or selling a stock.
    """
    try:
        order = create_order(
            db, account_id, stock_id, order_type, transaction_type, quantity, price, stop_price
        )
        return order
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Transactions Router
# =============================================================================
transactions_router = APIRouter(prefix="/transactions")

@transactions_router.post("/record", summary="Record a transaction")
def record_transaction_route(account_id: int, stock_id: int, transaction_type: str, 
                       quantity: int, price: float, order_id: int = None, commission: float = 0.0, 
                       db: Session = Depends(neon_client.get_db_session)):
    """
    Record a new transaction in the system.
    """
    try:
        transaction = record_transaction(
            db, account_id, stock_id, transaction_type, quantity, price, order_id, commission
        )
        return transaction
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Watchlists Router
# =============================================================================
watchlists_router = APIRouter(prefix="/watchlists")

@watchlists_router.post("/create", summary="Create a new watchlist")
def create_watchlist_route(user_id: int, name: str, db: Session = Depends(neon_client.get_db_session)):
    """
    Create a new watchlist for a user.
    """
    try:
        watchlist = create_watchlist(db, user_id, name)
        return watchlist
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@watchlists_router.post("/item/add", summary="Add an item to a watchlist")
def add_watchlist_item_route(watchlist_id: int, stock_id: int, db: Session = Depends(neon_client.get_db_session)):
    """
    Add a stock to an existing watchlist.
    """
    try:
        item = add_watchlist_item(db, watchlist_id, stock_id)
        return item
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# add routers to parent router
database_router.include_router(users_router, tags=["Database - Users"])
database_router.include_router(accounts_router, tags=["Database - Accounts"])
database_router.include_router(stocks_router, tags=["Database - Stocks"])
database_router.include_router(portfolio_router, tags=["Database - Portfolio"])
database_router.include_router(orders_router, tags=["Database - Orders"])
database_router.include_router(transactions_router, tags=["Database - Transactions"])
database_router.include_router(watchlists_router, tags=["Database - Watchlists"])