import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import { 
  Download, 
  Upload, 
  FileText, 
  BarChart3, 
  Database, 
  Settings,
  CheckCircle,
  AlertTriangle,
  Clock
} from 'lucide-react'

interface ExportImportProps {
  className?: string
}

export function ExportImport({ className }: ExportImportProps) {
  const [isExporting, setIsExporting] = useState(false)
  const [isImporting, setIsImporting] = useState(false)
  const [exportStatus, setExportStatus] = useState<'idle' | 'success' | 'error'>('idle')
  const [importStatus, setImportStatus] = useState<'idle' | 'success' | 'error'>('idle')

  const handleExport = async (format: string) => {
    setIsExporting(true)
    setExportStatus('idle')
    
    try {
      // Simulate export process
      await new Promise(resolve => setTimeout(resolve, 2000))
      setExportStatus('success')
    } catch (error) {
      setExportStatus('error')
    } finally {
      setIsExporting(false)
    }
  }

  const handleImport = async (file: File) => {
    setIsImporting(true)
    setImportStatus('idle')
    
    try {
      // Simulate import process
      await new Promise(resolve => setTimeout(resolve, 2000))
      setImportStatus('success')
    } catch (error) {
      setImportStatus('error')
    } finally {
      setIsImporting(false)
    }
  }

  const exportFormats = [
    { name: 'Excel', format: 'xlsx', icon: BarChart3 },
    { name: 'CSV', format: 'csv', icon: FileText },
    { name: 'JSON', format: 'json', icon: Database },
    { name: 'PDF', format: 'pdf', icon: FileText }
  ]

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success': return CheckCircle
      case 'error': return AlertTriangle
      default: return Clock
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'text-green-500'
      case 'error': return 'text-red-500'
      default: return 'text-gray-500'
    }
  }

  return (
    <div className={cn("space-y-6", className)}>
      {/* Export Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Download className="h-5 w-5" />
            <span>Export Data</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Export your dashboard data in various formats for analysis and reporting.
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {exportFormats.map((format) => {
                const FormatIcon = format.icon
                
                return (
                  <div key={format.format} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <FormatIcon className="h-5 w-5" />
                      <div>
                        <p className="font-medium">{format.name}</p>
                        <p className="text-sm text-muted-foreground">.{format.format}</p>
                      </div>
                    </div>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleExport(format.format)}
                      disabled={isExporting}
                    >
                      {isExporting ? 'Exporting...' : 'Export'}
                    </Button>
                  </div>
                )
              })}
            </div>
            
            {exportStatus !== 'idle' && (
              <div className="flex items-center space-x-2 p-3 bg-muted rounded-lg">
                {React.createElement(getStatusIcon(exportStatus), {
                  className: cn("h-4 w-4", getStatusColor(exportStatus))
                })}
                <span className="text-sm">
                  {exportStatus === 'success' ? 'Export completed successfully' : 'Export failed'}
                </span>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Import Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Upload className="h-5 w-5" />
            <span>Import Data</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Import data from external sources to enhance your dashboard.
            </p>
            
            <div className="space-y-4">
              <div className="flex items-center space-x-4">
                <input
                  type="file"
                  accept=".xlsx,.csv,.json"
                  onChange={(e) => {
                    const file = e.target.files?.[0]
                    if (file) handleImport(file)
                  }}
                  className="hidden"
                  id="file-import"
                />
                <label
                  htmlFor="file-import"
                  className="flex items-center space-x-2 px-4 py-2 border rounded-lg cursor-pointer hover:bg-muted"
                >
                  <Upload className="h-4 w-4" />
                  <span>Choose File</span>
                </label>
                <span className="text-sm text-muted-foreground">
                  Supported formats: .xlsx, .csv, .json
                </span>
              </div>
              
              {importStatus !== 'idle' && (
                <div className="flex items-center space-x-2 p-3 bg-muted rounded-lg">
                  {React.createElement(getStatusIcon(importStatus), {
                    className: cn("h-4 w-4", getStatusColor(importStatus))
                  })}
                  <span className="text-sm">
                    {importStatus === 'success' ? 'Import completed successfully' : 'Import failed'}
                  </span>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Settings Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Settings className="h-5 w-5" />
            <span>Export/Import Settings</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Export Format</label>
                <select className="w-full p-2 border rounded-lg">
                  <option value="xlsx">Excel (.xlsx)</option>
                  <option value="csv">CSV (.csv)</option>
                  <option value="json">JSON (.json)</option>
                  <option value="pdf">PDF (.pdf)</option>
                </select>
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium">Date Range</label>
                <select className="w-full p-2 border rounded-lg">
                  <option value="last7days">Last 7 days</option>
                  <option value="last30days">Last 30 days</option>
                  <option value="last90days">Last 90 days</option>
                  <option value="all">All time</option>
                </select>
              </div>
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium">Include Data</label>
              <div className="space-y-2">
                {[
                  'Quote Analytics',
                  'Performance Metrics',
                  'User Feedback',
                  'System Health',
                  'AI Insights'
                ].map((item) => (
                  <label key={item} className="flex items-center space-x-2">
                    <input type="checkbox" defaultChecked className="rounded" />
                    <span className="text-sm">{item}</span>
                  </label>
                ))}
              </div>
            </div>
            
            <Button className="w-full">
              Save Settings
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
