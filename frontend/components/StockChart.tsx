"use client"

import { useEffect, useRef } from "react"

declare global {
  interface Window {
    TradingView: any
  }
}

export function StockChart({ stock }) {
  const containerRef = useRef(null)

  useEffect(() => {
    if (containerRef.current) {
      const script = document.createElement("script")
      script.src = "https://s3.tradingview.com/tv.js"
      script.async = true
      script.onload = () => {
        if (window.TradingView) {
          new window.TradingView.widget({
            autosize: true,
            symbol: stock.symbol,
            interval: "D",
            timezone: "Etc/UTC",
            theme: "dark",
            style: "1",
            locale: "en",
            toolbar_bg: "#f1f3f6",
            enable_publishing: false,
            allow_symbol_change: true,
            container_id: "tradingview_chart",
            width: "100%",
            height: "100%",
          })
        }
      }
      document.head.appendChild(script)
    }

    return () => {
      if (containerRef.current) {
        containerRef.current.innerHTML = ""
      }
    }
  }, [stock])

  return (
    <div className="w-full h-full">
      <div id="tradingview_chart" ref={containerRef} className="w-full h-full" />
    </div>
  )
}

