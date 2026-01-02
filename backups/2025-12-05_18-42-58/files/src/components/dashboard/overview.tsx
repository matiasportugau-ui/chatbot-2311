import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown, 
  Users, 
  MessageSquare, 
  DollarSign,
  Clock,
  Target,
  CheckCircle,
  AlertTriangle,
  Activity
} from 'lucide-react'

interface OverviewProps {
  className?: string
}

export function Overview({ className }: OverviewProps) {
  const kpis = [
    {
      title: 'Total Quotes',
      value: '1,234',
      change: '+12.5%',
      trend: 'up',
      icon: BarChart3,
      description: 'Quotes generated this month'
    },
    {
      title: 'Conversion Rate',
      value: '68.2%',
      change: '+3.2%',
      trend: 'up',
      icon: Target,
      description: 'Quotes converted to sales'
    },
    {
      title: 'Active Users',
      value: '89',
      change: '+5.1%',
      trend: 'up',
      icon: Users,
      description: 'Users active this week'
    },
    {
      title: 'Response Time',
      value: '2.3m',
      change: '-15.2%',
      trend: 'down',
      icon: Clock,
      description: 'Average response time'
    }
  ]

  const recentActivities = [
    {
      id: '1',
      type: 'quote',
      title: 'New quote generated',
      description: 'Quote #1234 for 5 solar panels',
      timestamp: '2 minutes ago',
      status: 'success'
    },
    {
      id: '2',
      type: 'user',
      title: 'User feedback received',
      description: '4.5 star rating from customer',
      timestamp: '15 minutes ago',
      status: 'success'
    },
    {
      id: '3',
      type: 'system',
      title: 'System update',
      description: 'AI model updated to v2.1',
      timestamp: '1 hour ago',
      status: 'info'
    },
    {
      id: '4',
      type: 'alert',
      title: 'Performance warning',
      description: 'High CPU usage detected',
      timestamp: '2 hours ago',
      status: 'warning'
    }
  ]

  const getTrendIcon = (trend: string) => {
    return trend === 'up' ? TrendingUp : TrendingDown
  }

  const getTrendColor = (trend: string) => {
    return trend === 'up' ? 'text-green-500' : 'text-red-500'
  }

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'quote': return BarChart3
      case 'user': return Users
      case 'system': return Activity
      case 'alert': return AlertTriangle
      default: return Activity
    }
  }

  const getActivityColor = (status: string) => {
    switch (status) {
      case 'success': return 'text-green-500'
      case 'warning': return 'text-yellow-500'
      case 'error': return 'text-red-500'
      case 'info': return 'text-blue-500'
      default: return 'text-gray-500'
    }
  }

  return (
    <div className={cn("space-y-6", className)}>
      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.map((kpi, index) => {
          const TrendIcon = getTrendIcon(kpi.trend)
          
          return (
            <Card key={index}>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium flex items-center space-x-2">
                  <kpi.icon className="h-4 w-4" />
                  <span>{kpi.title}</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="text-2xl font-bold">{kpi.value}</div>
                  <div className="flex items-center space-x-1">
                    <TrendIcon className={cn("h-4 w-4", getTrendColor(kpi.trend))} />
                    <span className={cn("text-sm", getTrendColor(kpi.trend))}>
                      {kpi.change}
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground">{kpi.description}</p>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Quote Trends */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <BarChart3 className="h-5 w-5" />
              <span>Quote Trends</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="text-3xl font-bold">1,234</div>
              <div className="flex items-center space-x-2">
                <TrendingUp className="h-4 w-4 text-green-500" />
                <span className="text-sm text-green-500">+12.5% from last month</span>
              </div>
              <div className="h-32 bg-muted rounded-lg flex items-center justify-center">
                <span className="text-muted-foreground">Chart placeholder</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Performance Metrics */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Activity className="h-5 w-5" />
              <span>Performance</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-500">98.5%</div>
                  <p className="text-sm text-muted-foreground">Uptime</p>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-500">2.3s</div>
                  <p className="text-sm text-muted-foreground">Avg Response</p>
                </div>
              </div>
              <div className="h-32 bg-muted rounded-lg flex items-center justify-center">
                <span className="text-muted-foreground">Performance chart</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <MessageSquare className="h-5 w-5" />
            <span>Recent Activity</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recentActivities.map((activity) => {
              const ActivityIcon = getActivityIcon(activity.type)
              
              return (
                <div key={activity.id} className="flex items-start space-x-3">
                  <div className={cn("p-2 rounded-full", getActivityColor(activity.status))}>
                    <ActivityIcon className="h-4 w-4" />
                  </div>
                  <div className="flex-1 space-y-1">
                    <div className="flex items-center justify-between">
                      <h4 className="font-medium">{activity.title}</h4>
                      <span className="text-xs text-muted-foreground">{activity.timestamp}</span>
                    </div>
                    <p className="text-sm text-muted-foreground">{activity.description}</p>
                  </div>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Target className="h-5 w-5" />
            <span>Quick Actions</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Button variant="outline" className="h-20 flex flex-col items-center space-y-2">
              <BarChart3 className="h-6 w-6" />
              <span className="text-sm">New Quote</span>
            </Button>
            <Button variant="outline" className="h-20 flex flex-col items-center space-y-2">
              <Users className="h-6 w-6" />
              <span className="text-sm">Add User</span>
            </Button>
            <Button variant="outline" className="h-20 flex flex-col items-center space-y-2">
              <MessageSquare className="h-6 w-6" />
              <span className="text-sm">Send Message</span>
            </Button>
            <Button variant="outline" className="h-20 flex flex-col items-center space-y-2">
              <DollarSign className="h-6 w-6" />
              <span className="text-sm">View Reports</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
