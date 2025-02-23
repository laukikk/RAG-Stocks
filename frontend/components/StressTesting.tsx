import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Clock, AlertTriangle } from "lucide-react"

export default function StressTesting() {
  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold text-foreground">Portfolio Stress Testing</h1>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Clock className="w-6 h-6" />
            <span>Coming Soon</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground mb-4">
            Our advanced stress testing feature is currently under development. This tool will allow you to:
          </p>
          <ul className="list-disc list-inside space-y-2 mb-6">
            <li>Simulate market crashes and economic downturns</li>
            <li>Test your portfolio against historical crisis scenarios</li>
            <li>Analyze the impact of specific events on your investments</li>
            <li>Receive recommendations to improve portfolio resilience</li>
          </ul>
          <div className="flex items-center space-x-2 text-yellow-500">
            <AlertTriangle className="w-5 h-5" />
            <p className="text-sm">Stay tuned for updates on this exciting feature!</p>
          </div>
        </CardContent>
      </Card>

      <Button disabled className="mt-4">
        Run Stress Test (Coming Soon)
      </Button>
    </div>
  )
}

