import { NextRequest, NextResponse } from 'next/server'
import {
  errorResponse,
  successResponse,
  validationErrorResponse,
} from '@/lib/api-response'
import {
  changeListingStatus,
  createListing,
  fetchSellerListings,
  getListing,
  updateListing
} from '@/lib/mercado-libre/listings'

type RouteContext = {
  params: {
    action: string
  }
}


async function getListingsHandler(request: NextRequest, context: RouteContext) {

  const action = context.params.action
  const url = new URL(request.url)

  try {
    if (action === 'list') {
      let limit = Number(url.searchParams.get('limit') || '20')
      let offset = Number(url.searchParams.get('offset') || '0')
      const status = url.searchParams.get('status') || undefined

      // Validate limit and offset to prevent NaN
      if (Number.isNaN(limit) || limit <= 0) {
        limit = 20 // Use default if invalid
      }
      if (Number.isNaN(offset) || offset < 0) {
        offset = 0 // Use default if invalid
      }

      const listings = await fetchSellerListings({ limit, offset, status })
      return successResponse(listings)
    }

    if (action === 'get') {
      const listingId = url.searchParams.get('id')

      if (!listingId) {

        return validationErrorResponse(
          ['El parámetro id es obligatorio'],
          'Missing required parameter'
        )

      }

      const listing = await getListing(listingId)
      return successResponse(listing)
    }


    return validationErrorResponse(
      [`Acción no soportada: ${action}`],
      'Invalid action'
    )
  } catch (error: unknown) {
    const errorContext = {
      action,
      method: 'GET',
      url: request.url,
      queryParams: Object.fromEntries(url.searchParams.entries()),
      error: error instanceof Error ? error.message : String(error),
      stack: error instanceof Error ? error.stack : undefined,
      details: (error as any)?.details,
    }
    
    console.error(
      `[MercadoLibre Listings] Error en GET ${action}:`,
      JSON.stringify(errorContext, null, 2)
    )
    
    const errorMessage =
      error instanceof Error ? error.message : 'Error desconocido'
    
    // Determinar código de estado apropiado
    let statusCode = 500
    if ((error as any)?.details?.error === 'invalid_grant') {
      statusCode = 401
    } else if (error instanceof Error && error.message.includes('no está conectado')) {
      statusCode = 401
    } else if (error instanceof Error && error.message.includes('obligatorio')) {
      statusCode = 400
    }
    
    return errorResponse(errorMessage, statusCode)
  }
}

export async function POST(request: NextRequest, context: RouteContext) {
  const action = context.params.action
  const body = await request.json().catch(() => ({}))

  try {
    if (action === 'create') {
      const listing = await createListing(body)
      return successResponse(listing, undefined, 201)
    }

    if (action === 'update') {
      const { id, payload } = body

      if (!id || !payload) {

        return validationErrorResponse(
          ['Se requieren los campos id y payload'],
          'Missing required fields'
        )

      }

      const listing = await updateListing(id, payload)
      return successResponse(listing)
    }

    if (action === 'status') {
      const { id, status } = body

      if (!id || !status) {

        return validationErrorResponse(
          ['Se requieren los campos id y status'],
          'Missing required fields'
        )

      }

      const listing = await changeListingStatus(id, status)
      return successResponse(listing)
    }


    return validationErrorResponse(
      [`Acción no soportada: ${action}`],
      'Invalid action'
    )
  } catch (error: unknown) {
    const errorContext = {
      action,
      method: 'POST',
      body: body,
      error: error instanceof Error ? error.message : String(error),
      stack: error instanceof Error ? error.stack : undefined,
      details: (error as any)?.details,
    }
    
    console.error(
      `[MercadoLibre Listings] Error en POST ${action}:`,
      JSON.stringify(errorContext, null, 2)
    )
    
    const errorMessage =
      error instanceof Error ? error.message : 'Error desconocido'
    
    // Determinar código de estado apropiado
    let statusCode = 500
    if ((error as any)?.details?.error === 'invalid_grant') {
      statusCode = 401
    } else if (error instanceof Error && error.message.includes('no está conectado')) {
      statusCode = 401
    } else if (error instanceof Error && error.message.includes('obligatorio') || 
               error instanceof Error && error.message.includes('requieren')) {
      statusCode = 400
    }
    
    return errorResponse(errorMessage, statusCode)
  }
}

