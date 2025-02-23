import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"

const data = [
  { month: "Jan", pnl: 5000 },
  { month: "Feb", pnl: -2000 },
  { month: "Mar", pnl: 7000 },
  { month: "Apr", pnl: 3000 },
  { month: "May", pnl: -1000 },
  { month: "Jun", pnl: 6000 },
]

export default function MonthlyPnLChart() {
  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-semibold mb-4">Monthly P&L</h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="month" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="pnl" fill="#82ca9d" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

