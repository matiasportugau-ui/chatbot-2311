'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import { 
  BarChart3, 
  TrendingUp, 
  Users, 
  MessageSquare, 
  Settings, 
  Bell,
  Activity,
  Target,
  Shield,
  Database,
  Globe,
  HelpCircle,
  Search,
  Filter,
  RefreshCw,
  Sun,
  Moon,
  Zap,
  FileText
} from 'lucide-react'

// Import all dashboard components
import { Overview } from './overview'
import { QuoteAnalytics } from './quote-analytics'
import { PerformanceMetrics } from './performance-metrics'
import { SystemHealth } from './system-health'
import { TrendAnalysis } from './trend-analysis'
import { UserFeedback } from './user-feedback'
import { AIInsights } from './ai-insights'
import { RealTimeMonitoring } from './real-time-monitoring'
import { ImprovementSuggestions } from './improvement-suggestions'
import { ExportImport } from './export-import'
import { Notifications } from './notifications'
import { SearchFilters } from './search-filters'
import { HelpSupport } from './help-support'
import { Settings as SettingsComponent } from './settings'
import { ContextManagement } from './context-management'
import { ChatInterface } from '../chat/chat-interface'
import { BMCChatInterface } from '../chat/bmc-chat-interface'
import { QuotesManager } from './quotes-manager'
import { IntegratedSystemMetrics } from './integrated-system-metrics'
import { GoogleSheetsDashboard } from './google-sheets-dashboard'
import { Header } from './header'
import { Sidebar } from './sidebar'
import { Footer } from './footer'
import { MercadoLibreListings } from './mercado-libre-listings'
import { MercadoLibreOrders } from './mercado-libre-orders'

interface MainDashboardProps {
  className?: string
}

export function MainDashboard({ className }: MainDashboardProps) {
  const [activeTab, setActiveTab] = useState('overview')
  const [isDarkMode, setIsDarkMode] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const tabs = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'analytics', label: 'Analytics', icon: TrendingUp },
    { id: 'performance', label: 'Performance', icon: Activity },
    { id: 'health', label: 'System Health', icon: Shield },
    { id: 'context', label: 'Context Management', icon: Database },
    { id: 'chat', label: 'Live Chat', icon: MessageSquare },
    { id: 'integrated', label: 'Sistema Integrado', icon: Zap },
    { id: 'mercado-libre', label: 'Mercado Libre', icon: Globe },
    { id: 'sheets', label: 'Google Sheets', icon: FileText },
    { id: 'trends', label: 'Trends', icon: Target },
    { id: 'feedback', label: 'Feedback', icon: MessageSquare },
    { id: 'insights', label: 'AI Insights', icon: Database },
    { id: 'monitoring', label: 'Monitoring', icon: Globe },
    { id: 'improvements', label: 'Improvements', icon: TrendingUp },
    { id: 'export', label: 'Export/Import', icon: Database },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'search', label: 'Search', icon: Search },
    { id: 'help', label: 'Help', icon: HelpCircle },
    { id: 'settings', label: 'Settings', icon: Settings }
  ]

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return <Overview />
      case 'analytics':
        return <QuoteAnalytics analytics={{
          totalQuotes: 1234,
          quotesThisMonth: 89,
          quotesLastMonth: 76,
          averageQuoteValue: 2500,
          conversionRate: 0.682,
          averageResponseTime: 2.3,
          topProducts: [
            { name: 'Solar Panels', count: 45, percentage: 0.35 },
            { name: 'Batteries', count: 32, percentage: 0.25 },
            { name: 'Inverters', count: 28, percentage: 0.22 }
          ],
          quotesByStatus: [
            { status: 'Pending', count: 45, percentage: 0.35 },
            { status: 'Approved', count: 32, percentage: 0.25 },
            { status: 'Rejected', count: 28, percentage: 0.22 }
          ],
          quotesByTime: [
            { hour: 9, count: 12 },
            { hour: 10, count: 18 },
            { hour: 11, count: 15 },
            { hour: 14, count: 22 },
            { hour: 15, count: 19 },
            { hour: 16, count: 14 }
          ],
          revenue: {
            total: 3085000,
            thisMonth: 222500,
            lastMonth: 190000,
            growth: 0.171
          }
        }} />
      case 'performance':
        return <PerformanceMetrics metrics={[
          {
            name: 'Response Time',
            value: 2.3,
            target: 5.0,
            unit: 'seconds',
            trend: 'down',
            status: 'excellent',
            description: 'Average response time for quote generation',
            lastUpdated: '2024-12-19T10:30:00Z'
          },
          {
            name: 'Uptime',
            value: 99.9,
            target: 99.5,
            unit: '%',
            trend: 'stable',
            status: 'excellent',
            description: 'System availability',
            lastUpdated: '2024-12-19T10:30:00Z'
          },
          {
            name: 'CPU Usage',
            value: 45,
            target: 80,
            unit: '%',
            trend: 'stable',
            status: 'good',
            description: 'Current CPU utilization',
            lastUpdated: '2024-12-19T10:30:00Z'
          }
        ]} />
      case 'health':
        return <SystemHealth metrics={[
          {
            name: 'API Health',
            status: 'healthy',
            value: 100,
            maxValue: 100,
            unit: '%',
            description: 'API endpoint availability',
            lastChecked: '2024-12-19T10:30:00Z',
            trend: 'stable'
          },
          {
            name: 'Database',
            status: 'healthy',
            value: 95,
            maxValue: 100,
            unit: '%',
            description: 'Database connection health',
            lastChecked: '2024-12-19T10:30:00Z',
            trend: 'stable'
          }
        ]} />
      case 'context':
        return <ContextManagement />
      case 'chat':
        return <BMCChatInterface userPhone="+59891234567" />
      case 'integrated':
        return <IntegratedSystemMetrics />
      case 'mercado-libre':
        return (
          <div className="space-y-6">
            <MercadoLibreListings />
            <MercadoLibreOrders />
          </div>
        )
      case 'sheets':
        return <GoogleSheetsDashboard />
      case 'trends':
        return <TrendAnalysis trends={[
          {
            metric: 'Quote Volume',
            description: 'Total number of quotes generated over time',
            currentValue: 1234,
            previousValue: 1100,
            change: 134,
            changePercentage: 12.2,
            trend: 'up',
            confidence: 0.95,
            data: [
              { period: 'Week 1', value: 280, change: 15, changePercentage: 5.7 },
              { period: 'Week 2', value: 320, change: 40, changePercentage: 14.3 },
              { period: 'Week 3', value: 290, change: -30, changePercentage: -9.4 },
              { period: 'Week 4', value: 344, change: 54, changePercentage: 18.6 }
            ],
            insights: [
              'Quote volume is trending upward',
              'Peak activity occurs on weekdays',
              'Weekend activity is consistently lower'
            ],
            recommendations: [
              'Consider increasing weekend marketing',
              'Optimize weekday response times',
              'Implement automated follow-ups'
            ]
          }
        ]} />
      case 'feedback':
        return <UserFeedback feedback={[
          {
            id: '1',
            user: 'John Smith',
            rating: 5,
            comment: 'Great system! Very easy to use and generates accurate quotes quickly.',
            category: 'general',
            priority: 'low',
            status: 'resolved',
            timestamp: '2024-12-19T10:30:00Z',
            response: 'Thank you for your feedback!',
            tags: ['positive', 'usability']
          }
        ]} />
      case 'insights':
        return <AIInsights insights={[
          {
            id: '1',
            type: 'recommendation',
            title: 'Optimize Quote Response Time',
            description: 'AI analysis suggests implementing caching for frequently requested products.',
            confidence: 0.92,
            impact: 'high',
            urgency: 'medium',
            category: 'Performance',
            metrics: ['Response Time', 'User Satisfaction'],
            actionItems: [
              'Implement Redis caching',
              'Optimize database queries',
              'Add CDN for static assets'
            ],
            expectedOutcome: 'Reduce response time by 40%',
            timestamp: '2024-12-19T10:30:00Z'
          }
        ]} />
      case 'monitoring':
        return <RealTimeMonitoring metrics={[
          {
            name: 'API Response Time',
            value: 150,
            unit: 'ms',
            status: 'online',
            lastUpdate: '2024-12-19T10:30:00Z',
            trend: 'stable',
            threshold: { warning: 500, critical: 1000 }
          }
        ]} />
      case 'improvements':
        return <ImprovementSuggestions suggestions={[
          {
            id: '1',
            category: 'Performance',
            priority: 'high',
            title: 'Implement Caching Layer',
            description: 'Add Redis caching to improve response times',
            expectedImpact: '40% faster response times',
            implementationEffort: 'medium',
            confidenceScore: 0.92,
            status: 'pending',
            metricsAffected: ['Response Time', 'User Satisfaction']
          }
        ]} />
      case 'export':
        return <ExportImport />
      case 'notifications':
        return <Notifications />
      case 'search':
        return <SearchFilters 
          onSearch={(query) => console.log('Search:', query)}
          onFilterChange={(filters) => console.log('Filters:', filters)}
        />
      case 'help':
        return <HelpSupport />
      case 'settings':
        return <SettingsComponent />
      default:
        return <Overview />
    }
  }

  return (
    <div className={cn("min-h-screen bg-background", className)}>
      {/* Header */}
      <Header />

      <div className="flex">
        {/* Sidebar */}
        {sidebarOpen && (
          <div className="w-64 p-4">
            <Sidebar />
          </div>
        )}

        {/* Main Content */}
        <div className="flex-1 p-6">
          {/* Tab Navigation */}
          <Card className="mb-6">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex flex-wrap gap-2">
                  {tabs.map((tab) => {
                    const TabIcon = tab.icon
                    return (
                      <Button
                        key={tab.id}
                        variant={activeTab === tab.id ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setActiveTab(tab.id)}
                        className="flex items-center space-x-2"
                      >
                        <TabIcon className="h-4 w-4" />
                        <span>{tab.label}</span>
                      </Button>
                    )
                  })}
                </div>
                <div className="flex items-center space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setSidebarOpen(!sidebarOpen)}
                  >
                    <BarChart3 className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setIsDarkMode(!isDarkMode)}
                  >
                    {isDarkMode ? (
                      <Sun className="h-4 w-4" />
                    ) : (
                      <Moon className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Tab Content */}
          <div className="space-y-6">
            {renderTabContent()}
          </div>
        </div>
      </div>

      {/* Footer */}
      <Footer />
    </div>
  )
}
