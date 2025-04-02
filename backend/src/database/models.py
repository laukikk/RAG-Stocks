from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, Date, Enum, DECIMAL, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import TIMESTAMP
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Literal
from datetime import datetime, date, timezone
from enum import Enum as PyEnum
from .neon_client import Base

# ENUMs that remain as enum types
class AccountStatus(str, PyEnum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    SUSPENDED = 'suspended'

class TransactionType(str, PyEnum):
    BUY = 'buy'
    SELL = 'sell'

class StatementType(str, PyEnum):
    INCOME = 'income'
    BALANCE = 'balance'
    CASH_FLOW = 'cash_flow'

# Custom OrderStatus enum as specified
class OrderStatus(str, PyEnum):
    OPEN = 'open'
    CLOSED = 'closed'
    ALL = 'all'
    NEW = 'new'
    ACCEPTED = 'accepted'
    FILLED = 'filled'
    EXPIRED = 'expired'
    CANCELED = 'canceled'
    REPLACED = 'replaced'

# SQLAlchemy Models for Lookup Tables
class AccountType(Base):
    __tablename__ = "account_types"
    
    id = Column(Integer, primary_key=True, index=True)
    type_code = Column(String(20), unique=True, nullable=False)
    description = Column(Text)
    min_balance = Column(DECIMAL(15, 2), default=0.00)
    margin_allowed = Column(Boolean, default=False)
    interest_rate = Column(DECIMAL(5, 2))
    created_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    accounts = relationship("Account", back_populates="account_type")

class OrderType(Base):
    __tablename__ = "order_types"
    
    id = Column(Integer, primary_key=True, index=True)
    type_code = Column(String(20), unique=True, nullable=False)
    description = Column(Text)
    requires_price = Column(Boolean, default=False)
    requires_stop_price = Column(Boolean, default=False)
    available_hours = Column(String(20), default='market')
    created_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    orders = relationship("Order", back_populates="order_type")

class OrderStatusLookup(Base):
    __tablename__ = "order_statuses"
    
    id = Column(Integer, primary_key=True, index=True)
    status_code = Column(String(20), unique=True, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    requires_action = Column(Boolean, default=False)
    display_order = Column(Integer)
    created_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    orders = relationship("Order", back_populates="order_status")

# Main application models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
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
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    account_type_id = Column(Integer, ForeignKey("account_types.id"), nullable=False)
    account_number = Column(String(20), unique=True, nullable=False)
    currency = Column(String(3), default="USD")
    balance = Column(DECIMAL(15, 2), default=0.00)
    margin_available = Column(DECIMAL(15, 2), default=0.00)
    created_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    status = Column(Enum(AccountStatus, values_callable=lambda enum: [e.value for e in enum]), default=AccountStatus.ACTIVE)
    
    # Relationships
    user = relationship("User", back_populates="accounts")
    account_type = relationship("AccountType", back_populates="accounts")
    holdings = relationship("PortfolioHolding", back_populates="account")
    orders = relationship("Order", back_populates="account")
    transactions = relationship("Transaction", back_populates="account")
    daily_snapshots = relationship("DailyPortfolioSnapshot", back_populates="account")
    intraday_snapshots = relationship("IntradayPortfolioSnapshot", back_populates="account")

class Asset(Base):
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, nullable=False)
    company_name = Column(String(100), nullable=False)
    exchange = Column(String(20), nullable=False)
    sector = Column(String(50))
    industry = Column(String(50))
    is_active = Column(Boolean, default=True)
    added_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    holdings = relationship("PortfolioHolding", back_populates="asset")
    orders = relationship("Order", back_populates="asset")
    transactions = relationship("Transaction", back_populates="asset")
    financial_statements = relationship("FinancialStatement", back_populates="asset")
    dividends = relationship("Dividend", back_populates="asset")
    watchlist_items = relationship("WatchlistItem", back_populates="asset")
    daily_prices = relationship("AssetDailyPrice", back_populates="asset")
    
class AssetDailyPrice(Base):
    __tablename__ = "asset_daily_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    open_price = Column(DECIMAL(15, 2))
    high_price = Column(DECIMAL(15, 2))
    low_price = Column(DECIMAL(15, 2))
    close_price = Column(DECIMAL(15, 2), nullable=False)
    volume = Column(BigInteger)
    
    # Relationships
    asset = relationship("Asset", back_populates="daily_prices")

class PortfolioHolding(Base):
    __tablename__ = "portfolio_holdings"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False)
    average_purchase_price = Column(DECIMAL(15, 2), nullable=False)
    
    # Relationships
    account = relationship("Account", back_populates="holdings")
    asset = relationship("Asset", back_populates="holdings")

class DailyPortfolioSnapshot(Base):
    __tablename__ = "daily_portfolio_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    snapshot_date = Column(Date, nullable=False)
    portfolio_value = Column(DECIMAL(15, 2), nullable=False)
    cash_balance = Column(DECIMAL(15, 2))
    unrealized_intraday_pnl = Column(DECIMAL(15, 2))
    unrealized_intraday_pnl_percent = Column(DECIMAL(10, 2))
    
    # Relationships
    account = relationship("Account", back_populates="daily_snapshots")

class IntradayPortfolioSnapshot(Base):
    __tablename__ = "intraday_portfolio_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    record_timestamp = Column(TIMESTAMP(timezone=True), nullable=False)
    portfolio_value = Column(DECIMAL(15, 2), nullable=False)
    
    # Relationships
    account = relationship("Account", back_populates="intraday_snapshots")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id", ondelete="RESTRICT"), nullable=False)
    order_type_id = Column(Integer, ForeignKey("order_types.id"), nullable=False)
    transaction_type = Column(Enum(TransactionType, values_callable=lambda enum: [e.value for e in enum]), nullable=False)
    quantity = Column(Integer, nullable=False)
    filled_quantity = Column(Integer)
    price = Column(DECIMAL(15, 2))
    stop_price = Column(DECIMAL(15, 2))
    order_status_id = Column(Integer, ForeignKey("order_statuses.id"), nullable=False, default=2)  # Default to 'new' (id=2)
    placed_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    executed_at = Column(TIMESTAMP(timezone=True))
    expires_at = Column(TIMESTAMP(timezone=True))
    notes = Column(Text)
    
    # Relationships
    account = relationship("Account", back_populates="orders")
    asset = relationship("Asset", back_populates="orders")
    order_type = relationship("OrderType", back_populates="orders")
    order_status = relationship("OrderStatusLookup", back_populates="orders")
    transactions = relationship("Transaction", back_populates="order")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="SET NULL"))
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id", ondelete="RESTRICT"), nullable=False)
    transaction_type = Column(Enum(TransactionType, values_callable=lambda enum: [e.value for e in enum]), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(DECIMAL(15, 2), nullable=False)
    commission = Column(DECIMAL(10, 2), default=0.00)
    total_amount = Column(DECIMAL(15, 2), nullable=False)
    transaction_date = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    order = relationship("Order", back_populates="transactions")
    account = relationship("Account", back_populates="transactions")
    asset = relationship("Asset", back_populates="transactions")

class Watchlist(Base):
    __tablename__ = "watchlists"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="watchlists")
    watchlist_items = relationship("WatchlistItem", back_populates="watchlist")

class WatchlistItem(Base):
    __tablename__ = "watchlist_items"
    
    id = Column(Integer, primary_key=True, index=True)
    watchlist_id = Column(Integer, ForeignKey("watchlists.id", ondelete="CASCADE"), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    added_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    watchlist = relationship("Watchlist", back_populates="watchlist_items")
    asset = relationship("Asset", back_populates="watchlist_items")

class FinancialStatement(Base):
    __tablename__ = "financial_statements"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    statement_type = Column(Enum(StatementType, values_callable=lambda enum: [e.value for e in enum]), nullable=False)
    fiscal_year = Column(Integer, nullable=False)
    fiscal_quarter = Column(Integer, nullable=True)
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
    asset = relationship("Asset", back_populates="financial_statements")

class Dividend(Base):
    __tablename__ = "dividends"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    ex_date = Column(Date, nullable=False)
    payment_date = Column(Date)
    amount_per_share = Column(DECIMAL(10, 4), nullable=False)
    
    # Relationships
    asset = relationship("Asset", back_populates="dividends")

# Pydantic Models for API requests/responses
class AccountTypeBase(BaseModel):
    type_code: str
    description: Optional[str] = None
    min_balance: float = 0.0
    margin_allowed: bool = False
    interest_rate: Optional[float] = None

class AccountTypeCreate(AccountTypeBase):
    pass

class AccountTypeResponse(AccountTypeBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class OrderTypeBase(BaseModel):
    type_code: str
    description: Optional[str] = None
    requires_price: bool = False
    requires_stop_price: bool = False
    available_hours: str = 'market'

class OrderTypeCreate(OrderTypeBase):
    pass

class OrderTypeResponse(OrderTypeBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class OrderStatusBase(BaseModel):
    status_code: str
    description: Optional[str] = None
    is_active: bool = True
    requires_action: bool = False
    display_order: Optional[int] = None

class OrderStatusCreate(OrderStatusBase):
    pass

class OrderStatusResponse(OrderStatusBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

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
    id: int
    date_of_birth: Optional[date] = None
    created_at: datetime
    account_status: str
    
    class Config:
        from_attributes = True

class AccountBase(BaseModel):
    account_type_id: int
    account_number: Optional[str] = None
    currency: str = "USD"

class AccountCreate(AccountBase):
    pass

class AccountResponse(AccountBase):
    id: int
    user_id: int
    balance: float
    margin_available: float
    created_at: datetime
    status: str
    account_type: AccountTypeResponse
    
    class Config:
        from_attributes = True

class AssetBase(BaseModel):
    symbol: str
    company_name: str
    exchange: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    
    def to_asset(self) -> Asset:
        return Asset(
            symbol=self.symbol,
            company_name=self.company_name,
            exchange=self.exchange,
            sector=self.sector,
            industry=self.industry
        )

class AssetCreate(AssetBase):
    pass

class AssetResponse(AssetBase):
    id: int
    is_active: bool
    added_at: datetime
    
    class Config:
        from_attributes = True

class AssetDailyPriceBase(BaseModel):
    asset_id: int
    date: date
    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    close_price: float
    volume: Optional[int] = None

class AssetDailyPriceCreate(AssetDailyPriceBase):
    pass

class AssetDailyPriceResponse(AssetDailyPriceBase):
    id: int
    
    class Config:
        from_attributes = True

class PortfolioHoldingBase(BaseModel):
    account_id: int
    asset_id: int
    quantity: int
    average_purchase_price: float

class PortfolioHoldingCreate(PortfolioHoldingBase):
    pass

class PortfolioHoldingResponse(PortfolioHoldingBase):
    id: int
    asset: AssetResponse
    
    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    account_id: int
    asset_id: int
    order_type_id: int
    transaction_type: TransactionType
    quantity: int
    price: Optional[float] = None
    stop_price: Optional[float] = None
    notes: Optional[str] = None

class OrderCreate(OrderBase):
    pass

class OrderResponse(OrderBase):
    id: int
    filled_quantity: Optional[int] = None
    order_status_id: int
    placed_at: datetime
    executed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    asset: AssetResponse
    order_type: OrderTypeResponse
    order_status: OrderStatusResponse
    
    class Config:
        from_attributes = True

class TransactionBase(BaseModel):
    account_id: int
    asset_id: int
    transaction_type: TransactionType
    quantity: int
    price: float
    commission: float = 0.0

class TransactionCreate(TransactionBase):
    order_id: Optional[int] = None
    total_amount: float

class TransactionResponse(TransactionBase):
    id: int
    order_id: Optional[int] = None
    total_amount: float
    transaction_date: datetime
    asset: AssetResponse
    
    class Config:
        from_attributes = True

class WatchlistBase(BaseModel):
    name: str

class WatchlistCreate(WatchlistBase):
    pass

class WatchlistItemBase(BaseModel):
    asset_id: int

class WatchlistItemCreate(WatchlistItemBase):
    pass

class WatchlistItemResponse(BaseModel):
    id: int
    added_at: datetime
    asset: AssetResponse
    
    class Config:
        from_attributes = True

class WatchlistResponse(WatchlistBase):
    id: int
    user_id: int
    created_at: datetime
    items: List[WatchlistItemResponse] = []
    
    class Config:
        from_attributes = True

class UserWatchlistsResponse(BaseModel):
    watchlists: List[WatchlistResponse]