"use client"

import { TrendingUp, TrendingDown } from "lucide-react"
import { Area, AreaChart, CartesianGrid, XAxis, YAxis, Tooltip } from "recharts"
import { subMonths, format } from "date-fns"

import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { type ChartConfig, ChartContainer } from "@/components/ui/chart"

const generateChartData = () => {
  const data = []
  const startValue = 100000
  const numMonths = 6

  for (let i = numMonths - 1; i >= 0; i--) {
    const date = subMonths(new Date(), i)
    const value = startValue + Math.random() * 20000 - 10000 // Random fluctuation
    data.push({
      month: format(date, "MMMM"),
      value: Math.round(value),
    })
  }

  return data
}

const chartData = generateChartData()

const chartConfig = {
  value: {
    label: "Investment Value",
    color: "hsl(var(--primary))",
  },
} satisfies ChartConfig

export default function InvestmentValueChart() {
  const firstValue = chartData[0].value
  const lastValue = chartData[chartData.length - 1].value
  const percentageChange = ((lastValue - firstValue) / firstValue) * 100
  const isPositive = percentageChange >= 0

  return (
    <Card>
      <CardHeader>
        <CardTitle>Investment Value</CardTitle>
        <CardDescription>Showing total investment value for the last 6 months</CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig}>
          <AreaChart
            accessibilityLayer
            data={chartData}
            margin={{
              top: 10,
              right: 30,
              left: 0,
              bottom: 0,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis
              dataKey="month"
              tickLine={false}
              axisLine={false}
              tickMargin={8}
              tickFormatter={(value) => value.slice(0, 3)}
            />
            <YAxis tickLine={false} axisLine={false} tickFormatter={(value) => `$${value.toLocaleString()}`} />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  return (
                    <div className="bg-background p-2 rounded-md shadow border">
                      <p className="font-semibold">{payload[0].payload.month}</p>
                      <p className="text-primary">${payload[0].value.toLocaleString()}</p>
                    </div>
                  )
                }
                return null
              }}
            />
            <defs>
              <linearGradient id="fillValue" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="var(--color-value)" stopOpacity={0.8} />
                <stop offset="95%" stopColor="var(--color-value)" stopOpacity={0.1} />
              </linearGradient>
            </defs>
            <Area type="monotone" dataKey="value" stroke="var(--color-value)" fillOpacity={1} fill="url(#fillValue)" />
          </AreaChart>
        </ChartContainer>
      </CardContent>
      <CardFooter className="flex justify-between">
        <div className="text-sm text-muted-foreground">Starting value: ${firstValue.toLocaleString()}</div>
        <div className={`flex items-center ${isPositive ? "text-green-600" : "text-red-600"}`}>
          {isPositive ? <TrendingUp className="mr-1 h-4 w-4" /> : <TrendingDown className="mr-1 h-4 w-4" />}
          <span>{percentageChange.toFixed(2)}%</span>
        </div>
      </CardFooter>
    </Card>
  )
}

