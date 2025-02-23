import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Clock, Lightbulb } from "lucide-react"

export default function Recommendations() {
  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold text-foreground">Investment Recommendations</h1>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Clock className="w-6 h-6" />
            <span>Coming Soon</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground mb-4">
            Our AI-powered investment recommendation system is in the final stages of development. Once launched, you'll
            be able to:
          </p>
          <ul className="list-disc list-inside space-y-2 mb-6">
            <li>Receive personalized investment suggestions based on your risk profile</li>
            <li>Discover new investment opportunities across various asset classes</li>
            <li>Get insights on potential portfolio rebalancing strategies</li>
            <li>Access real-time market analysis and trend predictions</li>
          </ul>
          <div className="flex items-center space-x-2 text-blue-500">
            <Lightbulb className="w-5 h-5" />
            <p className="text-sm">We're excited to bring you cutting-edge investment advice soon!</p>
          </div>
        </CardContent>
      </Card>

      <Button disabled className="mt-4">
        Get Recommendations (Coming Soon)
      </Button>
    </div>
  )
}

