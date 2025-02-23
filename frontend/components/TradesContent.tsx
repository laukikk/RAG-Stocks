"use client"

import { useState, useEffect } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { StockChart } from "./StockChart"
import { sampleStocks, userPortfolio } from "@/lib/sampleData"
import { TrendingUp, TrendingDown, MinusCircle } from "lucide-react"
import { Watchlist } from "./Watchlist"
import { useSearchParams } from "next/navigation"

export default function TradesContent() {
  const [selectedStock, setSelectedStock] = useState(sampleStocks[0])
  const [quantity, setQuantity] = useState(1)
  const searchParams = useSearchParams()

  useEffect(() => {
    const symbol = searchParams.get("symbol")
    if (symbol) {
      const stock = sampleStocks.find((s) => s.symbol === symbol)
      if (stock) {
        setSelectedStock(stock)
      }
    }
  }, [searchParams])

  const handleStockSelect = (stock) => {
    setSelectedStock(stock)
    setQuantity(1)
  }

  const handleTrade = (action) => {
    console.log(`${action} ${quantity} shares of ${selectedStock.symbol}`)
    // Implement actual trading logic here
  }

  const ownedShares = userPortfolio[selectedStock.symbol] || 0
  const totalCost = quantity * selectedStock.price

  const getRecommendationIcon = (action) => {
    if (action === "BUY") return <TrendingUp className="w-5 h-5 text-green-500" />
    if (action === "SELL") return <TrendingDown className="w-5 h-5 text-red-500" />
    return <MinusCircle className="w-5 h-5 text-yellow-500" />
  }

  return (
    <div className="flex h-[calc(100vh-4rem)]">
      <div className="flex-1 p-6 space-y-6 overflow-y-auto">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-semibold text-foreground">Trades</h1>
          <div className="text-sm text-muted-foreground">
            {selectedStock.symbol} • {selectedStock.sector} • {selectedStock.marketCap}
          </div>
        </div>

        <Card className="h-[60vh]">
          <CardContent className="p-6 h-full">
            <StockChart stock={selectedStock} />
          </CardContent>
        </Card>

        <div className="grid grid-cols-2 gap-6">
          <Card>
            <CardContent className="p-6">
              <div className="space-y-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-semibold text-lg">{selectedStock.name}</h3>
                    <p className="text-sm text-muted-foreground">Current Price: ${selectedStock.price.toFixed(2)}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-muted-foreground">Owned</p>
                    <p className="font-medium">{ownedShares} shares</p>
                  </div>
                </div>

                <div className="flex items-end space-x-4">
                  <div className="flex-1">
                    <label className="text-sm text-muted-foreground">Quantity</label>
                    <Input
                      type="number"
                      min="1"
                      value={quantity}
                      onChange={(e) => setQuantity(Number.parseInt(e.target.value) || 1)}
                    />
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-muted-foreground">Total Cost</p>
                    <p className="font-medium">${totalCost.toFixed(2)}</p>
                  </div>
                </div>

                <div className="flex space-x-2">
                  <Button
                    onClick={() => handleTrade("buy")}
                    className="flex-1 bg-primary text-primary-foreground hover:bg-primary/90"
                  >
                    Buy
                  </Button>
                  <Button
                    onClick={() => handleTrade("sell")}
                    disabled={ownedShares === 0}
                    className={`flex-1 ${ownedShares === 0 ? "bg-muted text-muted-foreground" : "bg-primary text-primary-foreground hover:bg-primary/90"}`}
                  >
                    Sell
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="space-y-4">
                <div className="flex items-center space-x-2">
                  {getRecommendationIcon(selectedStock.recommendation.action)}
                  <h3 className="font-semibold text-lg">Recommendation</h3>
                </div>

                <div className="space-y-2">
                  <p className="font-medium">
                    We recommend to {selectedStock.recommendation.action.toLowerCase()}{" "}
                    {selectedStock.recommendation.timeframe}
                  </p>
                  <p className="text-sm text-muted-foreground">{selectedStock.recommendation.reason}</p>
                </div>

                <div className="pt-2 border-t">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Sector</p>
                      <p className="font-medium">{selectedStock.sector}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Market Cap</p>
                      <p className="font-medium">{selectedStock.marketCap}</p>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <div className="w-80 border-l p-6 overflow-y-auto">
        <Watchlist stocks={userPortfolio} onSelectStock={setSelectedStock} />
      </div>
    </div>
  )
}

