"use client"

import { useEffect, useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { ArrowUpRight, ArrowDownRight } from "lucide-react"
import { fetchHoldings, type Holding } from "@/lib/fetchHoldings"
import { HoldingsTable } from "./HoldingsTable"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"
import { Watchlist } from "../Watchlist"
import { MonthlyPnLChart } from "./MonthlyPnLChart"

export default function PortfolioContent() {
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
      <div className="flex-1 p-6 space-y-6 overflow-auto">
        <h1 className="text-2xl font-semibold text-foreground">Portfolio</h1>

        <div className="grid grid-cols-4 gap-4">
          <Card>
            <CardContent className="pt-6">
              <div className="space-y-2">
                <div className="text-sm text-muted-foreground">Total Invested</div>
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

        <div>
          <ResponsiveContainer width="100%" height="50%">
            <MonthlyPnLChart></MonthlyPnLChart>
          </ResponsiveContainer>
        </div>

        <Card>
          <CardContent className="p-6">
            <h3 className="text-xl font-semibold mb-3">Holdings</h3>
            <HoldingsTable holdings={holdings} />
          </CardContent>
        </Card>
      </div>

      <div className="w-80 p-6 border-l">
        <Watchlist />
      </div>
    </div>
  )
}

