'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import { 
  Settings as SettingsIcon, 
  User, 
  Bell, 
  Shield, 
  Palette, 
  Database,
  Globe,
  Save,
  RefreshCw
} from 'lucide-react'

interface SettingsProps {
  className?: string
}

export function Settings({ className }: SettingsProps) {
  const [activeTab, setActiveTab] = useState('general')
  const [isSaving, setIsSaving] = useState(false)

  const tabs = [
    { id: 'general', label: 'General', icon: SettingsIcon },
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'appearance', label: 'Appearance', icon: Palette },
    { id: 'data', label: 'Data', icon: Database },
    { id: 'integrations', label: 'Integrations', icon: Globe }
  ]

  const handleSave = async () => {
    setIsSaving(true)
    // Simulate save operation
    await new Promise(resolve => setTimeout(resolve, 1000))
    setIsSaving(false)
  }

  const renderGeneralSettings = () => (
    <div className="space-y-6">
      <div className="space-y-4">
        <h4 className="font-medium">Dashboard Settings</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Default View</label>
            <select className="w-full p-2 border rounded-lg">
              <option value="overview">Overview</option>
              <option value="analytics">Analytics</option>
              <option value="quotes">Quotes</option>
              <option value="custom">Custom</option>
            </select>
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Refresh Interval</label>
            <select className="w-full p-2 border rounded-lg">
              <option value="30">30 seconds</option>
              <option value="60">1 minute</option>
              <option value="300">5 minutes</option>
              <option value="900">15 minutes</option>
            </select>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <h4 className="font-medium">Language & Region</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Language</label>
            <select className="w-full p-2 border rounded-lg">
              <option value="es">Español</option>
              <option value="en">English</option>
              <option value="pt">Português</option>
            </select>
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Timezone</label>
            <select className="w-full p-2 border rounded-lg">
              <option value="America/Montevideo">Montevideo (GMT-3)</option>
              <option value="America/New_York">New York (GMT-5)</option>
              <option value="Europe/London">London (GMT+0)</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  )

  const renderProfileSettings = () => (
    <div className="space-y-6">
      <div className="space-y-4">
        <h4 className="font-medium">Personal Information</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">First Name</label>
            <input type="text" className="w-full p-2 border rounded-lg" defaultValue="John" />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Last Name</label>
            <input type="text" className="w-full p-2 border rounded-lg" defaultValue="Doe" />
          </div>
        </div>
        <div className="space-y-2">
          <label className="text-sm font-medium">Email</label>
          <input type="email" className="w-full p-2 border rounded-lg" defaultValue="john.doe@example.com" />
        </div>
      </div>

      <div className="space-y-4">
        <h4 className="font-medium">Role & Permissions</h4>
        <div className="space-y-2">
          <label className="text-sm font-medium">Role</label>
          <select className="w-full p-2 border rounded-lg">
            <option value="admin">Administrator</option>
            <option value="manager">Manager</option>
            <option value="user">User</option>
            <option value="viewer">Viewer</option>
          </select>
        </div>
      </div>
    </div>
  )

  const renderNotificationSettings = () => (
    <div className="space-y-6">
      <div className="space-y-4">
        <h4 className="font-medium">Notification Preferences</h4>
        <div className="space-y-3">
          {[
            { name: 'Email Notifications', description: 'Receive notifications via email' },
            { name: 'Push Notifications', description: 'Receive push notifications' },
            { name: 'SMS Notifications', description: 'Receive SMS notifications' },
            { name: 'Desktop Notifications', description: 'Show desktop notifications' }
          ].map((setting) => (
            <div key={setting.name} className="flex items-center justify-between">
              <div>
                <p className="font-medium">{setting.name}</p>
                <p className="text-sm text-muted-foreground">{setting.description}</p>
              </div>
              <input type="checkbox" defaultChecked className="rounded" />
            </div>
          ))}
        </div>
      </div>

      <div className="space-y-4">
        <h4 className="font-medium">Notification Types</h4>
        <div className="space-y-3">
          {[
            'System Alerts',
            'Quote Updates',
            'Performance Warnings',
            'AI Insights',
            'User Feedback',
            'Security Alerts'
          ].map((type) => (
            <div key={type} className="flex items-center justify-between">
              <span className="text-sm">{type}</span>
              <input type="checkbox" defaultChecked className="rounded" />
            </div>
          ))}
        </div>
      </div>
    </div>
  )

  const renderSecuritySettings = () => (
    <div className="space-y-6">
      <div className="space-y-4">
        <h4 className="font-medium">Password & Authentication</h4>
        <div className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Current Password</label>
            <input type="password" className="w-full p-2 border rounded-lg" />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">New Password</label>
            <input type="password" className="w-full p-2 border rounded-lg" />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Confirm New Password</label>
            <input type="password" className="w-full p-2 border rounded-lg" />
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <h4 className="font-medium">Two-Factor Authentication</h4>
        <div className="flex items-center justify-between">
          <div>
            <p className="font-medium">2FA Status</p>
            <p className="text-sm text-muted-foreground">Add an extra layer of security</p>
          </div>
          <Badge variant="secondary">Disabled</Badge>
        </div>
        <Button size="sm" variant="outline">Enable 2FA</Button>
      </div>

      <div className="space-y-4">
        <h4 className="font-medium">Session Management</h4>
        <div className="space-y-2">
          <label className="text-sm font-medium">Session Timeout</label>
          <select className="w-full p-2 border rounded-lg">
            <option value="15">15 minutes</option>
            <option value="30">30 minutes</option>
            <option value="60">1 hour</option>
            <option value="480">8 hours</option>
          </select>
        </div>
      </div>
    </div>
  )

  const renderAppearanceSettings = () => (
    <div className="space-y-6">
      <div className="space-y-4">
        <h4 className="font-medium">Theme</h4>
        <div className="grid grid-cols-3 gap-4">
          {['Light', 'Dark', 'System'].map((theme) => (
            <div key={theme} className="text-center space-y-2">
              <div className="w-16 h-16 border rounded-lg mx-auto"></div>
              <p className="text-sm">{theme}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="space-y-4">
        <h4 className="font-medium">Color Scheme</h4>
        <div className="grid grid-cols-4 gap-2">
          {['Blue', 'Green', 'Purple', 'Orange'].map((color) => (
            <div key={color} className="text-center space-y-1">
              <div className="w-8 h-8 border rounded-full mx-auto"></div>
              <p className="text-xs">{color}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="space-y-4">
        <h4 className="font-medium">Display Options</h4>
        <div className="space-y-3">
          {[
            'Compact Mode',
            'Show Sidebar',
            'Show Tooltips',
            'Animate Transitions'
          ].map((option) => (
            <div key={option} className="flex items-center justify-between">
              <span className="text-sm">{option}</span>
              <input type="checkbox" defaultChecked className="rounded" />
            </div>
          ))}
        </div>
      </div>
    </div>
  )

  const renderDataSettings = () => (
    <div className="space-y-6">
      <div className="space-y-4">
        <h4 className="font-medium">Data Management</h4>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Auto Backup</p>
              <p className="text-sm text-muted-foreground">Automatically backup your data</p>
            </div>
            <input type="checkbox" defaultChecked className="rounded" />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Data Retention</p>
              <p className="text-sm text-muted-foreground">How long to keep data</p>
            </div>
            <select className="p-2 border rounded-lg">
              <option value="30">30 days</option>
              <option value="90">90 days</option>
              <option value="365">1 year</option>
              <option value="forever">Forever</option>
            </select>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <h4 className="font-medium">Export & Import</h4>
        <div className="grid grid-cols-2 gap-4">
          <Button variant="outline">
            <Database className="h-4 w-4 mr-2" />
            Export Data
          </Button>
          <Button variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Import Data
          </Button>
        </div>
      </div>
    </div>
  )

  const renderIntegrationsSettings = () => (
    <div className="space-y-6">
      <div className="space-y-4">
        <h4 className="font-medium">Connected Services</h4>
        <div className="space-y-3">
          {[
            { name: 'WhatsApp Business', status: 'connected', description: 'Messaging platform' },
            { name: 'Google Sheets', status: 'connected', description: 'Spreadsheet integration' },
            { name: 'MongoDB Atlas', status: 'connected', description: 'Database service' },
            { name: 'OpenAI API', status: 'connected', description: 'AI services' },
            { name: 'Dropbox', status: 'disconnected', description: 'File storage' }
          ].map((service) => (
            <div key={service.name} className="flex items-center justify-between p-3 border rounded-lg">
              <div>
                <p className="font-medium">{service.name}</p>
                <p className="text-sm text-muted-foreground">{service.description}</p>
              </div>
              <div className="flex items-center space-x-2">
                <Badge variant={service.status === 'connected' ? 'success' : 'secondary'}>
                  {service.status}
                </Badge>
                <Button size="sm" variant="outline">
                  {service.status === 'connected' ? 'Disconnect' : 'Connect'}
                </Button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )

  const renderTabContent = () => {
    switch (activeTab) {
      case 'general': return renderGeneralSettings()
      case 'profile': return renderProfileSettings()
      case 'notifications': return renderNotificationSettings()
      case 'security': return renderSecuritySettings()
      case 'appearance': return renderAppearanceSettings()
      case 'data': return renderDataSettings()
      case 'integrations': return renderIntegrationsSettings()
      default: return renderGeneralSettings()
    }
  }

  return (
    <div className={cn("space-y-6", className)}>
      {/* Tabs */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Settings className="h-5 w-5" />
            <span>Settings</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
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
        </CardContent>
      </Card>

      {/* Tab Content */}
      <Card>
        <CardContent className="p-6">
          {renderTabContent()}
        </CardContent>
      </Card>

      {/* Save Button */}
      <div className="flex justify-end">
        <Button
          onClick={handleSave}
          disabled={isSaving}
          className="flex items-center space-x-2"
        >
          {isSaving ? (
            <RefreshCw className="h-4 w-4 animate-spin" />
          ) : (
            <Save className="h-4 w-4" />
          )}
          <span>{isSaving ? 'Saving...' : 'Save Changes'}</span>
        </Button>
      </div>
    </div>
  )
}
