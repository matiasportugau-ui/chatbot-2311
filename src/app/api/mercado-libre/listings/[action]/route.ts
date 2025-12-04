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

<<<<<<< Updated upstream
function invalidActionResponse(action: string) {
  return NextResponse.json({ error: `Acción no soportada: ${action}` }, { status: 400 })
}

export async function GET(request: NextRequest, context: RouteContext) {
=======
async function getListingsHandler(request: NextRequest, context: RouteContext) {
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
        return NextResponse.json({ error: 'El parámetro id es obligatorio' }, { status: 400 })
=======
        return validationErrorResponse(
          ['El parámetro id es obligatorio'],
          'Missing required parameter'
        )
>>>>>>> Stashed changes
      }

      const listing = await getListing(listingId)
      return successResponse(listing)
    }

<<<<<<< Updated upstream
    return invalidActionResponse(action)
  } catch (error) {
    console.error(`Error handling Mercado Libre listings GET (${action}):`, error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Error desconocido' },
      { status: 500 }
    )
=======
    return validationErrorResponse(
      [`Acción no soportada: ${action}`],
      'Invalid action'
    )
  } catch (error: unknown) {
    console.error(
      `Error handling Mercado Libre listings GET (${action}):`,
      error
    )
    const errorMessage =
      error instanceof Error ? error.message : 'Error desconocido'
    return errorResponse(errorMessage, 500)
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
        return NextResponse.json({ error: 'Se requieren los campos id y payload' }, { status: 400 })
=======
        return validationErrorResponse(
          ['Se requieren los campos id y payload'],
          'Missing required fields'
        )
>>>>>>> Stashed changes
      }

      const listing = await updateListing(id, payload)
      return successResponse(listing)
    }

    if (action === 'status') {
      const { id, status } = body

      if (!id || !status) {
<<<<<<< Updated upstream
        return NextResponse.json({ error: 'Se requieren los campos id y status' }, { status: 400 })
=======
        return validationErrorResponse(
          ['Se requieren los campos id y status'],
          'Missing required fields'
        )
>>>>>>> Stashed changes
      }

      const listing = await changeListingStatus(id, status)
      return successResponse(listing)
    }

<<<<<<< Updated upstream
    return invalidActionResponse(action)
  } catch (error) {
    console.error(`Error handling Mercado Libre listings POST (${action}):`, error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Error desconocido' },
      { status: 500 }
    )
=======
    return validationErrorResponse(
      [`Acción no soportada: ${action}`],
      'Invalid action'
    )
  } catch (error: unknown) {
    console.error(
      `Error handling Mercado Libre listings POST (${action}):`,
      error
    )
    const errorMessage =
      error instanceof Error ? error.message : 'Error desconocido'
    return errorResponse(errorMessage, 500)
>>>>>>> Stashed changes
  }
}

