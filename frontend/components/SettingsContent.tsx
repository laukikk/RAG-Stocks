"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"

export default function SettingsContent() {
  const [notifications, setNotifications] = useState(true)
  const [darkMode, setDarkMode] = useState(false)

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-semibold text-primary">Settings</h1>

      <Card>
        <CardHeader>
          <CardTitle>Account Settings</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input id="email" type="email" placeholder="your@email.com" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input id="password" type="password" />
          </div>
          <Button className="bg-primary text-primary-foreground hover:bg-primary/90">Update Account</Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Preferences</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <Label htmlFor="notifications">Enable Notifications</Label>
            <Switch id="notifications" checked={notifications} onCheckedChange={setNotifications} />
          </div>
          <div className="flex items-center justify-between">
            <Label htmlFor="darkMode">Dark Mode</Label>
            <Switch id="darkMode" checked={darkMode} onCheckedChange={setDarkMode} />
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

