import { NextResponse } from "next/server"
import { OpenAI } from "langchain/llms/openai"
import { VectorDBQAChain } from "langchain/chains"
import { SupabaseVectorStore } from "langchain/vectorstores/supabase"
import { OpenAIEmbeddings } from "langchain/embeddings/openai"
import pool from "@/lib/db"

export async function POST(req: Request) {
  try {
    const { query } = await req.json()

    const model = new OpenAI({ temperature: 0 })
    const embeddings = new OpenAIEmbeddings()

    // Initialize the vector store with your Neon PostgreSQL database
    const vectorStore = await SupabaseVectorStore.fromExistingIndex(embeddings, {
      client: pool,
      tableName: "documents",
      queryName: "match_documents",
    })

    const chain = VectorDBQAChain.fromLLM(model, vectorStore)

    const response = await chain.call({
      query: query,
    })

    return NextResponse.json({ result: response.text })
  } catch (error) {
    console.error("Error in RAG query:", error)
    return NextResponse.json({ error: "An error occurred while processing your request." }, { status: 500 })
  }
}

