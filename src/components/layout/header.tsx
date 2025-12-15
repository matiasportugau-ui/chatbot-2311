'use client'

import { Menu } from 'lucide-react'
import { UserMenu } from './user-menu'
import { Button } from '@/components/ui/button'

interface HeaderProps {
  onMenuClick?: () => void
}

export function Header({ onMenuClick }: HeaderProps) {
  return (
    <header className="sticky top-0 z-40 border-b bg-background">
      <div className="flex h-16 items-center gap-4 px-4 md:px-6">
        {/* Mobile menu button */}
        <Button
          variant="ghost"
          size="icon"
          className="md:hidden"
          onClick={onMenuClick}
        >
          <Menu className="h-5 w-5" />
          <span className="sr-only">Toggle menu</span>
        </Button>

        {/* Logo / Title */}
        <div className="flex items-center gap-2">
          <div className="hidden md:block">
            <h1 className="text-xl font-bold">CRM Dashboard</h1>
          </div>
        </div>

        {/* Spacer */}
        <div className="flex-1" />

        {/* User menu */}
        <UserMenu />
      </div>
    </header>
  )
}
