import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import type { Holding } from "@/lib/fetchHoldings"

interface HoldingsTableProps {
  holdings: Holding[]
}

export function HoldingsTable({ holdings }: HoldingsTableProps) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Investment</TableHead>
          <TableHead>Quantity</TableHead>
          <TableHead>Avg. Cost</TableHead>
          <TableHead>Current Price</TableHead>
          <TableHead>Current Value</TableHead>
          <TableHead>P&L</TableHead>
          <TableHead>Net Change</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {holdings.map((holding) => (
          <TableRow key={holding.Investment}>
            <TableCell>{holding.Investment}</TableCell>
            <TableCell>{holding.Quantity}</TableCell>
            <TableCell>${holding.AverageCost.toFixed(2)}</TableCell>
            <TableCell>${holding.LastTradedPrice.toFixed(2)}</TableCell>
            <TableCell>${holding.CurrentValue.toFixed(2)}</TableCell>
            <TableCell className={holding.ProfitLoss >= 0 ? "text-green-600" : "text-red-600"}>
              ${holding.ProfitLoss.toFixed(2)}
            </TableCell>
            <TableCell className={holding.NetChange >= 0 ? "text-green-600" : "text-red-600"}>
              {holding.NetChange.toFixed(2)}%
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}

