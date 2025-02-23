import type React from "react"
import { Raleway } from "next/font/google"
import "./globals.css"
import { ThemeProvider } from "@/components/theme-provider"
import Header from "@/components/Header"
import Sidebar from "@/components/Sidebar"

const raleway = Raleway({
  weight: ["300", "400", "500", "700"],
  subsets: ["latin"],
  display: "swap",
})

export const metadata = {
  title: "DexTrader - Portfolio Management",
  description: "AI-powered stock portfolio management platform",
    generator: 'v0.dev'
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={raleway.className}>
        <ThemeProvider attribute="class" defaultTheme="dark" enableSystem={false} disableTransitionOnChange>
          <div className="flex h-screen">
            <Sidebar />
            <div className="flex-1 flex flex-col">
              <Header />
              <main className="flex-1 overflow-auto bg-accent">{children}</main>
            </div>
          </div>
        </ThemeProvider>
      </body>
    </html>
  )
}



import './globals.css'