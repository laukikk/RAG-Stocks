from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, Date, Enum, DECIMAL, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import TIMESTAMP
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Literal
from datetime import datetime, date, timezone
from enum import Enum as PyEnum
from .neon_client import Base

# ENUMs
class AccountStatus(str, PyEnum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    SUSPENDED = 'suspended'

class AccountType(str, PyEnum):
    CASH = 'cash'
    MARGIN = 'margin'
    RETIREMENT = 'retirement'
    BUSINESS = 'business'

class OrderType(str, PyEnum):
    MARKET = 'market'
    LIMIT = 'limit'
    STOP = 'stop'
    STOP_LIMIT = 'stop_limit'

class TransactionType(str, PyEnum):
    BUY = 'buy'
    SELL = 'sell'

class OrderStatus(str, PyEnum):
    PENDING = 'pending'
    EXECUTED = 'executed'
    PARTIAL = 'partial'
    CANCELED = 'canceled'
    EXPIRED = 'expired'
    REJECTED = 'rejected'

class StatementType(str, PyEnum):
    INCOME = 'income'
    BALANCE = 'balance'
    CASH_FLOW = 'cash_flow'

# SQLAlchemy ORM Models
class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    date_of_birth = Column(Date)
    phone_number = Column(String(20))
    created_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_login = Column(TIMESTAMP(timezone=True))
    account_status = Column(Enum(AccountStatus, values_callable=lambda enum: [e.value for e in enum]), default=AccountStatus.ACTIVE)
    two_factor_enabled = Column(Boolean, default=False)
    
    # Relationships
    accounts = relationship("Account", back_populates="user")
    watchlists = relationship("Watchlist", back_populates="user")

class Account(Base):
    __tablename__ = "accounts"
    
    account_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    account_type = Column(Enum(AccountType, values_callable=lambda enum: [e.value for e in enum]), nullable=False)
    account_number = Column(String(20), unique=True, nullable=False)
    currency = Column(String(3), default="USD")
    balance = Column(DECIMAL(15, 2), default=0.00)
    margin_available = Column(DECIMAL(15, 2), default=0.00)
    created_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    status = Column(Enum(AccountStatus, values_callable=lambda enum: [e.value for e in enum]), default=AccountStatus.ACTIVE)
    
    # Relationships
    user = relationship("User", back_populates="accounts")
    holdings = relationship("PortfolioHolding", back_populates="account")
    orders = relationship("Order", back_populates="account")
    transactions = relationship("Transaction", back_populates="account")

class Stock(Base):
    __tablename__ = "stocks"
    
    stock_id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, nullable=False)
    company_name = Column(String(100), nullable=False)
    exchange = Column(String(20), nullable=False)
    sector = Column(String(50))
    industry = Column(String(50))
    is_active = Column(Boolean, default=True)
    added_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_updated = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    holdings = relationship("PortfolioHolding", back_populates="stock")
    orders = relationship("Order", back_populates="stock")
    transactions = relationship("Transaction", back_populates="stock")
    financial_statements = relationship("FinancialStatement", back_populates="stock")
    dividends = relationship("Dividend", back_populates="stock")
    watchlist_items = relationship("WatchlistItem", back_populates="stock")
    daily_prices = relationship("StockDailyPrice", back_populates="stock")
    
class StockDailyPrice(Base):
    __tablename__ = "stock_daily_prices"
    
    price_id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.stock_id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    open_price = Column(DECIMAL(15, 2))
    high_price = Column(DECIMAL(15, 2))
    low_price = Column(DECIMAL(15, 2))
    close_price = Column(DECIMAL(15, 2), nullable=False)
    volume = Column(BigInteger)
    
    # Relationships
    stock = relationship("Stock", back_populates="daily_prices")

class PortfolioHolding(Base):
    __tablename__ = "portfolio_holdings"
    
    holding_id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id", ondelete="CASCADE"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.stock_id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False)
    average_purchase_price = Column(DECIMAL(15, 2), nullable=False)
    purchase_date = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_transaction_date = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    account = relationship("Account", back_populates="holdings")
    stock = relationship("Stock", back_populates="holdings")

class Order(Base):
    __tablename__ = "orders"
    
    order_id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id", ondelete="CASCADE"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.stock_id", ondelete="RESTRICT"), nullable=False)
    order_type = Column(Enum(OrderType, values_callable=lambda enum: [e.value for e in enum]), nullable=False)
    transaction_type = Column(Enum(TransactionType, values_callable=lambda enum: [e.value for e in enum]), nullable=False)
    quantity = Column(Integer, nullable=False)
    filled_quantity = Column(Integer)
    price = Column(DECIMAL(15, 2))
    stop_price = Column(DECIMAL(15, 2))
    status = Column(Enum(OrderStatus, values_callable=lambda enum: [e.value for e in enum]), nullable=False, default=OrderStatus.PENDING)
    placed_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    executed_at = Column(TIMESTAMP(timezone=True))
    expires_at = Column(TIMESTAMP(timezone=True))
    notes = Column(Text)
    
    # Relationships
    account = relationship("Account", back_populates="orders")
    stock = relationship("Stock", back_populates="orders")
    transactions = relationship("Transaction", back_populates="order")

class Transaction(Base):
    __tablename__ = "transactions"
    
    transaction_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id", ondelete="SET NULL"))
    account_id = Column(Integer, ForeignKey("accounts.account_id", ondelete="CASCADE"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.stock_id", ondelete="RESTRICT"), nullable=False)
    transaction_type = Column(Enum(TransactionType, values_callable=lambda enum: [e.value for e in enum]), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(DECIMAL(15, 2), nullable=False)
    commission = Column(DECIMAL(10, 2), default=0.00)
    total_amount = Column(DECIMAL(15, 2), nullable=False)
    transaction_date = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    order = relationship("Order", back_populates="transactions")
    account = relationship("Account", back_populates="transactions")
    stock = relationship("Stock", back_populates="transactions")

class Watchlist(Base):
    __tablename__ = "watchlists"
    
    watchlist_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    name = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_modified = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="watchlists")
    watchlist_items = relationship("WatchlistItem", back_populates="watchlist")

class WatchlistItem(Base):
    __tablename__ = "watchlist_items"
    
    watchlist_item_id = Column(Integer, primary_key=True, index=True)
    watchlist_id = Column(Integer, ForeignKey("watchlists.watchlist_id", ondelete="CASCADE"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.stock_id", ondelete="CASCADE"), nullable=False)
    added_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    watchlist = relationship("Watchlist", back_populates="watchlist_items")
    stock = relationship("Stock", back_populates="watchlist_items")

class FinancialStatement(Base):
    __tablename__ = "financial_statements"
    
    statement_id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.stock_id", ondelete="CASCADE"), nullable=False)
    statement_type = Column(Enum(StatementType, values_callable=lambda enum: [e.value for e in enum]), nullable=False)
    fiscal_year = Column(Integer, nullable=False)
    fiscal_quarter = Column(Integer)
    revenue = Column(DECIMAL(20, 2))
    gross_profit = Column(DECIMAL(20, 2))
    operating_income = Column(DECIMAL(20, 2))
    net_income = Column(DECIMAL(20, 2))
    eps = Column(DECIMAL(10, 2))
    total_assets = Column(DECIMAL(20, 2))
    total_liabilities = Column(DECIMAL(20, 2))
    total_equity = Column(DECIMAL(20, 2))
    operating_cash_flow = Column(DECIMAL(20, 2))
    investing_cash_flow = Column(DECIMAL(20, 2))
    financing_cash_flow = Column(DECIMAL(20, 2))
    report_date = Column(Date, nullable=False)
    
    # Relationships
    stock = relationship("Stock", back_populates="financial_statements")

class Dividend(Base):
    __tablename__ = "dividends"
    
    dividend_id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.stock_id", ondelete="CASCADE"), nullable=False)
    ex_date = Column(Date, nullable=False)
    payment_date = Column(Date)
    amount_per_share = Column(DECIMAL(10, 4), nullable=False)
    
    # Relationships
    stock = relationship("Stock", back_populates="dividends")

# Pydantic Models for API requests/responses
class UserBase(BaseModel):
    username: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None

class UserCreate(UserBase):
    password: str
    date_of_birth: Optional[date] = None

class UserResponse(UserBase):
    user_id: int
    date_of_birth: Optional[date] = None
    created_at: datetime
    account_status: str
    
    class Config:
        from_attributes = True

class AccountBase(BaseModel):
    account_type: AccountType
    account_number: str
    currency: str = "USD"

class AccountCreate(AccountBase):
    pass

class AccountResponse(AccountBase):
    account_id: int
    user_id: int
    balance: float
    margin_available: float
    created_at: datetime
    status: str
    
    class Config:
        from_attributes = True

class StockBase(BaseModel):
    symbol: str
    company_name: str
    exchange: str
    sector: Optional[str] = None
    industry: Optional[str] = None

class StockCreate(StockBase):
    pass

class StockResponse(StockBase):
    stock_id: int
    is_active: bool
    added_at: datetime
    last_updated: datetime
    
    class Config:
        from_attributes = True

class StockDailyPriceBase(BaseModel):
    stock_id: int
    date: date
    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    close_price: float
    volume: Optional[int] = None

class StockDailyPriceCreate(StockDailyPriceBase):
    pass

class StockDailyPriceResponse(StockDailyPriceBase):
    price_id: int
    
    class Config:
        from_attributes = True

class PortfolioHoldingBase(BaseModel):
    account_id: int
    stock_id: int
    quantity: int
    average_purchase_price: float

class PortfolioHoldingCreate(PortfolioHoldingBase):
    pass

class PortfolioHoldingResponse(PortfolioHoldingBase):
    holding_id: int
    purchase_date: datetime
    last_transaction_date: datetime
    stock: StockResponse
    
    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    account_id: int
    stock_id: int
    order_type: OrderType
    transaction_type: TransactionType
    quantity: int
    price: Optional[float] = None
    stop_price: Optional[float] = None
    notes: Optional[str] = None

class OrderCreate(OrderBase):
    pass

class OrderResponse(OrderBase):
    order_id: int
    filled_quantity: Optional[int] = None
    status: OrderStatus
    placed_at: datetime
    executed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    stock: StockResponse
    
    class Config:
        from_attributes = True

class TransactionBase(BaseModel):
    account_id: int
    stock_id: int
    transaction_type: TransactionType
    quantity: int
    price: float
    commission: float = 0.0

class TransactionCreate(TransactionBase):
    order_id: Optional[int] = None
    total_amount: float

class TransactionResponse(TransactionBase):
    transaction_id: int
    order_id: Optional[int] = None
    total_amount: float
    transaction_date: datetime
    stock: StockResponse
    
    class Config:
        from_attributes = True

class WatchlistBase(BaseModel):
    name: str

class WatchlistCreate(WatchlistBase):
    pass

class WatchlistItemBase(BaseModel):
    stock_id: int

class WatchlistItemCreate(WatchlistItemBase):
    pass

class WatchlistItemResponse(BaseModel):
    watchlist_item_id: int
    added_at: datetime
    stock: StockResponse
    
    class Config:
        from_attributes = True

class WatchlistResponse(WatchlistBase):
    watchlist_id: int
    user_id: int
    created_at: datetime
    last_modified: datetime
    items: List[WatchlistItemResponse] = []
    
    class Config:
        from_attributes = True

class UserWatchlistsResponse(BaseModel):
    watchlists: List[WatchlistResponse]