export default function Metrics() {
  const metrics = [
    { label: "Total Value", value: "$100,000" },
    { label: "Daily Change", value: "+$1,200 (1.2%)" },
    { label: "Total Gain/Loss", value: "+$15,000 (15%)" },
    { label: "Number of Positions", value: "12" },
  ]

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-semibold mb-4">Portfolio Metrics</h2>
      <div className="grid grid-cols-2 gap-4">
        {metrics.map((metric) => (
          <div key={metric.label} className="text-center">
            <p className="text-gray-600">{metric.label}</p>
            <p className="text-xl font-bold">{metric.value}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

