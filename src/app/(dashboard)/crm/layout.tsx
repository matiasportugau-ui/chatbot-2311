import { NextAuthProvider } from '@/components/providers/session-provider'
import { QueryProvider } from '@/components/providers/query-provider'
import { DashboardLayout } from '@/components/layout/dashboard-layout'

export default function CRMLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <NextAuthProvider>
      <QueryProvider>
        <DashboardLayout>{children}</DashboardLayout>
      </QueryProvider>
    </NextAuthProvider>
  )
}
