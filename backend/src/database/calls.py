from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import date, datetime, timedelta

# Custom library imports
from .models import (
    User, Account, Stock, PortfolioHolding, 
    Order, Transaction, Watchlist, 
    WatchlistItem, FinancialStatement, 
    Dividend, StockDailyPrice
)
from utils.security import generate_account_number

class DatabaseCalls:
    @classmethod
    def create_user(cls, db: Session, username: str, email: str, password_hash: str, 
                    first_name: str = None, last_name: str = None, 
                    date_of_birth: date = None, phone_number: str = None) -> User:
        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            phone_number=phone_number
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    @classmethod
    def get_user_by_email(cls, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    @classmethod
    def create_account(cls, db: Session, user_id: int, account_type: str, currency: str = 'USD') -> Account:
        account_number = generate_account_number(user_id, account_type)
        new_account = Account(
            user_id=user_id,
            account_type=account_type,
            account_number=account_number,
            currency=currency
        )
        db.add(new_account)
        db.commit()
        db.refresh(new_account)
        return new_account

    @classmethod
    def create_stock(cls, db: Session, symbol: str, company_name: str, 
                     exchange: str, sector: str = None, industry: str = None) -> Stock:
        new_stock = Stock(
            symbol=symbol,
            company_name=company_name,
            exchange=exchange,
            sector=sector,
            industry=industry
        )
        db.add(new_stock)
        db.commit()
        db.refresh(new_stock)
        return new_stock

    @classmethod
    def add_portfolio_holding(cls, db: Session, account_id: int, stock_id: int, 
                               quantity: int, average_price: float) -> PortfolioHolding:
        new_holding = PortfolioHolding(
            account_id=account_id,
            stock_id=stock_id,
            quantity=quantity,
            average_purchase_price=average_price
        )
        db.add(new_holding)
        db.commit()
        db.refresh(new_holding)
        return new_holding

    @classmethod
    def create_order(cls, db: Session, account_id: int, stock_id: int, 
                     order_type: str, transaction_type: str, quantity: int, 
                     price: float = None, stop_price: float = None) -> Order:
        new_order = Order(
            account_id=account_id,
            stock_id=stock_id,
            order_type=order_type,
            transaction_type=transaction_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price
        )
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        return new_order

    @classmethod
    def record_transaction(cls, db: Session, account_id: int, stock_id: int, 
                           transaction_type: str, quantity: int, price: float, 
                           order_id: int = None, commission: float = 0.0) -> Transaction:
        total_amount = quantity * price + commission
        new_transaction = Transaction(
            order_id=order_id,
            account_id=account_id,
            stock_id=stock_id,
            transaction_type=transaction_type,
            quantity=quantity,
            price=price,
            commission=commission,
            total_amount=total_amount
        )
        db.add(new_transaction)
        db.commit()
        db.refresh(new_transaction)
        return new_transaction

    @classmethod
    def create_watchlist(cls, db: Session, user_id: int, name: str) -> Watchlist:
        new_watchlist = Watchlist(
            user_id=user_id,
            name=name
        )
        db.add(new_watchlist)
        db.commit()
        db.refresh(new_watchlist)
        return new_watchlist

    @classmethod
    def add_watchlist_item(cls, db: Session, watchlist_id: int, stock_id: int) -> WatchlistItem:
        new_item = WatchlistItem(
            watchlist_id=watchlist_id,
            stock_id=stock_id
        )
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item

    @classmethod
    def record_stock_daily_price(cls, db: Session, stock_id: int, date: date, 
                                  close_price: float, open_price: float = None, 
                                  high_price: float = None, low_price: float = None, 
                                  volume: int = None) -> StockDailyPrice:
        new_daily_price = StockDailyPrice(
            stock_id=stock_id,
            date=date,
            open_price=open_price,
            high_price=high_price,
            low_price=low_price,
            close_price=close_price,
            volume=volume
        )
        db.add(new_daily_price)
        db.commit()
        db.refresh(new_daily_price)
        return new_daily_price

    @classmethod
    def get_stock_price_history(cls, db: Session, stock_id: int, 
                                 start_date: date = None, 
                                 end_date: date = None) -> List[StockDailyPrice]:
        query = db.query(StockDailyPrice).filter(StockDailyPrice.stock_id == stock_id)
        
        if start_date:
            query = query.filter(StockDailyPrice.date >= start_date)
        
        if end_date:
            query = query.filter(StockDailyPrice.date <= end_date)
        
        return query.order_by(StockDailyPrice.date).all()

    @classmethod
    def get_stock_performance(cls, db: Session, stock_id: int, 
                               days: int = 30) -> dict:
        # Get the most recent date in the daily prices
        latest_date = db.query(func.max(StockDailyPrice.date)).filter(
            StockDailyPrice.stock_id == stock_id
        ).scalar()

        if not latest_date:
            return None

        start_date = latest_date - timedelta(days=days)

        # Fetch price history
        prices = db.query(StockDailyPrice).filter(
            StockDailyPrice.stock_id == stock_id,
            StockDailyPrice.date >= start_date
        ).order_by(StockDailyPrice.date).all()

        if not prices:
            return None

        return {
            'start_price': prices[0].close_price,
            'end_price': prices[-1].close_price,
            'performance_percentage': ((prices[-1].close_price - prices[0].close_price) / prices[0].close_price) * 100,
            'highest_price': max(price.high_price for price in prices),
            'lowest_price': min(price.low_price for price in prices),
            'total_volume': sum(price.volume or 0 for price in prices)
        }

    @classmethod
    def get_user_portfolio_summary(cls, db: Session, user_id: int) -> dict:
        # Get all accounts for the user
        accounts = db.query(Account).filter(Account.user_id == user_id).all()
        
        total_portfolio_value = 0
        holdings_details = []

        for account in accounts:
            # Get portfolio holdings with stock details
            holdings = db.query(PortfolioHolding).filter(
                PortfolioHolding.account_id == account.account_id
            ).options(joinedload(PortfolioHolding.stock)).all()

            for holding in holdings:
                # Get latest stock price
                latest_price = db.query(StockDailyPrice).filter(
                    StockDailyPrice.stock_id == holding.stock_id
                ).order_by(desc(StockDailyPrice.date)).first()

                current_value = holding.quantity * (latest_price.close_price if latest_price else holding.average_purchase_price)
                total_portfolio_value += current_value

                holdings_details.append({
                    'symbol': holding.stock.symbol,
                    'company_name': holding.stock.company_name,
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