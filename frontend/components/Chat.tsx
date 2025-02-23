"use client"

import { useState, useEffect } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { MessageSquare, Send, PlusCircle } from "lucide-react"
import sampleChatHistories from "@/lib/sampleChatHistories.json"

interface Message {
  role: "user" | "assistant"
  content: string
}

interface ChatHistory {
  id: string
  title: string
  messages: Message[]
}

export default function Chat({ initialPrompt = "" }) {
  const [input, setInput] = useState(initialPrompt)
  const [chatHistories, setChatHistories] = useState<ChatHistory[]>(sampleChatHistories)
  const [currentChat, setCurrentChat] = useState<ChatHistory | null>(null)

  useEffect(() => {
    if (initialPrompt) {
      handleSend()
    }
  }, [initialPrompt])

  const handleSend = () => {
    if (input.trim()) {
      const newMessage: Message = { role: "user", content: input }
      const assistantMessage: Message = { role: "assistant", content: `User typed: ${input}` }

      if (currentChat) {
        setCurrentChat({
          ...currentChat,
          messages: [...currentChat.messages, newMessage, assistantMessage],
        })
      } else {
        const newChat: ChatHistory = {
          id: (chatHistories.length + 1).toString(),
          title: input.slice(0, 30) + (input.length > 30 ? "..." : ""),
          messages: [newMessage, assistantMessage],
        }
        setChatHistories([newChat, ...chatHistories])
        setCurrentChat(newChat)
      }

      setInput("")
    }
  }

  const startNewChat = () => {
    setCurrentChat(null)
    setInput("")
  }

  return (
    <div className="flex h-[calc(100vh-4rem)]">
      <div className="flex-1 p-6 flex flex-col">
        <h1 className="text-2xl font-semibold text-foreground mb-4">AI Chat</h1>
        <Card className="flex-1 mb-4 overflow-auto">
          <CardContent className="p-4">
            {currentChat &&
              currentChat.messages.map((message, index) => (
                <div key={index} className={`mb-4 ${message.role === "user" ? "text-right pl-12" : "text-left pr-12"}`}>
                  <div
                    className={`inline-block p-2 rounded-lg ${message.role === "user" ? "bg-primary text-primary-foreground" : "bg-secondary"}`}
                  >
                    {message.content}
                  </div>
                </div>
              ))}
          </CardContent>
        </Card>
        <div className="flex space-x-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message here..."
            onKeyPress={(e) => e.key === "Enter" && handleSend()}
          />
          <Button onClick={handleSend}>
            <Send className="w-4 h-4 mr-2" />
            Send
          </Button>
        </div>
      </div>
      <div className="w-80 border-l p-6 flex flex-col">
        <h2 className="text-lg font-semibold mb-4">Chat History</h2>
        <div className="flex-1 overflow-auto space-y-2">
          {chatHistories.map((chat) => (
            <Button key={chat.id} variant="ghost" className="w-full justify-start" onClick={() => setCurrentChat(chat)}>
              <MessageSquare className="w-4 h-4 mr-2" />
              {chat.title}
            </Button>
          ))}
        </div>
        <Button onClick={startNewChat} className="mt-4">
          <PlusCircle className="w-4 h-4 mr-2" />
          New Chat
        </Button>
      </div>
    </div>
  )
}

