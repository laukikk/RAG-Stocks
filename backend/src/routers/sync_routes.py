from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Import the sync functions
from integration.sync_databases import (
    ensure_asset_exists,
    sync_positions,
    sync_orders,
    sync_assets,
    sync_asset_historical_data,
    full_sync
)

# Database client
from database.neon_client import NeonClient

# Create NeonClient instance
neon_client = NeonClient()

# Parent router
db_sync_router = APIRouter(prefix="/db-sync", tags=["Syncing"])

# =============================================================================
# Alpaca Sync Router
# =============================================================================

@db_sync_router.post("/full-sync/{account_id}", summary="Perform a full sync with Alpaca")
def full_sync_route(
    account_id: int,
    days_back_for_orders: int = 7,
    db: Session = Depends(neon_client.get_db_session)
):
    """
    Perform a full synchronization of all data from Alpaca for the specified account.
    
    This endpoint syncs positions, orders, and transactions from Alpaca to the database.
    
    Parameters:
    - account_id: The database ID of the account to sync
    - days_back_for_orders: Number of days to look back for orders (default: 7)
    
    Returns:
    - A dictionary with the results of each sync operation
    """
    try:
        results = full_sync(db, account_id, days_back_for_orders)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@db_sync_router.post("/positions/{account_id}", summary="Sync positions from Alpaca")
def sync_positions_route(
    account_id: int,
    db: Session = Depends(neon_client.get_db_session)
):
    """
    Synchronize positions from Alpaca to the database for the specified account.
    
    This endpoint retrieves all positions from Alpaca and updates the database accordingly.
    
    Parameters:
    - account_id: The database ID of the account to sync positions for
    
    Returns:
    - A list of synced positions with their action (added/updated)
    """
    try:
        results = sync_positions(db, account_id)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@db_sync_router.post("/orders/{account_id}", summary="Sync orders from Alpaca")
def sync_orders_route(
    account_id: int,
    days_back: int = 7,
    db: Session = Depends(neon_client.get_db_session)
):
    """
    Synchronize orders from Alpaca to the database for the specified account.
    
    This endpoint fetches orders from Alpaca for the specified date range and updates the database.
    
    Parameters:
    - account_id: The database ID of the account to sync orders for
    - days_back: Number of days to look back for orders (default: 7)
    
    Returns:
    - A list of synced orders with their action (added/updated/unchanged)
    """
    try:
        results = sync_orders(db, account_id, days_back)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# @alpaca_sync_router.post("/assets", summary="Sync all assets from Alpaca")
# def sync_assets_route(
#     account_id: int,
#     db: Session = Depends(neon_client.get_db_session)
# ):
#     """
#     Synchronize all tradable assets from Alpaca to the database.
    
#     This endpoint retrieves all tradable assets from Alpaca and adds them to the database if they don't exist.
    
#     Parameters:
#     - account_id: The database ID of the account to use for syncing context
    
#     Returns:
#     - A list of synced assets with their action (added/exists)
#     """
#     try:
#         results = sync_assets(db)
#         return results
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


@db_sync_router.post("/assets/{symbol}/ensure", summary="Ensure an asset exists")
def ensure_asset_exists_route(
    symbol: str,
    account_id: int,
    history_sync: bool = True,
    db: Session = Depends(neon_client.get_db_session)
):
    """
    Ensure that a specific asset exists in the database, fetching it from Alpaca if needed.
    
    This endpoint checks if the asset exists in the database, and if not, creates it from Alpaca data.
    
    Parameters:
    - symbol: The stock symbol to ensure exists
    - account_id: The database ID of the account to use for syncing context
    - history_sync: Whether to sync historical data for the asset (default: True)
    
    Returns:
    - The asset object from the database
    """
    try:
        asset = ensure_asset_exists(db, account_id, symbol, history_sync)
        return asset
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@db_sync_router.post("/assets/{symbol}/historical", summary="Sync historical data for an asset")
def sync_asset_historical_data_route(
    symbol: str,
    account_id: int,
    days: int = 365,
    db: Session = Depends(neon_client.get_db_session)
):
    """
    Synchronize historical price data for a specific asset from Alpaca.
    
    This endpoint fetches historical price bars for the specified asset and number of days.
    
    Parameters:
    - symbol: The stock symbol to sync historical data for
    - account_id: The database ID of the account to use for syncing context
    - days: Number of days of historical data to sync (default: 365)
    
    Returns:
    - A list of price records synced with their action (added/failed)
    """
    try:
        results = sync_asset_historical_data(db, account_id, symbol, days)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@db_sync_router.post("/background/{account_id}", summary="Perform sync in background")
def background_sync_route(
    account_id: int,
    background_tasks: BackgroundTasks,
    days_back_for_orders: int = 7,
    db: Session = Depends(neon_client.get_db_session)
):
    """
    Start a full synchronization with Alpaca in the background.
    
    This endpoint schedules a full sync to run in the background, allowing the API to return immediately.
    
    Parameters:
    - account_id: The database ID of the account to sync
    - days_back_for_orders: Number of days to look back for orders (default: 7)
    
    Returns:
    - A message indicating the sync has been scheduled
    """
    try:
        # Add the sync task to background tasks
        background_tasks.add_task(full_sync, db, account_id, days_back_for_orders)
        return {"message": f"Background sync scheduled for account {account_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
