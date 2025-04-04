from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from datetime import datetime

from trading.alpaca_client import AlpacaClient

from alpaca.data import StockHistoricalDataClient
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.data.requests import (
    StockBarsRequest,
    StockQuotesRequest,
    StockTradesRequest,
    StockLatestQuoteRequest,
    StockLatestTradeRequest,
    StockSnapshotRequest,
    MostActivesRequest,
    MarketMoversRequest
)

def str_to_TimeFrame(timeframe: str) -> TimeFrame:
    """
    Convert a string to a TimeFrameUnit.
    """
    try:
        return TimeFrame(int(timeframe[0]), TimeFrameUnit[timeframe[1:]])
    except KeyError:
        raise ValueError(f"Invalid TimeFrameUnit: {timeframe}")

# Initialize Alpaca client (singleton)
alpaca_client = AlpacaClient()

# Create a router for stock market data endpoints
stock_data_router = APIRouter(prefix="/stock", tags=["Stock Market Data"])

@stock_data_router.get("/bars/{symbol}", summary="Get Stock Bars")
def get_stock_bars(
    symbol: str,
    timeframe: str = "1Day",
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    client: StockHistoricalDataClient = Depends(alpaca_client.stock_client)
):
    """
    Retrieve historical bars for the specified stock symbol.
    """
    try:
        bars_req = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=str_to_TimeFrame(timeframe),
            start=start,
            end=end
        )
        bars = client.get_stock_bars(bars_req)
        return bars
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@stock_data_router.get("/quotes/{symbol}", summary="Get Stock Quotes")
def get_stock_quotes(
    symbol: str,
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    client: StockHistoricalDataClient = Depends(alpaca_client.stock_client)
):
    """
    Retrieve historical quotes for the specified stock symbol.
    """
    try:
        quotes_req = StockQuotesRequest(
            symbol_or_symbols=symbol,
            start=start,
            end=end
        )
        quotes = client.get_stock_quotes(quotes_req)
        return quotes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@stock_data_router.get("/trades/{symbol}", summary="Get Stock Trades")
def get_stock_trades(
    symbol: str,
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    client: StockHistoricalDataClient = Depends(alpaca_client.stock_client)
):
    """
    Retrieve historical trades for the specified stock symbol.
    """
    try:
        trades_req = StockTradesRequest(
            symbol_or_symbols=symbol,
            start=start,
            end=end
        )
        trades = client.get_stock_trades(trades_req)
        return trades
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@stock_data_router.get("/latest-quote/{symbol}", summary="Get Stock Latest Quote")
def get_stock_latest_quote(
    symbol: str,
    client: StockHistoricalDataClient = Depends(alpaca_client.stock_client)
):
    """
    Retrieve the latest quote for the specified stock symbol.
    """
    try:
        latest_quote_req = StockLatestQuoteRequest(symbol_or_symbols=symbol)
        latest_quote = client.get_stock_latest_quote(latest_quote_req)
        return latest_quote
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@stock_data_router.get("/latest-trade/{symbol}", summary="Get Stock Latest Trade")
def get_stock_latest_trade(
    symbol: str,
    client: StockHistoricalDataClient = Depends(alpaca_client.stock_client)
):
    """
    Retrieve the latest trade for the specified stock symbol.
    """
    try:
        latest_trade_req = StockLatestTradeRequest(symbol_or_symbols=symbol)
        latest_trade = client.get_stock_latest_trade(latest_trade_req)
        return latest_trade
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@stock_data_router.get("/snapshot/{symbol}", summary="Get Stock Snapshot")
def get_stock_snapshot(
    symbol: str,
    client: StockHistoricalDataClient = Depends(alpaca_client.stock_client)
):
    """
    Retrieve a snapshot for the specified stock symbol.
    """
    try:
        snapshot_req = StockSnapshotRequest(symbol_or_symbols=symbol)
        snapshot = client.get_stock_snapshot(snapshot_req)
        return snapshot
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@stock_data_router.get("/most-actives", summary="Get Most Actives")
def get_most_actives(
    limit: Optional[int] = Query(10),
    client: StockHistoricalDataClient = Depends(alpaca_client.stock_client)
):
    """
    Retrieve a list of the most active stocks.
    """
    try:
        most_actives_req = MostActivesRequest(limit=limit)
        most_actives = client.get_most_actives(most_actives_req)
        return most_actives
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@stock_data_router.get("/market-movers", summary="Get Market Movers")
def get_market_movers(
    client: StockHistoricalDataClient = Depends(alpaca_client.stock_client)
):
    """
    Retrieve a list of market movers.
    """
    try:
        market_movers_req = MarketMoversRequest()
        market_movers = client.get_market_movers(market_movers_req)
        return market_movers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))