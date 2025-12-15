import { NextAuthProvider } from '@/components/providers/session-provider'
import { DashboardLayout } from '@/components/layout/dashboard-layout'

export default function CRMLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <NextAuthProvider>
      <DashboardLayout>{children}</DashboardLayout>
    </NextAuthProvider>
  )
}
