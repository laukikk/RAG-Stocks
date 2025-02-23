"use client"

import { ArrowUpRight, ArrowDownRight } from "lucide-react"
import Link from "next/link"
import Image from "next/image"
import { Badge } from "@/components/ui/badge"
import newsData from "@/lib/sampleNewsData.json"
import { LatestNews } from "./common/LatestNews"
import { Card, CardContent } from "@/components/ui/card"

const companyNames = {
  AAPL: "Apple Inc",
  GOOGL: "Alphabet Inc",
  MSFT: "Microsoft Corporation",
  AMZN: "Amazon.com Inc",
  TSLA: "Tesla Inc",
  // Add more as needed
}

function NewsCard({ article }) {
  return (
    <Card className="overflow-hidden">
      <CardContent className="p-4">
        <div className="flex gap-4">
          <Image
            src={`https://picsum.photos/200?random=${article.id}`}
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

export default function NewsArticlePage({ articleId }: { articleId: string }) {
  const article = newsData.newsArticles.find((article) => article.id === articleId)
  const similarArticles = newsData.newsArticles
  .filter((a) => a.id !== articleId)
  .sort(() => Math.random() - 0.5) // Shuffle the array randomly
  .slice(0, 3)

  if (!article) {
    return <div>Article not found</div>
  }

  return (
    <div className="flex p-6 space-x-6">
      <div className="flex-1 space-y-6">
        <h1 className="text-3xl font-semibold text-foreground">{article.title}</h1>
        <div className="flex justify-between items-center">
          <p className="text-muted-foreground">
            {article.source} • {article.time}
          </p>
          <div className="flex items-center gap-2">
            <Badge variant="secondary" className="font-normal">
              {companyNames[article.relatedStock] || "Company Name"}
            </Badge>
            <span className="font-medium">{article.relatedStock}</span>
            <span className={`flex items-center ${article.stockPnL >= 0 ? "text-green-600" : "text-red-600"}`}>
              {article.stockPnL >= 0 ? (
                <ArrowUpRight className="h-4 w-4 mr-1" />
              ) : (
                <ArrowDownRight className="h-4 w-4 mr-1" />
              )}
              {Math.abs(article.stockPnL).toFixed(2)}%
            </span>
          </div>
        </div>
        <Image
          src={`https://picsum.photos/800/400?random=${article.id}`}
          alt={article.title}
          width={800}
          height={400}
          className="rounded-lg"
        />
        <p className="text-lg">{article.content}</p>

        {similarArticles.length > 0 && (
          <div className="mt-8">
            <h2 className="text-2xl font-semibold text-foreground mb-4">Similar Articles</h2>
            <div className="grid grid-cols-3 gap-4">
              {similarArticles.map((similarArticle) => (
                <Link href={`/news/${similarArticle.id}`} key={similarArticle.id}>
                  <NewsCard article={similarArticle} />
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>
      <div className="w-80">
        <LatestNews />
      </div>
    </div>
  )
}

