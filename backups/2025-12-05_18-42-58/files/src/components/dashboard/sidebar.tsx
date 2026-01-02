import React from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import { 
  Home, 
  BarChart3, 
  Users, 
  MessageSquare, 
  Settings, 
  HelpCircle,
  Bell,
  Search,
  Filter,
  Activity,
  TrendingUp,
  Target,
  Shield,
  Database,
  Globe
} from 'lucide-react'

interface SidebarProps {
  className?: string
}

export function Sidebar({ className }: SidebarProps) {
  const navigationItems = [
    { id: 'overview', label: 'Overview', icon: Home, badge: null },
    { id: 'analytics', label: 'Analytics', icon: BarChart3, badge: null },
    { id: 'quotes', label: 'Quotes', icon: MessageSquare, badge: '12' },
    { id: 'users', label: 'Users', icon: Users, badge: null },
    { id: 'performance', label: 'Performance', icon: Activity, badge: null },
    { id: 'trends', label: 'Trends', icon: TrendingUp, badge: null },
    { id: 'targets', label: 'Targets', icon: Target, badge: null },
    { id: 'security', label: 'Security', icon: Shield, badge: null },
    { id: 'data', label: 'Data', icon: Database, badge: null },
    { id: 'integrations', label: 'Integrations', icon: Globe, badge: null }
  ]

  const quickActions = [
    { id: 'search', label: 'Search', icon: Search, description: 'Find anything' },
    { id: 'filter', label: 'Filter', icon: Filter, description: 'Filter data' },
    { id: 'notifications', label: 'Notifications', icon: Bell, description: 'View alerts' },
    { id: 'settings', label: 'Settings', icon: Settings, description: 'Configure' },
    { id: 'help', label: 'Help', icon: HelpCircle, description: 'Get support' }
  ]

  return (
    <div className={cn("space-y-4", className)}>
      {/* Navigation */}
      <Card>
        <CardContent className="p-4">
          <div className="space-y-2">
            <h3 className="font-medium text-sm text-muted-foreground mb-3">Navigation</h3>
            {navigationItems.map((item) => (
              <Button
                key={item.id}
                variant="ghost"
                className="w-full justify-start h-10"
              >
                <item.icon className="h-4 w-4 mr-3" />
                <span className="flex-1 text-left">{item.label}</span>
                {item.badge && (
                  <Badge variant="secondary" className="ml-2">
                    {item.badge}
                  </Badge>
                )}
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card>
        <CardContent className="p-4">
          <div className="space-y-2">
            <h3 className="font-medium text-sm text-muted-foreground mb-3">Quick Actions</h3>
            {quickActions.map((action) => (
              <Button
                key={action.id}
                variant="outline"
                className="w-full justify-start h-10"
              >
                <action.icon className="h-4 w-4 mr-3" />
                <div className="flex-1 text-left">
                  <div className="font-medium">{action.label}</div>
                  <div className="text-xs text-muted-foreground">{action.description}</div>
                </div>
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Status */}
      <Card>
        <CardContent className="p-4">
          <div className="space-y-3">
            <h3 className="font-medium text-sm text-muted-foreground">System Status</h3>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm">API Status</span>
                <Badge variant="success">Online</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Database</span>
                <Badge variant="success">Connected</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">AI Services</span>
                <Badge variant="success">Active</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">WhatsApp</span>
                <Badge variant="warning">Limited</Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Recent Activity */}
      <Card>
        <CardContent className="p-4">
          <div className="space-y-2">
            <h3 className="font-medium text-sm text-muted-foreground">Recent Activity</h3>
            <div className="space-y-2">
              <div className="text-xs text-muted-foreground">
                <div className="font-medium">Quote #1234</div>
                <div>Generated 2 minutes ago</div>
              </div>
              <div className="text-xs text-muted-foreground">
                <div className="font-medium">User feedback</div>
                <div>Received 15 minutes ago</div>
              </div>
              <div className="text-xs text-muted-foreground">
                <div className="font-medium">System update</div>
                <div>Completed 1 hour ago</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
