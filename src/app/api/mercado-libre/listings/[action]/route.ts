import { NextRequest, NextResponse } from 'next/server'
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

function invalidActionResponse(action: string) {
  return NextResponse.json({ error: `Acción no soportada: ${action}` }, { status: 400 })
}

export async function GET(request: NextRequest, context: RouteContext) {
  const action = context.params.action
  const url = new URL(request.url)

  try {
    if (action === 'list') {
      const limit = Number(url.searchParams.get('limit') || '20')
      const offset = Number(url.searchParams.get('offset') || '0')
      const status = url.searchParams.get('status') || undefined

      const listings = await fetchSellerListings({ limit, offset, status })
      return NextResponse.json(listings)
    }

    if (action === 'get') {
      const listingId = url.searchParams.get('id')

      if (!listingId) {
        return NextResponse.json({ error: 'El parámetro id es obligatorio' }, { status: 400 })
      }

      const listing = await getListing(listingId)
      return NextResponse.json(listing)
    }

    return invalidActionResponse(action)
  } catch (error) {
    console.error(`Error handling Mercado Libre listings GET (${action}):`, error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Error desconocido' },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest, context: RouteContext) {
  const action = context.params.action
  const body = await request.json().catch(() => ({}))

  try {
    if (action === 'create') {
      const listing = await createListing(body)
      return NextResponse.json(listing, { status: 201 })
    }

    if (action === 'update') {
      const { id, payload } = body

      if (!id || !payload) {
        return NextResponse.json({ error: 'Se requieren los campos id y payload' }, { status: 400 })
      }

      const listing = await updateListing(id, payload)
      return NextResponse.json(listing)
    }

    if (action === 'status') {
      const { id, status } = body

      if (!id || !status) {
        return NextResponse.json({ error: 'Se requieren los campos id y status' }, { status: 400 })
      }

      const listing = await changeListingStatus(id, status)
      return NextResponse.json(listing)
    }

    return invalidActionResponse(action)
  } catch (error) {
    console.error(`Error handling Mercado Libre listings POST (${action}):`, error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Error desconocido' },
      { status: 500 }
    )
  }
}

