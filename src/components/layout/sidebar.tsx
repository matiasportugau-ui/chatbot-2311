'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  LayoutDashboard,
  Users,
  BarChart3,
  Settings,
  FileText,
  Package
} from 'lucide-react'
import { cn } from '@/lib/utils'

const navigation = [
  {
    name: 'Dashboard',
    href: '/crm',
    icon: LayoutDashboard,
  },
  {
    name: 'Customers',
    href: '/crm/customers',
    icon: Users,
  },
  {
    name: 'Quotes',
    href: '/crm/quotes',
    icon: FileText,
  },
  {
    name: 'Products',
    href: '/crm/products',
    icon: Package,
  },
  {
    name: 'Analytics',
    href: '/crm/analytics',
    icon: BarChart3,
  },
  {
    name: 'Settings',
    href: '/crm/settings',
    icon: Settings,
  },
]

interface SidebarProps {
  className?: string
}

export function Sidebar({ className }: SidebarProps) {
  const pathname = usePathname()

  return (
    <div className={cn('flex h-full flex-col gap-2', className)}>
      <div className="flex h-16 items-center border-b px-6">
        <Link href="/crm" className="flex items-center gap-2 font-semibold">
          <LayoutDashboard className="h-6 w-6" />
          <span className="text-lg">CRM</span>
        </Link>
      </div>
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navigation.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
              )}
            >
              <item.icon className="h-5 w-5" />
              {item.name}
            </Link>
          )
        })}
      </nav>
      <div className="border-t p-4">
        <div className="text-xs text-muted-foreground">
          CRM Dashboard v1.0
        </div>
      </div>
    </div>
  )
}
