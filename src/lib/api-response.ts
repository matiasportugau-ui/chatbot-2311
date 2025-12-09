/**
 * API Response Helper Functions
 * Standardized response format for all API endpoints
 */

import { ErrorResponse, SuccessResponse } from '@/types/api'
import { NextResponse } from 'next/server'

/**
 * Create a success response
 */
export function successResponse<T>(
  data: T,
  message?: string,
  status: number = 200
): NextResponse<SuccessResponse<T>> {
  const response: SuccessResponse<T> = {
    success: true,
    data,
  }

  if (message) {
    response.message = message
  }

  return NextResponse.json(response, { status })
}

/**
 * Create an error response
 */
export function errorResponse(
  error: string,
  status: number = 500,
  message?: string
): NextResponse<ErrorResponse> {
  const response: ErrorResponse = {
    success: false,
    error,
  }

  if (message) {
    response.message = message
  }

  return NextResponse.json(response, { status })
}

/**
 * Create a paginated response
 */
export function paginatedResponse<T>(
  data: T[],
  page: number,
  total: number,
  limit: number,
  message?: string
): NextResponse<
  SuccessResponse<{
    items: T[]
    pagination: {
      page: number
      limit: number
      total: number
      totalPages: number
    }
  }>
> {
  // Validate limit to prevent NaN and division by zero
  if (Number.isNaN(limit) || limit <= 0) {
    throw new Error('Limit must be a valid number greater than zero')
  }

  const totalPages = Math.ceil(total / limit)

  return successResponse(
    {
      items: data,
      pagination: {
        page,
        limit,
        total,
        totalPages,
      },
    },
    message
  )
}

/**
 * Create a validation error response
 */
export function validationErrorResponse(
  errors: string[],
  message?: string
): NextResponse<ErrorResponse> {
  return errorResponse(
    `Validation failed: ${errors.join(', ')}`,
    400,
    message || 'Please check your input and try again'
  )
}

/**
 * Create a not found response
 */
export function notFoundResponse(
  resource: string = 'Resource'
): NextResponse<ErrorResponse> {
  return errorResponse(
    `${resource} not found`,
    404,
    `The requested ${resource.toLowerCase()} could not be found`
  )
}

/**
 * Create an unauthorized response
 */
export function unauthorizedResponse(
  message: string = 'Unauthorized'
): NextResponse<ErrorResponse> {
  return errorResponse(message, 401, 'Authentication required')
}

/**
 * Create a forbidden response
 */
export function forbiddenResponse(
  message: string = 'Forbidden'
): NextResponse<ErrorResponse> {
  return errorResponse(
    message,
    403,
    'You do not have permission to access this resource'
  )
}
