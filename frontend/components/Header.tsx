"use client"

import type React from "react"

import { Search, Command } from "lucide-react"
import { Input } from "@/components/ui/input"
import { useEffect, useState } from "react"
import { ThemeToggle } from "./ThemeToggle"
import Image from "next/image"
import { useRouter } from "next/navigation"

export default function Header() {
  const [searchOpen, setSearchOpen] = useState(false)
  const [searchInput, setSearchInput] = useState("")
  const router = useRouter()

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "i" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        setSearchOpen(true)
      }
    }

    document.addEventListener("keydown", down)
    return () => document.removeEventListener("keydown", down)
  }, [])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchInput.trim()) {
      router.push(`/chat?prompt=${encodeURIComponent(searchInput)}`)
      setSearchInput("")
    }
  }

  return (
    <header className="border-b bg-background">
      <div className="flex items-center justify-between px-6 h-16">
        <div className="flex items-center flex-1 space-x-4">
          <form onSubmit={handleSearch} className="relative w-96">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-primary" />
            <Command className="absolute right-2 top-2.5 h-4 w-4 text-primary" />
            <Input
              placeholder="Ask anything about your portfolio... (⌘+I)"
              className="pl-8 pr-8 w-full bg-accent focus:ring-primary"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              onFocus={() => setSearchOpen(true)}
            />
          </form>
        </div>

        <div className="flex items-center space-x-4">
          <ThemeToggle />
          <div className="flex items-center space-x-2">
            <Image
              src="https://avatar.iran.liara.run/public"
              alt="Laukik Avhad"
              width={32}
              height={32}
              className="rounded-full"
            />
            <div>
              <div className="text-sm font-medium">Laukik Avhad</div>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}

