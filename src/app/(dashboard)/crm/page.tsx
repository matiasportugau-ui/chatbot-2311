import { requireAuth } from '@/lib/auth/session'
import { redirect } from 'next/navigation'
import { KanbanView } from './kanban-view'

export default async function CRMDashboardPage() {
  // Protect the page - redirect to login if not authenticated
  let user
  try {
    user = await requireAuth()
  } catch {
    redirect('/login')
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground mt-2">
          Welcome back, {user.name}!
        </p>
      </div>

      <KanbanView />

      <div className="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-4">
        <h3 className="font-semibold text-purple-900 dark:text-purple-100">🎉 Phase 5 Complete!</h3>
        <p className="text-sm text-purple-800 dark:text-purple-200 mt-1">
          Kanban board with drag-and-drop functionality is now live! Try dragging quotes between columns.
        </p>
      </div>
    </div>
  )
}
