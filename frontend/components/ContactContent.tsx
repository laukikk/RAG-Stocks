"use client"

import type React from "react"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"

export default function ContactContent() {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Handle form submission
  }

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-semibold text-primary">Contact Us</h1>

      <Card>
        <CardHeader>
          <CardTitle>Send us a message</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Name</Label>
              <Input id="name" placeholder="Your name" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" placeholder="your@email.com" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="message">Message</Label>
              <Textarea id="message" placeholder="Your message" rows={5} />
            </div>
            <Button type="submit" className="bg-primary text-primary-foreground hover:bg-primary/90">
              Send Message
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Contact Information</CardTitle>
        </CardHeader>
        <CardContent>
          <p>Email: support@dextrader.com</p>
          <p>Phone: +1 (555) 123-4567</p>
          <p>Address: 123 Trading St, Financial District, New York, NY 10005</p>
        </CardContent>
      </Card>
    </div>
  )
}

