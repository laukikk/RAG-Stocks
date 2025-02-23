"use client"

import Chat from "@/components/Chat"
import { useSearchParams } from "next/navigation"

export default function ChatPage() {
  const searchParams = useSearchParams()
  const initialPrompt = searchParams.get("prompt") || ""

  return <Chat initialPrompt={initialPrompt} />
}

