import React from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import { 
  Heart, 
  Github, 
  Twitter, 
  Linkedin, 
  Mail, 
  Phone,
  MapPin,
  Clock,
  Shield,
  CheckCircle
} from 'lucide-react'

interface FooterProps {
  className?: string
}

export function Footer({ className }: FooterProps) {
  const currentYear = new Date().getFullYear()

  const socialLinks = [
    { name: 'GitHub', icon: Github, href: '#' },
    { name: 'Twitter', icon: Twitter, href: '#' },
    { name: 'LinkedIn', icon: Linkedin, href: '#' }
  ]

  const quickLinks = [
    { name: 'Documentation', href: '#' },
    { name: 'API Reference', href: '#' },
    { name: 'Support', href: '#' },
    { name: 'Privacy Policy', href: '#' },
    { name: 'Terms of Service', href: '#' }
  ]

  const systemInfo = [
    { label: 'Version', value: 'v1.0.0' },
    { label: 'Last Updated', value: '2 hours ago' },
    { label: 'Uptime', value: '99.9%' },
    { label: 'Status', value: 'Operational' }
  ]

  return (
    <Card className={className}>
      <CardContent className="p-6">
        <div className="space-y-6">
          {/* Main Footer Content */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {/* Company Info */}
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                  <span className="text-primary-foreground font-bold text-sm">B</span>
                </div>
                <div>
                  <h3 className="font-bold">BMC Dashboard</h3>
                  <p className="text-sm text-muted-foreground">WhatsApp Quoting System</p>
                </div>
              </div>
              <p className="text-sm text-muted-foreground">
                Automated conversational quoting system powered by AI and n8n workflows.
              </p>
              <div className="flex space-x-2">
                {socialLinks.map((link) => (
                  <Button key={link.name} variant="outline" size="sm">
                    <link.icon className="h-4 w-4" />
                  </Button>
                ))}
              </div>
            </div>

            {/* Quick Links */}
            <div className="space-y-4">
              <h4 className="font-medium">Quick Links</h4>
              <div className="space-y-2">
                {quickLinks.map((link) => (
                  <a
                    key={link.name}
                    href={link.href}
                    className="block text-sm text-muted-foreground hover:text-foreground transition-colors"
                  >
                    {link.name}
                  </a>
                ))}
              </div>
            </div>

            {/* Contact Info */}
            <div className="space-y-4">
              <h4 className="font-medium">Contact</h4>
              <div className="space-y-2">
                <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                  <Mail className="h-4 w-4" />
                  <span>support@bmc.com</span>
                </div>
                <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                  <Phone className="h-4 w-4" />
                  <span>+598 99 123 456</span>
                </div>
                <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                  <MapPin className="h-4 w-4" />
                  <span>Montevideo, Uruguay</span>
                </div>
              </div>
            </div>

            {/* System Status */}
            <div className="space-y-4">
              <h4 className="font-medium">System Status</h4>
              <div className="space-y-2">
                {systemInfo.map((info) => (
                  <div key={info.label} className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">{info.label}</span>
                    <div className="flex items-center space-x-1">
                      {info.label === 'Status' && (
                        <CheckCircle className="h-3 w-3 text-green-500" />
                      )}
                      <span className="font-medium">{info.value}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Bottom Bar */}
          <div className="border-t pt-4">
            <div className="flex flex-col md:flex-row items-center justify-between space-y-2 md:space-y-0">
              <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                <span>© {currentYear} BMC Dashboard. Made with</span>
                <Heart className="h-4 w-4 text-red-500" />
                <span>in Uruguay</span>
              </div>
              <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                <div className="flex items-center space-x-1">
                  <Shield className="h-4 w-4" />
                  <span>Secure</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Clock className="h-4 w-4" />
                  <span>24/7</span>
                </div>
                <div className="flex items-center space-x-1">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span>Operational</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
