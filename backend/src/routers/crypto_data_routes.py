from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from datetime import datetime

from trading.alpaca_client import AlpacaClient

from alpaca.data import CryptoHistoricalDataClient
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.data.requests import (
    CryptoBarsRequest,
    CryptoQuoteRequest,
    CryptoTradesRequest,
    CryptoLatestQuoteRequest,
    CryptoLatestTradeRequest,
    CryptoSnapshotRequest
)

def str_to_TimeFrame(timeframe: str) -> TimeFrame:
    """
    Convert a string to a TimeFrameUnit.
    """
    try:
        return TimeFrame(int(timeframe[0]), TimeFrameUnit[timeframe[1:]])
    except KeyError:
        raise ValueError(f"Invalid TimeFrameUnit: {timeframe}")

alpaca_client = AlpacaClient()

# Create a router for crypto market data endpoints
crypto_data_router = APIRouter(prefix="/crypto", tags=["Crypto Market Data"])

@crypto_data_router.get("/bars/{symbol:path}", summary="Get Crypto Bars")
def get_crypto_bars(
    symbol: str,
    timeframe: str = "1Day",
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    client: CryptoHistoricalDataClient = Depends(alpaca_client.crypto_client)
):
    """
    Retrieve historical bars for the specified crypto symbol.
    Symbol can be in the format 'ETH/USD'.
    """
    try:
        bars_req = CryptoBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=str_to_TimeFrame(timeframe),
            start=start,
            end=end
        )
        bars = client.get_crypto_bars(bars_req)
        return bars
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@crypto_data_router.get("/quotes/{symbol:path}", summary="Get Crypto Quotes")
def get_crypto_quotes(
    symbol: str,
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    client: CryptoHistoricalDataClient = Depends(alpaca_client.crypto_client)
):
    """
    Retrieve historical quotes for the specified crypto symbol.
    """
    try:
        quotes_req = CryptoQuoteRequest(
            symbol_or_symbols=symbol,
            start=start,
            end=end
        )
        quotes = client.get_crypto_quotes(quotes_req)
        return quotes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@crypto_data_router.get("/trades/{symbol:path}", summary="Get Crypto Trades")
def get_crypto_trades(
    symbol: str,
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    client: CryptoHistoricalDataClient = Depends(alpaca_client.crypto_client)
):
    """
    Retrieve historical trades for the specified crypto symbol.
    """
    try:
        trades_req = CryptoTradesRequest(
            symbol_or_symbols=symbol,
            start=start,
            end=end
        )
        trades = client.get_crypto_trades(trades_req)
        return trades
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@crypto_data_router.get("/latest-quote/{symbol:path}", summary="Get Crypto Latest Quote")
def get_crypto_latest_quote(
    symbol: str,
    client: CryptoHistoricalDataClient = Depends(alpaca_client.crypto_client)
):
    """
    Retrieve the latest quote for the specified crypto symbol.
    """
    try:
        latest_quote_req = CryptoLatestQuoteRequest(symbol_or_symbols=symbol)
        latest_quote = client.get_crypto_latest_quote(latest_quote_req)
        return latest_quote
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@crypto_data_router.get("/latest-trade/{symbol:path}", summary="Get Crypto Latest Trade")
def get_crypto_latest_trade(
    symbol: str,
    client: CryptoHistoricalDataClient = Depends(alpaca_client.crypto_client)
):
    """
    Retrieve the latest trade for the specified crypto symbol.
    """
    try:
        latest_trade_req = CryptoLatestTradeRequest(symbol_or_symbols=symbol)
        latest_trade = client.get_crypto_latest_trade(latest_trade_req)
        return latest_trade
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@crypto_data_router.get("/snapshot/{symbol:path}", summary="Get Crypto Snapshot")
def get_crypto_snapshot(
    symbol: str,
    client: CryptoHistoricalDataClient = Depends(alpaca_client.crypto_client)
):
    """
    Retrieve a snapshot for the specified crypto symbol.
    """
    try:
        snapshot_req = CryptoSnapshotRequest(symbol_or_symbols=symbol)
        snapshot = client.get_crypto_snapshot(snapshot_req)
        return snapshot
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
