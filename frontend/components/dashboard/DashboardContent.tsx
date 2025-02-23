"use client"

import { useState, useEffect } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { ArrowUpRight, ArrowDownRight } from "lucide-react"
import { LatestNews } from "../common/LatestNews"
import { fetchHoldings, type Holding } from "@/lib/fetchHoldings"
import InvestmentValueChart from "./InvestmentValueChart"

const stockCards = [
  { symbol: "AAPL", name: "Apple Inc", price: "15,215.70", change: "+0.05%", portfolio: "Portfolio" },
  { symbol: "TSLA", name: "Tesla Inc", price: "32,140.20", change: "+1.20%", portfolio: "Portfolio" },
  { symbol: "AMZN", name: "Amazon Inc", price: "12,290.40", change: "+2.20%", portfolio: "Portfolio" },
  { symbol: "MSFT", name: "Microsoft Corp", price: "15,215.70", change: "+0.05%", portfolio: "Portfolio" },
]

export default function DashboardContent() {
  const [holdings, setHoldings] = useState<Holding[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchHoldings()
      .then(setHoldings)
      .finally(() => setLoading(false))
  }, [])

  const totalInvested = holdings.reduce((sum, holding) => sum + holding.Invested, 0)
  const totalCurrentValue = holdings.reduce((sum, holding) => sum + holding.CurrentValue, 0)
  const totalProfitLoss = totalCurrentValue - totalInvested
  const totalProfitLossPercentage = (totalProfitLoss / totalInvested) * 100

  if (loading) {
    return <div>Loading...</div>
  }

  return (
    <div className="flex h-screen">
      <div className="flex-auto p-6 space-y-4">
        <h1 className="text-xl font-semibold text-foreground">Dashboard</h1>

        <div className="grid grid-cols-4 gap-4">
          <Card>
            <CardContent className="pt-6">
              <div className="space-y-2">
                <div className="text-sm text-muted-foreground">Initial Investment</div>
                <div className="text-2xl font-bold">${totalInvested.toFixed(2)}</div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="space-y-2">
                <div className="text-sm text-muted-foreground">Current Value</div>
                <div className="text-2xl font-bold">${totalCurrentValue.toFixed(2)}</div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="space-y-2">
                <div className="text-sm text-muted-foreground">Total Gain/Loss</div>
                <div className={`text-2xl font-bold ${totalProfitLoss >= 0 ? "text-green-600" : "text-red-600"}`}>
                  ${totalProfitLoss.toFixed(2)}
                </div>
                <div
                  className={`flex items-center text-sm ${totalProfitLoss >= 0 ? "text-green-600" : "text-red-600"}`}
                >
                  {totalProfitLoss >= 0 ? (
                    <ArrowUpRight className="h-4 w-4 mr-1" />
                  ) : (
                    <ArrowDownRight className="h-4 w-4 mr-1" />
                  )}
                  <span>{totalProfitLossPercentage.toFixed(2)}%</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="space-y-2">
                <div className="text-sm text-muted-foreground">Daily Change</div>
                <div className="text-2xl font-bold text-gray-500">N/A</div>
                <div className="text-sm text-gray-500">Data not available</div>
              </div>
            </CardContent>
          </Card>
        </div>

        <h1 className="text-xl font-semibold text-foreground">Your Stock Portfolio</h1>
        <div className="flex gap-4 pb-4">
          {stockCards.map((stock) => (
            <Card key={stock.symbol} className="flex-1">
              <CardContent className="p-4">
                <div className="flex flex-col gap-1">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-8 h-8 bg-accent rounded-full flex items-center justify-center">
                      {stock.symbol[0]}
                    </div>
                    <div className="text-xs text-muted-foreground">{stock.name}</div>
                  </div>
                  <div className="font-medium">{stock.symbol}</div>
                  <div className="flex items-center justify-between">
                    <div className="text-xl font-semibold">{stock.price}</div>
                    <div className={stock.change.startsWith("+") ? "text-green-600" : "text-red-600"}>
                      {stock.change}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <InvestmentValueChart />
        
      </div>

      <div className="w-80 flex-none p-6 border-l">
        <LatestNews />
      </div>
    </div>
  )
}

