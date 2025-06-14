from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
import asyncio
import json

# Custom imports
from database.calls import (
    get_portfolio_holdings,
    get_user_portfolio_summary,
    get_asset_by_id,
    get_asset_price_history
)
from database.models import PortfolioHolding, AssetDailyPrice
from database.neon_client import NeonClient
from trading.alpaca_client import AlpacaClient

# Initialize clients
neon_client = NeonClient()
alpaca_client = AlpacaClient()

# Router
portfolio_api_router = APIRouter(prefix="/api/portfolio")

# Connected WebSocket clients
connected_clients = {}

# =============================================================================
# Portfolio Analytics HTTP Routes
# =============================================================================

@portfolio_api_router.get("/investment/{account_id}", summary="Get total investment for an account")
async def get_total_investment(account_id: int, db: Session = Depends(neon_client.get_db_session)):
    """
    Get the initial/total investment value for an account.
    """
    try:
        # Get all holdings for the account
        holdings = get_portfolio_holdings(db, account_id)
        if not holdings:
            raise HTTPException(status_code=404, detail="No holdings found for this account")
        
        # Calculate total investment (quantity * average purchase price)
        total_invested = sum(holding.quantity * holding.average_purchase_price for holding in holdings)
        
        return {
            "account_id": account_id,
            "total_invested": total_invested
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@portfolio_api_router.get("/top-holdings/{account_id}", summary="Get top 6 holdings by value")
async def get_top_holdings(account_id: int, limit: int = 6, db: Session = Depends(neon_client.get_db_session)):
    """
    Get the top holdings (by invested value) for an account.
    """
    try:
        # Get all holdings for the account
        holdings = get_portfolio_holdings(db, account_id)
        if not holdings:
            raise HTTPException(status_code=404, detail="No holdings found for this account")
        
        # Calculate current value for each holding and sort
        holdings_with_value = []
        for holding in holdings:
            invested_value = holding.quantity * holding.average_purchase_price
            
            holdings_with_value.append({
                "symbol": holding.asset.symbol,
                "company_name": holding.asset.company_name,
                "quantity": holding.quantity,
                "average_purchase_price": holding.average_purchase_price,
                "invested_value": invested_value,
                "asset_id": holding.asset_id
            })
        
        # Sort by invested value (descending) and take top 'limit'
        sorted_holdings = sorted(holdings_with_value, key=lambda x: x["invested_value"], reverse=True)
        top_holdings = sorted_holdings[:limit]
        
        return {
            "account_id": account_id,
            "top_holdings": top_holdings
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@portfolio_api_router.get("/historical-value/{account_id}", summary="Get historical portfolio values")
async def get_historical_portfolio_value(
    account_id: int, 
    months: int = 6, 
    db: Session = Depends(neon_client.get_db_session)
):
    """
    Get daily portfolio values for the past X months.
    """
    try:
        # Calculate start date (6 months ago from today)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30 * months)
        
        # Get all holdings for the account
        holdings = get_portfolio_holdings(db, account_id)
        if not holdings:
            raise HTTPException(status_code=404, detail="No holdings found for this account")
        
        # Get all unique dates in the range across all assets
        all_dates = set()
        asset_price_histories = {}
        
        for holding in holdings:
            # Get price history for each asset
            price_history = get_asset_price_history(db, holding.asset_id, start_date, end_date)
            
            # Store price history by date for easy lookup
            asset_price_histories[holding.asset_id] = {
                price.date: price.close_price for price in price_history
            }
            
            # Collect all unique dates
            all_dates.update(price.date for price in price_history)
        
        # Sort dates
        sorted_dates = sorted(all_dates)
        
        # Calculate portfolio value for each date
        portfolio_values = []
        for current_date in sorted_dates:
            daily_value = 0
            
            for holding in holdings:
                # Get price for this asset on this date if available
                if current_date in asset_price_histories.get(holding.asset_id, {}):
                    price = asset_price_histories[holding.asset_id][current_date]
                    daily_value += holding.quantity * price
            
            if daily_value > 0:  # Only add days where we have price data
                portfolio_values.append({
                    "date": current_date.isoformat(),
                    "portfolio_value": daily_value
                })
        
        return {
            "account_id": account_id,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "daily_values": portfolio_values
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# WebSocket Implementation for Real-time Updates
# =============================================================================

@portfolio_api_router.websocket("/ws/{account_id}")
async def portfolio_websocket(websocket: WebSocket, account_id: int):
    await websocket.accept()
    
    # Store client connection
    if account_id not in connected_clients:
        connected_clients[account_id] = []
    connected_clients[account_id].append(websocket)
    
    try:
        # Get portfolio holdings to monitor
        db = next(neon_client.get_db_session())
        holdings = get_portfolio_holdings(db, account_id)
        
        if not holdings:
            await websocket.send_text(json.dumps({"error": "No holdings found for this account"}))
            await websocket.close()
            return
        
        # Extract symbols to subscribe to
        symbols = [holding.asset.symbol for holding in holdings]
        
        # Set up Alpaca stock data stream
        stock_stream = alpaca_client.stock_stream_client()
        
        # Initialize portfolio data
        portfolio_data = {
            "holdings": {holding.asset.symbol: {
                "asset_id": holding.asset_id,
                "quantity": holding.quantity,
                "average_purchase_price": holding.average_purchase_price,
                "current_price": None,
                "previous_close": None
            } for holding in holdings},
            "total_invested": sum(holding.quantity * holding.average_purchase_price for holding in holdings),
            "current_value": 0,
            "daily_change_value": 0,
            "daily_change_pnl": 0,
            "total_gain_loss": 0,
            "total_gain_loss_pnl": 0
        }
        
        # Set up subscription for stock updates
        async def subscribe_and_receive():
            # Subscribe to trade updates for all symbols
            stock_stream.subscribe_trades(symbols)
            
            # Also get quote data for more comprehensive price info
            stock_stream.subscribe_quotes(symbols)
            
            # Handle incoming trade data
            async def handle_trade_updates(trade):
                symbol = trade.symbol
                
                # Update current price
                if symbol in portfolio_data["holdings"]:
                    portfolio_data["holdings"][symbol]["current_price"] = trade.price
                    
                    # Recalculate portfolio metrics
                    await calculate_portfolio_metrics()
                    
                    # Send update to all connected clients
                    await broadcast_updates(account_id)
            
            # Handle incoming quote data
            async def handle_quote_updates(quote):
                symbol = quote.symbol
                
                # Update previous close price (for daily change calculations)
                if symbol in portfolio_data["holdings"]:
                    # Use the ask price as the current price
                    portfolio_data["holdings"][symbol]["current_price"] = quote.ask_price
                    
                    # Recalculate portfolio metrics
                    await calculate_portfolio_metrics()
                    
                    # Send update to all connected clients
                    await broadcast_updates(account_id)
            
            # Set handlers for trade and quote data
            stock_stream.handler = handle_trade_updates
            stock_stream.quote_handler = handle_quote_updates
            
            # Start receiving updates
            await stock_stream._run_ws()
        
        # Function to calculate portfolio metrics
        async def calculate_portfolio_metrics():
            current_value = 0
            daily_change_value = 0
            
            for symbol, data in portfolio_data["holdings"].items():
                if data["current_price"] is not None:
                    # Calculate holding value
                    holding_value = data["quantity"] * data["current_price"]
                    current_value += holding_value
                    
                    # Calculate daily change if previous_close is available
                    if data["previous_close"] is not None:
                        daily_change = data["current_price"] - data["previous_close"]
                        daily_change_value += data["quantity"] * daily_change
            
            # Update portfolio metrics
            portfolio_data["current_value"] = current_value
            portfolio_data["daily_change_value"] = daily_change_value
            
            # Calculate percentages
            if current_value > 0:
                portfolio_data["daily_change_pnl"] = (daily_change_value / (current_value - daily_change_value)) * 100
            else:
                portfolio_data["daily_change_pnl"] = 0
            
            # Calculate total gain/loss
            portfolio_data["total_gain_loss"] = current_value - portfolio_data["total_invested"]
            
            if portfolio_data["total_invested"] > 0:
                portfolio_data["total_gain_loss_pnl"] = (portfolio_data["total_gain_loss"] / portfolio_data["total_invested"]) * 100
            else:
                portfolio_data["total_gain_loss_pnl"] = 0
        
        # Function to broadcast updates to all connected clients
        async def broadcast_updates(account_id):
            if account_id in connected_clients:
                # Prepare data for sending (just the relevant metrics)
                update_data = {
                    "current_value": portfolio_data["current_value"],
                    "daily_change_value": portfolio_data["daily_change_value"],
                    "daily_change_pnl": portfolio_data["daily_change_pnl"],
                    "total_gain_loss": portfolio_data["total_gain_loss"],
                    "total_gain_loss_pnl": portfolio_data["total_gain_loss_pnl"],
                    "timestamp": datetime.now().isoformat()
                }
                
                # Send to all connected clients for this account
                for client in connected_clients[account_id]:
                    try:
                        await client.send_text(json.dumps(update_data))
                    except Exception:
                        # Handle closed connections
                        pass
        
        # Initialize previous close prices
        # This would typically come from yesterday's closing prices
        # For simplicity, we're setting them to the average purchase price initially
        for symbol, data in portfolio_data["holdings"].items():
            data["previous_close"] = data["average_purchase_price"]
        
        # Start subscription task
        subscription_task = asyncio.create_task(subscribe_and_receive())
        
        # Heartbeat to keep connection alive
        while True:
            try:
                # Wait for messages from client (not used, but keeps connection alive)
                data = await websocket.receive_text()
            except WebSocketDisconnect:
                break
    
    except WebSocketDisconnect:
        # Remove this client from connected clients
        if account_id in connected_clients and websocket in connected_clients[account_id]:
            connected_clients[account_id].remove(websocket)
    except Exception as e:
        # Handle exceptions
        try:
            await websocket.send_text(json.dumps({"error": str(e)}))
        except:
            pass
    finally:
        # Cleanup
        if account_id in connected_clients and websocket in connected_clients[account_id]:
            connected_clients[account_id].remove(websocket)
        
        try:
            await websocket.close()
        except:
            pass