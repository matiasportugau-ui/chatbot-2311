'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import { 
  Search, 
  Filter, 
  Calendar, 
  User, 
  Tag, 
  X,
  ChevronDown,
  ChevronUp
} from 'lucide-react'

interface FilterOption {
  value: string
  label: string
  count?: number
}

interface SearchFiltersProps {
  onSearch: (query: string) => void
  onFilterChange: (filters: Record<string, any>) => void
  className?: string
}

export function SearchFilters({ onSearch, onFilterChange, className }: SearchFiltersProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [filters, setFilters] = useState<Record<string, any>>({})
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({})

  const filterSections = {
    dateRange: {
      title: 'Date Range',
      icon: Calendar,
      options: [
        { value: 'today', label: 'Today' },
        { value: 'yesterday', label: 'Yesterday' },
        { value: 'last7days', label: 'Last 7 days' },
        { value: 'last30days', label: 'Last 30 days' },
        { value: 'last90days', label: 'Last 90 days' },
        { value: 'custom', label: 'Custom range' }
      ]
    },
    category: {
      title: 'Category',
      icon: Tag,
      options: [
        { value: 'quotes', label: 'Quotes', count: 45 },
        { value: 'users', label: 'Users', count: 23 },
        { value: 'system', label: 'System', count: 12 },
        { value: 'ai', label: 'AI Insights', count: 8 }
      ]
    },
    status: {
      title: 'Status',
      icon: Filter,
      options: [
        { value: 'active', label: 'Active', count: 32 },
        { value: 'pending', label: 'Pending', count: 15 },
        { value: 'completed', label: 'Completed', count: 28 },
        { value: 'failed', label: 'Failed', count: 3 }
      ]
    },
    user: {
      title: 'User',
      icon: User,
      options: [
        { value: 'all', label: 'All Users' },
        { value: 'admin', label: 'Administrators' },
        { value: 'user', label: 'Regular Users' },
        { value: 'guest', label: 'Guest Users' }
      ]
    }
  }

  const handleSearch = (query: string) => {
    setSearchQuery(query)
    onSearch(query)
  }

  const handleFilterChange = (section: string, value: string) => {
    const newFilters = { ...filters }
    if (newFilters[section] === value) {
      delete newFilters[section]
    } else {
      newFilters[section] = value
    }
    setFilters(newFilters)
    onFilterChange(newFilters)
  }

  const clearAllFilters = () => {
    setFilters({})
    onFilterChange({})
  }

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  const getActiveFiltersCount = () => {
    return Object.keys(filters).length
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Search className="h-5 w-5" />
            <span>Search & Filters</span>
            {getActiveFiltersCount() > 0 && (
              <Badge variant="secondary">{getActiveFiltersCount()}</Badge>
            )}
          </div>
          {getActiveFiltersCount() > 0 && (
            <Button
              size="sm"
              variant="outline"
              onClick={clearAllFilters}
            >
              Clear All
            </Button>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Search Input */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search..."
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          {/* Filter Sections */}
          {Object.entries(filterSections).map(([sectionKey, section]) => {
            const SectionIcon = section.icon
            const isExpanded = expandedSections[sectionKey]
            
            return (
              <div key={sectionKey} className="space-y-2">
                <Button
                  variant="ghost"
                  className="w-full justify-between p-2 h-auto"
                  onClick={() => toggleSection(sectionKey)}
                >
                  <div className="flex items-center space-x-2">
                    <SectionIcon className="h-4 w-4" />
                    <span>{section.title}</span>
                    {filters[sectionKey] && (
                      <Badge variant="secondary" className="ml-2">
                        {section.options.find(opt => opt.value === filters[sectionKey])?.label}
                      </Badge>
                    )}
                  </div>
                  {isExpanded ? (
                    <ChevronUp className="h-4 w-4" />
                  ) : (
                    <ChevronDown className="h-4 w-4" />
                  )}
                </Button>

                {isExpanded && (
                  <div className="space-y-1 pl-6">
                    {section.options.map((option) => (
                      <div
                        key={option.value}
                        className="flex items-center justify-between p-2 rounded hover:bg-muted cursor-pointer"
                        onClick={() => handleFilterChange(sectionKey, option.value)}
                      >
                        <div className="flex items-center space-x-2">
                          <input
                            type="radio"
                            name={sectionKey}
                            value={option.value}
                            checked={filters[sectionKey] === option.value}
                            onChange={() => handleFilterChange(sectionKey, option.value)}
                            className="rounded"
                          />
                          <span className="text-sm">{option.label}</span>
                        </div>
                        {'count' in option && option.count && (
                          <Badge variant="outline" className="text-xs">
                            {option.count}
                          </Badge>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )
          })}

          {/* Active Filters */}
          {getActiveFiltersCount() > 0 && (
            <div className="space-y-2">
              <h4 className="text-sm font-medium">Active Filters</h4>
              <div className="flex flex-wrap gap-2">
                {Object.entries(filters).map(([section, value]) => {
                  const sectionConfig = filterSections[section as keyof typeof filterSections]
                  const option = sectionConfig.options.find(opt => opt.value === value)
                  
                  return (
                    <Badge
                      key={`${section}-${value}`}
                      variant="secondary"
                      className="flex items-center space-x-1"
                    >
                      <span>{sectionConfig.title}: {option?.label}</span>
                      <X
                        className="h-3 w-3 cursor-pointer"
                        onClick={() => handleFilterChange(section, value)}
                      />
                    </Badge>
                  )
                })}
              </div>
            </div>
          )}

          {/* Quick Actions */}
          <div className="space-y-2">
            <h4 className="text-sm font-medium">Quick Actions</h4>
            <div className="grid grid-cols-2 gap-2">
              <Button
                size="sm"
                variant="outline"
                onClick={() => {
                  setFilters({ dateRange: 'last7days' })
                  onFilterChange({ dateRange: 'last7days' })
                }}
              >
                Last 7 days
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => {
                  setFilters({ status: 'active' })
                  onFilterChange({ status: 'active' })
                }}
              >
                Active only
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
