import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { formatNumber } from '@/lib/utils'

interface PerformanceData {
  date: string
  responseTime: number
  conversionRate: number
  satisfaction: number
  uptime: number
}

interface PerformanceChartProps {
  data: PerformanceData[]
  className?: string
}

export function PerformanceChart({ data, className }: PerformanceChartProps) {
  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>Performance Metrics</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="date" 
                tick={{ fontSize: 12 }}
                tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
              />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip 
                formatter={(value: number, name: string) => [
                  name === 'responseTime' ? `${value.toFixed(1)}s` :
                  name === 'conversionRate' ? `${(value * 100).toFixed(1)}%` :
                  name === 'satisfaction' ? `${value.toFixed(1)}/10` :
                  name === 'uptime' ? `${value.toFixed(1)}%` :
                  value,
                  name === 'responseTime' ? 'Response Time' :
                  name === 'conversionRate' ? 'Conversion Rate' :
                  name === 'satisfaction' ? 'Satisfaction' :
                  name === 'uptime' ? 'Uptime' : name
                ]}
                labelFormatter={(value) => new Date(value).toLocaleDateString()}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="responseTime"
                stroke="#8884d8"
                strokeWidth={2}
                dot={{ r: 4 }}
                name="Response Time (s)"
              />
              <Line
                type="monotone"
                dataKey="conversionRate"
                stroke="#82ca9d"
                strokeWidth={2}
                dot={{ r: 4 }}
                name="Conversion Rate"
              />
              <Line
                type="monotone"
                dataKey="satisfaction"
                stroke="#ffc658"
                strokeWidth={2}
                dot={{ r: 4 }}
                name="Satisfaction (/10)"
              />
              <Line
                type="monotone"
                dataKey="uptime"
                stroke="#ff7300"
                strokeWidth={2}
                dot={{ r: 4 }}
                name="Uptime (%)"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}
