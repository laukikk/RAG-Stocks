export function LatestNews() {
  const mockNews = [
    {
      id: 1,
      title: "Market Rally Continues as Tech Stocks Surge",
      source: "Financial Times",
      time: "2 hours ago",
    },
    {
      id: 2,
      title: "Fed Signals Potential Rate Cut in 2024",
      source: "Wall Street Journal",
      time: "3 hours ago",
    },
    {
      id: 3,
      title: "AI Boom Drives Record Investment in Tech Sector",
      source: "Bloomberg",
      time: "5 hours ago",
    },
    // Add more news items as needed
  ]

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-semibold">Latest News</h2>
      <div className="space-y-4">
        {mockNews.map((news) => (
          <div key={news.id} className="space-y-1">
            <h3 className="font-medium">{news.title}</h3>
            <div className="text-sm text-muted-foreground">
              {news.source} • {news.time}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

