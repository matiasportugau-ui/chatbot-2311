import { requireAuth } from '@/lib/auth/session'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { redirect } from 'next/navigation'

export default async function CRMDashboardPage() {
  // Protect the page - redirect to login if not authenticated
  let user
  try {
    user = await requireAuth()
  } catch {
    redirect('/login')
  }

  return (
    <div className="container mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">CRM Dashboard</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Welcome back, {user.name}! (Role: {user.role})
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Pending Quotes</CardTitle>
            <CardDescription>Quotes awaiting action</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">0</div>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
              No pending quotes
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Sent Quotes</CardTitle>
            <CardDescription>Quotes sent to customers</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">0</div>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
              No sent quotes
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Confirmed Orders</CardTitle>
            <CardDescription>Confirmed and processing</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">0</div>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
              No confirmed orders
            </p>
          </CardContent>
        </Card>
      </div>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Kanban Board</CardTitle>
          <CardDescription>
            Quote management board - Coming soon in Phase 5
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12 text-gray-500 dark:text-gray-400">
            <p className="text-lg font-medium">Kanban board will be implemented in Phase 5</p>
            <p className="mt-2 text-sm">
              This will include drag-and-drop functionality for managing quotes across different stages
            </p>
          </div>
        </CardContent>
      </Card>

      <div className="mt-6 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
        <h3 className="font-semibold text-blue-900 dark:text-blue-100">Phase 2 Complete!</h3>
        <p className="text-sm text-blue-800 dark:text-blue-200 mt-1">
          Authentication system is now fully functional. Next up: Dashboard layout shell and Kanban board.
        </p>
      </div>
    </div>
  )
}
