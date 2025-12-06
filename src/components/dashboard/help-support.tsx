import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import { 
  HelpCircle, 
  BookOpen, 
  MessageSquare, 
  Phone, 
  Mail, 
  ExternalLink,
  ChevronRight,
  Search,
  Star,
  Clock,
  User
} from 'lucide-react'

interface HelpArticle {
  id: string
  title: string
  description: string
  category: string
  difficulty: 'beginner' | 'intermediate' | 'advanced'
  readTime: number
  rating: number
  tags: string[]
}

interface HelpSupportProps {
  className?: string
}

export function HelpSupport({ className }: HelpSupportProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')

  const helpArticles: HelpArticle[] = [
    {
      id: '1',
      title: 'Getting Started with the Dashboard',
      description: 'Learn how to navigate and use the main dashboard features.',
      category: 'Getting Started',
      difficulty: 'beginner',
      readTime: 5,
      rating: 4.8,
      tags: ['dashboard', 'navigation', 'basics']
    },
    {
      id: '2',
      title: 'Understanding Quote Analytics',
      description: 'Deep dive into quote analytics and how to interpret the data.',
      category: 'Analytics',
      difficulty: 'intermediate',
      readTime: 8,
      rating: 4.6,
      tags: ['analytics', 'quotes', 'data']
    },
    {
      id: '3',
      title: 'Setting Up AI Insights',
      description: 'Configure and customize AI insights for your business.',
      category: 'AI Features',
      difficulty: 'advanced',
      readTime: 12,
      rating: 4.9,
      tags: ['ai', 'insights', 'configuration']
    },
    {
      id: '4',
      title: 'Troubleshooting Common Issues',
      description: 'Solutions to common problems and error messages.',
      category: 'Troubleshooting',
      difficulty: 'intermediate',
      readTime: 6,
      rating: 4.7,
      tags: ['troubleshooting', 'errors', 'solutions']
    }
  ]

  const categories = [
    'Getting Started',
    'Analytics',
    'AI Features',
    'Troubleshooting',
    'API Documentation',
    'Integrations'
  ]

  const difficultyColors = {
    beginner: 'success',
    intermediate: 'warning',
    advanced: 'destructive'
  } as const

  const filteredArticles = helpArticles.filter(article => {
    const matchesSearch = article.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         article.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         article.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
    const matchesCategory = selectedCategory === 'all' || article.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'text-green-500'
      case 'intermediate': return 'text-yellow-500'
      case 'advanced': return 'text-red-500'
      default: return 'text-gray-500'
    }
  }

  return (
    <div className={cn("space-y-6", className)}>
      {/* Search and Categories */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <HelpCircle className="h-5 w-5" />
            <span>Help & Support</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search help articles..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>

            {/* Categories */}
            <div className="flex flex-wrap gap-2">
              <Button
                variant={selectedCategory === 'all' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSelectedCategory('all')}
              >
                All
              </Button>
              {categories.map((category) => (
                <Button
                  key={category}
                  variant={selectedCategory === category ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedCategory(category)}
                >
                  {category}
                </Button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Help Articles */}
      <div className="space-y-4">
        {filteredArticles.map((article) => (
          <Card key={article.id} className="p-4">
            <div className="space-y-3">
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <h3 className="font-medium">{article.title}</h3>
                  <p className="text-sm text-muted-foreground">{article.description}</p>
                </div>
                <div className="flex items-center space-x-1">
                  <Star className="h-4 w-4 text-yellow-400" />
                  <span className="text-sm">{article.rating}</span>
                </div>
              </div>

              <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                <div className="flex items-center space-x-1">
                  <Clock className="h-4 w-4" />
                  <span>{article.readTime} min read</span>
                </div>
                <Badge variant={difficultyColors[article.difficulty]}>
                  {article.difficulty.toUpperCase()}
                </Badge>
                <span>{article.category}</span>
              </div>

              <div className="flex flex-wrap gap-1">
                {article.tags.map((tag) => (
                  <Badge key={tag} variant="outline" className="text-xs">
                    {tag}
                  </Badge>
                ))}
              </div>

              <div className="flex items-center space-x-2">
                <Button size="sm" variant="outline">
                  Read Article
                </Button>
                <Button size="sm" variant="outline">
                  <ExternalLink className="h-4 w-4 mr-1" />
                  Open in New Tab
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Contact Support */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <MessageSquare className="h-5 w-5" />
            <span>Contact Support</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center space-y-2">
              <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mx-auto">
                <MessageSquare className="h-6 w-6 text-primary" />
              </div>
              <h4 className="font-medium">Live Chat</h4>
              <p className="text-sm text-muted-foreground">Get instant help from our support team</p>
              <Button size="sm" className="w-full">
                Start Chat
              </Button>
            </div>

            <div className="text-center space-y-2">
              <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mx-auto">
                <Mail className="h-6 w-6 text-primary" />
              </div>
              <h4 className="font-medium">Email Support</h4>
              <p className="text-sm text-muted-foreground">Send us a detailed message</p>
              <Button size="sm" variant="outline" className="w-full">
                Send Email
              </Button>
            </div>

            <div className="text-center space-y-2">
              <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mx-auto">
                <Phone className="h-6 w-6 text-primary" />
              </div>
              <h4 className="font-medium">Phone Support</h4>
              <p className="text-sm text-muted-foreground">Call us for urgent issues</p>
              <Button size="sm" variant="outline" className="w-full">
                Call Now
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Documentation */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <BookOpen className="h-5 w-5" />
            <span>Documentation</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <h4 className="font-medium">API Documentation</h4>
              <p className="text-sm text-muted-foreground">
                Complete API reference and integration guides
              </p>
              <Button size="sm" variant="outline" className="w-full">
                <ExternalLink className="h-4 w-4 mr-1" />
                View API Docs
              </Button>
            </div>

            <div className="space-y-2">
              <h4 className="font-medium">User Guide</h4>
              <p className="text-sm text-muted-foreground">
                Step-by-step guides for all features
              </p>
              <Button size="sm" variant="outline" className="w-full">
                <ExternalLink className="h-4 w-4 mr-1" />
                View User Guide
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
