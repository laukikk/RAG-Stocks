from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from typing import List, Optional

from .models import (
    Portfolio, Holding, Transaction,
    PortfolioCreate, 
    PortfolioResponse, 
    UserPortfoliosResponse, 
)

# Portfolio functions
def get_user_portfolios(user_id: int, db: Session) -> UserPortfoliosResponse:
    """
    Retrieve all portfolios for a given user using SQLAlchemy ORM.
    """
    try:
        portfolios = db.query(Portfolio).filter(Portfolio.user_id == user_id).all()
        return UserPortfoliosResponse(
            portfolios=[PortfolioResponse.model_validate(p.__dict__) for p in portfolios]
        )
    finally:
        db.close()