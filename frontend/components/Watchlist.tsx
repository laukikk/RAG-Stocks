"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Plus, BarChart2 } from "lucide-react"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import Link from "next/link"
import { sampleStocks } from '@/lib/sampleData';

const watchlistStocks = {
  all: sampleStocks,
  gainers: sampleStocks.filter(
    stock => !String(stock.change).startsWith("-")
  ),
  losers: sampleStocks.filter(
    stock => String(stock.change).startsWith("-")
  ),
};


export function Watchlist({ stocks, onSelectStock }) {
  const [activeTab, setActiveTab] = useState("all")

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-foreground">Watchlist</h2>
        <Button variant="ghost" size="icon">
          <Plus className="h-4 w-4" />
        </Button>
      </div>
      <Tabs defaultValue="all" onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="all">All</TabsTrigger>
          <TabsTrigger value="gainers">Gainers</TabsTrigger>
          <TabsTrigger value="losers">Losers</TabsTrigger>
        </TabsList>
      </Tabs>
      <div className="space-y-1">
        {watchlistStocks[activeTab].map((stock, index) => (
          <div key={stock.symbol}>
            <div className="relative group">
              <div className="flex items-center justify-between p-2 rounded-lg transition-all duration-300 group-hover:blur-sm">
                <div>
                  <div className="font-medium">{stock.symbol}</div>
                  <div className="text-sm text-muted-foreground">{stock.name}</div>
                </div>
                <div className="text-right">
                  <div className="font-medium">{stock.price}</div>
                  <div className={!String(stock.change).startsWith("-") ? "text-green-600" : "text-red-600"}>{stock.change} %</div>
                </div>
              </div>
              <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <Button variant="secondary" className="flex items-center space-x-2 bg-gray-500 bg-opacity-0" onClick={() => onSelectStock(stock)}>
                  <BarChart2 className="h-4 w-4" />
                  <span>Open Chart</span>
                </Button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
