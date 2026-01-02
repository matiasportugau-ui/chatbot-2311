import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, ComposedChart } from 'recharts'
import { formatNumber } from '@/lib/utils'

interface HourlyData {
  hour: string
  conversations: number
  successRate: number
  avgResponseTime: number
}

interface HourlyChartProps {
  data: HourlyData[]
  className?: string
}

export function HourlyChart({ data, className }: HourlyChartProps) {
  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>Hourly Analysis</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="hour" 
                tick={{ fontSize: 12 }}
                tickFormatter={(value) => `${value}:00`}
              />
              <YAxis yAxisId="left" tick={{ fontSize: 12 }} />
              <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 12 }} />
              <Tooltip 
                formatter={(value: number, name: string) => [
                  name === 'conversations' ? formatNumber(value) :
                  name === 'successRate' ? `${(value * 100).toFixed(1)}%` :
                  name === 'avgResponseTime' ? `${value.toFixed(1)}s` :
                  value,
                  name === 'conversations' ? 'Conversations' :
                  name === 'successRate' ? 'Success Rate' :
                  name === 'avgResponseTime' ? 'Avg Response Time' : name
                ]}
                labelFormatter={(value) => `${value}:00`}
              />
              <Bar
                yAxisId="left"
                dataKey="conversations"
                fill="#8884d8"
                name="Conversations"
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="successRate"
                stroke="#82ca9d"
                strokeWidth={2}
                dot={{ r: 4 }}
                name="Success Rate"
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="avgResponseTime"
                stroke="#ffc658"
                strokeWidth={2}
                dot={{ r: 4 }}
                name="Avg Response Time"
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}
