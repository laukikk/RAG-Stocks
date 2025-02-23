const news = [
  {
    id: 1,
    title: "Tech Stocks Surge on AI Advancements",
    source: "Financial Times",
    date: "2023-06-15",
  },
  {
    id: 2,
    title: "Federal Reserve Hints at Potential Rate Hike",
    source: "Wall Street Journal",
    date: "2023-06-14",
  },
  {
    id: 3,
    title: "Oil Prices Stabilize Amid Global Supply Concerns",
    source: "Reuters",
    date: "2023-06-13",
  },
  {
    id: 4,
    title: "Emerging Markets Show Signs of Recovery",
    source: "Bloomberg",
    date: "2023-06-12",
  },
]

export default function LatestNews() {
  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-semibold mb-4">Latest News</h2>
      <ul className="space-y-4">
        {news.map((item) => (
          <li key={item.id} className="border-b pb-2">
            <h3 className="font-semibold">{item.title}</h3>
            <p className="text-sm text-gray-600">
              {item.source} - {item.date}
            </p>
          </li>
        ))}
      </ul>
    </div>
  )
}

