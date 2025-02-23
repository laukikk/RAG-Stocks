import Link from "next/link"
import newsData from "@/lib/sampleNewsData.json"

export function LatestNews() {
  const latestNews = newsData.newsArticles.slice(0, 5)

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-semibold">Latest News</h2>
      <div className="space-y-4">
        {latestNews.map((news) => (
          <Link
            href={`/news/${news.id}`}
            key={news.id}
            className="block space-y-1 hover:bg-accent rounded-lg p-2 transition-colors"
          >
            <h3 className="font-medium">{news.title}</h3>
            <div className="flex justify-between items-center text-sm">
              <span className="text-muted-foreground">
                {news.source} • {news.time}
              </span>
              <div className="text-right">
                <span className="font-medium">{news.relatedStock}</span>
                <span className={`ml-2 ${news.stockPnL >= 0 ? "text-green-600" : "text-red-600"}`}>
                  {news.stockPnL >= 0 ? "+" : ""}
                  {news.stockPnL}%
                </span>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}

