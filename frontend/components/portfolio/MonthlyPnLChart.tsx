"use client"

import { TrendingUp } from "lucide-react"
import { Bar, BarChart, CartesianGrid, Cell, XAxis, YAxis, Tooltip } from "recharts"
import { useState, useEffect } from "react"

import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { type ChartConfig, ChartContainer } from "@/components/ui/chart"

const chartData = [
  { month: "Mar", pnl: 7000 },
  { month: "Apr", pnl: 3000 },
  { month: "May", pnl: -1000 },
  { month: "Jun", pnl: 6000 },
  { month: "Jul", pnl: -2000 },
  { month: "Aug", pnl: 4000 },
  { month: "Sep", pnl: 2000 },
  { month: "Oct", pnl: -2000 },
  { month: "Nov", pnl: 5000 },
  { month: "Dec", pnl: 3000 },
  { month: "Jan", pnl: 5000 },
  { month: "Feb", pnl: -2000 },
]

const chartConfig = {
  pnl: {
    label: "Profit/Loss",
  },
} satisfies ChartConfig

export function MonthlyPnLChart() {
  const [isMounted, setIsMounted] = useState(false)

  useEffect(() => {
    setIsMounted(true)
  }, [])

  if (!isMounted) {
    return null // or a loading indicator
  }

  const totalPnL = chartData.reduce((sum, item) => sum + item.pnl, 0)
  const percentageChange = (totalPnL / Math.abs(chartData[0].pnl)) * 100

  return (
    <Card>
      <CardHeader>
        <CardTitle>Monthly Profit/Loss</CardTitle>
        <CardDescription>March 2023 - February 2024</CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig}>
          <BarChart accessibilityLayer data={chartData}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="month" tickLine={false} axisLine={false} />
            <YAxis tickLine={false} axisLine={false} tickFormatter={(value) => `$${value.toLocaleString()}`} />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  return (
                    <div className="bg-background p-2 rounded-md shadow border">
                      <p className="font-semibold">{payload[0].payload.month}</p>
                      <p className={payload[0].value >= 0 ? "text-green-600" : "text-red-600"}>
                        ${payload[0].value.toLocaleString()}
                      </p>
                    </div>
                  )
                }
                return null
              }}
            />
            <Bar dataKey="pnl">
              {chartData.map((item) => (
                <Cell key={item.month} fill={item.pnl > 0 ? "hsl(var(--chart-1))" : "hsl(var(--chart-2))"} />
              ))}
            </Bar>
          </BarChart>
        </ChartContainer>
      </CardContent>
      <CardFooter className="flex justify-between">
        <div className="text-sm text-muted-foreground">Total P&L: ${totalPnL.toLocaleString()}</div>
        <div className="flex items-center text-green-600">
          <TrendingUp className="mr-1 h-4 w-4" />
          <span>{percentageChange.toFixed(2)}% overall change</span>
        </div>
      </CardFooter>
    </Card>
  )
}

