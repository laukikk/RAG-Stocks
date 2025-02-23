import NewsArticlePage from "@/components/NewsArticlePage"

export default function NewsArticle({ params }: { params: { id: string } }) {
  return <NewsArticlePage articleId={params.id} />
}

