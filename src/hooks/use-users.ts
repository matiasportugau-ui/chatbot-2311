import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import type { SafeUser, CreateUserInput, UpdateUserInput } from '@/types/user'

interface UsersResponse {
  users: SafeUser[]
  total: number
}

interface CreateUserResponse {
  message: string
  user: SafeUser
}

/**
 * Fetch all users
 */
export function useUsers(options?: {
  limit?: number
  skip?: number
  role?: string
}) {
  return useQuery<UsersResponse>({
    queryKey: ['users', options],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (options?.limit) params.set('limit', options.limit.toString())
      if (options?.skip) params.set('skip', options.skip.toString())
      if (options?.role) params.set('role', options.role)

      const response = await fetch(`/api/users?${params}`)
      if (!response.ok) {
        throw new Error('Failed to fetch users')
      }
      return response.json()
    },
  })
}

/**
 * Fetch single user by ID
 */
export function useUser(id: string | null) {
  return useQuery<{ user: SafeUser }>({
    queryKey: ['user', id],
    queryFn: async () => {
      if (!id) throw new Error('User ID is required')

      const response = await fetch(`/api/users/${id}`)
      if (!response.ok) {
        throw new Error('Failed to fetch user')
      }
      return response.json()
    },
    enabled: !!id,
  })
}

/**
 * Create new user
 */
export function useCreateUser() {
  const queryClient = useQueryClient()

  return useMutation<CreateUserResponse, Error, CreateUserInput>({
    mutationFn: async (data) => {
      const response = await fetch('/api/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || 'Failed to create user')
      }

      return response.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
    },
  })
}

/**
 * Update existing user
 */
export function useUpdateUser(id: string) {
  const queryClient = useQueryClient()

  return useMutation<{ message: string; user: SafeUser }, Error, UpdateUserInput>({
    mutationFn: async (data) => {
      const response = await fetch(`/api/users/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || 'Failed to update user')
      }

      return response.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
      queryClient.invalidateQueries({ queryKey: ['user', id] })
    },
  })
}

/**
 * Delete user
 */
export function useDeleteUser() {
  const queryClient = useQueryClient()

  return useMutation<{ message: string }, Error, string>({
    mutationFn: async (id) => {
      const response = await fetch(`/api/users/${id}`, {
        method: 'DELETE',
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || 'Failed to delete user')
      }

      return response.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
    },
  })
}
