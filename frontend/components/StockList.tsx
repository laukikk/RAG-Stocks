import { Card, CardContent } from "@/components/ui/card"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { BarChart2 } from "lucide-react"

export function StockList({ stocks, onSelectStock }) {
  return (
    <div className="space-y-2">
      <h2 className="text-lg font-semibold mb-4">Live Stock Data</h2>
      {stocks.map((stock) => (
        <TooltipProvider key={stock.symbol}>
          <Tooltip>
            <TooltipTrigger asChild>
              <Card
                className="cursor-pointer hover:bg-accent transition-colors relative group"
                onClick={() => onSelectStock(stock)}
              >
                <CardContent className="p-2">
                  <div className="flex justify-between items-center">
                    <div className="font-medium">{stock.symbol}</div>
                    <div className={stock.change >= 0 ? "text-green-600" : "text-red-600"}>
                      ${stock.price.toFixed(2)}
                      <span className="ml-2">
                        {stock.change >= 0 ? "+" : ""}
                        {stock.change.toFixed(2)}%
                      </span>
                    </div>
                  </div>
                  <div className="absolute right-2 top-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <BarChart2 className="h-4 w-4" />
                  </div>
                </CardContent>
              </Card>
            </TooltipTrigger>
            <TooltipContent>
              <div className="space-y-1">
                <p className="font-medium">{stock.name}</p>
                <p className="text-sm text-muted-foreground">{stock.sector}</p>
                <p className="text-sm text-muted-foreground">{stock.marketCap}</p>
                <p className="text-sm font-medium">Open chart</p>
              </div>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      ))}
    </div>
  )
}

