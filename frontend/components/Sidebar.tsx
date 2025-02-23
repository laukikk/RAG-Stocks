"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  LayoutDashboard,
  Briefcase,
  ArrowLeftRight,
  BrainCircuit,
  Lightbulb,
  MessageSquare,
  Settings,
  MessageCircle,
  Newspaper,
} from "lucide-react"

export default function Sidebar() {
  const pathname = usePathname()

  const isActive = (path: string) => pathname === path

  return (
    <div className="w-64 border-r bg-background h-screen flex flex-col">
      <div className="p-6 border-b">
        <Link href="/" className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
            <span className="text-primary-foreground font-semibold">D</span>
          </div>
          <span className="text-xl font-semibold text-primary">DexTrader</span>
        </Link>
      </div>

      <div className="flex-1 py-6 px-4">
        <div className="space-y-6">
          <div>
            <h3 className="text-xs font-semibold text-muted-foreground mb-2 px-2">MAIN</h3>
            <nav className="space-y-1">
              {[
                { href: "/", label: "Dashboard", icon: LayoutDashboard },
                { href: "/portfolio", label: "Portfolio", icon: Briefcase },
                { href: "/trades", label: "Trades", icon: ArrowLeftRight },
                { href: "/news", label: "News", icon: Newspaper },
              ].map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center space-x-2 px-2 py-2 rounded-lg 
                    ${isActive(item.href) ? "bg-primary/10 text-foreground" : "text-muted-foreground hover:bg-accent"}`}
                >
                  <item.icon className="w-5 h-5" />
                  <span>{item.label}</span>
                </Link>
              ))}
            </nav>
          </div>

          <div>
            <h3 className="text-xs font-semibold text-muted-foreground mb-2 px-2">AI</h3>
            <nav className="space-y-1">
              {[
                { href: "/stress-testing", label: "Stress Testing", icon: BrainCircuit },
                { href: "/recommendations", label: "Recommendations", icon: Lightbulb },
                { href: "/chat", label: "Chat", icon: MessageSquare },
              ].map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center space-x-2 px-2 py-2 rounded-lg 
                    ${isActive(item.href) ? "bg-primary/10 text-foreground" : "text-muted-foreground hover:bg-accent"}`}
                >
                  <item.icon className="w-5 h-5" />
                  <span>{item.label}</span>
                </Link>
              ))}
            </nav>
          </div>
        </div>
      </div>

      <div className="mt-auto p-4 space-y-2">
        {[
          { href: "/settings", label: "Settings", icon: Settings },
          { href: "/contact", label: "Contact", icon: MessageCircle },
        ].map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={`flex items-center space-x-2 px-2 py-2 rounded-lg 
              ${isActive(item.href) ? "bg-primary/10 text-primary" : "text-muted-foreground hover:bg-accent"}`}
          >
            <item.icon className="w-5 h-5" />
            <span>{item.label}</span>
          </Link>
        ))}
      </div>
    </div>
  )
}

