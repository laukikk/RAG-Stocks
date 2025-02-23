import Papa from "papaparse"

export interface Holding {
  Investment: string
  Quantity: number
  AverageCost: number
  LastTradedPrice: number
  Invested: number
  CurrentValue: number
  ProfitLoss: number
  NetChange: number
  DayChange: number
  PurchaseDate: Date
  PurchaseTime: string
}

const currentPrices = {
  AAPL: 245.83,
  GOOGL: 184.915,
  AMZN: 222.97,
  MSFT: 416.13,
  TSLA: 354.4,
}

export async function fetchHoldings(): Promise<Holding[]> {
  const response = await fetch(
    "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/sample_holdings-twDUUvTfAYsM021UhweX0KszG9TQuY.csv",
  )
  const csvText = await response.text()

  return new Promise((resolve, reject) => {
    Papa.parse(csvText, {
      header: true,
      dynamicTyping: true,
      complete: (results) => {
        const holdings = results.data
          .map((row: any) => {
            const investment = row.Investment
            const quantity = Number.parseFloat(row["Qty."])
            const averageCost = Number.parseFloat(row["Avg. cost"])
            const lastTradedPrice = currentPrices[investment] || Number.parseFloat(row.LTP)
            const invested = averageCost * quantity
            const currentValue = lastTradedPrice * quantity
            const profitLoss = currentValue - invested
            const netChange = (profitLoss / invested) * 100

            return {
              Investment: investment,
              Quantity: quantity,
              AverageCost: averageCost,
              LastTradedPrice: lastTradedPrice,
              Invested: invested,
              CurrentValue: currentValue,
              ProfitLoss: profitLoss,
              NetChange: netChange,
              DayChange: 0, // We don't have this data, so setting it to 0
              PurchaseDate: new Date(row["Purchase Date"]),
              PurchaseTime: row["Purchase Time"],
            }
          })
          .filter((holding) => holding.Investment !== undefined)
        resolve(holdings as Holding[])
      },
      error: (error) => {
        reject(error)
      },
    })
  })
}

