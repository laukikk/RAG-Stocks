"use client"

import { Card, CardContent } from "@/components/ui/card"
import { ArrowUpRight, ArrowDownRight } from "lucide-react"
import Link from "next/link"
import Image from "next/image"
import newsData from "@/lib/sampleNewsData.json"
import { LatestNews } from "./common/LatestNews"

function NewsCard({ article }) {
  return (
    <Card className="overflow-hidden">
      <CardContent className="p-4">
        <div className="flex gap-4">
          <Image
            src={`https://picsum.photos/800/400?random=${article.id}`}
            alt={article.title}
            width={100}
            height={100}
            className="rounded-lg object-cover"
          />
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold line-clamp-2">{article.title}</h3>
            <p className="text-sm text-muted-foreground mt-1">
              {article.source} • {article.time}
            </p>
            <div className="flex items-center mt-2">
              <span className="font-medium">{article.relatedStock}</span>
              <span className={`ml-2 flex items-center ${article.stockPnL >= 0 ? "text-green-600" : "text-red-600"}`}>
                {article.stockPnL >= 0 ? (
                  <ArrowUpRight className="h-4 w-4 mr-1" />
                ) : (
                  <ArrowDownRight className="h-4 w-4 mr-1" />
                )}
                {Math.abs(article.stockPnL).toFixed(2)}%
              </span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default function NewsContent() {
  const recommendedNews = newsData.newsArticles.filter((article) => article.recommended).slice(0, 6)
  const latestNews = newsData.newsArticles.slice(0, 15)

  return (
    <div className="flex p-6 space-x-6">
      <div className="flex-1 space-y-8">
        <section>
          <h2 className="text-2xl font-semibold text-foreground mb-4">Recommended for You</h2>
          <div className="grid grid-cols-3 gap-4">
            {recommendedNews.map((article) => (
              <Link href={`/news/${article.id}`} key={article.id}>
                <NewsCard article={article} />
              </Link>
            ))}
          </div>
        </section>
        <section>
          <h2 className="text-2xl font-semibold text-foreground mb-4">Top Latest News</h2>
          <div className="grid grid-cols-3 gap-4">
            {latestNews.map((article) => (
              <Link href={`/news/${article.id}`} key={article.id}>
                <NewsCard article={article} />
              </Link>
            ))}
          </div>
        </section>
      </div>
      <div className="w-80">
        <LatestNews />
      </div>
    </div>
  )
}

