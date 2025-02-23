"use client"

import type React from "react"

import { useState } from "react"

export default function RagInput() {
  const [query, setQuery] = useState("")
  const [result, setResult] = useState("")
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const response = await fetch("/api/rag", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      })

      if (!response.ok) {
        throw new Error("Failed to fetch RAG result")
      }

      const data = await response.json()
      setResult(data.result)
    } catch (error) {
      console.error("Error fetching RAG result:", error)
      setResult("An error occurred while processing your request.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <form onSubmit={handleSubmit} className="flex mb-4">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask about your portfolio..."
          className="px-2 py-1 rounded-l-md text-black flex-grow"
        />
        <button type="submit" className="bg-blue-500 px-4 py-1 rounded-r-md" disabled={loading}>
          {loading ? "Loading..." : "Ask"}
        </button>
      </form>
      {result && (
        <div className="bg-gray-100 p-4 rounded-md">
          <h3 className="font-semibold mb-2">Result:</h3>
          <p>{result}</p>
        </div>
      )}
    </div>
  )
}

