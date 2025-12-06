import { callMercadoLibreAPI, getMercadoLibreConfig } from './client'
import { MercadoLibreListing } from './types'

export interface ListingQueryParams {
  status?: string
  limit?: number
  offset?: number
}

export interface ListingSyncResult {
  listings: MercadoLibreListing[]
  paging: {
    total: number
    limit: number
    offset: number
  }
}

const MAX_ITEMS_PER_REQUEST = 20

function chunk<T>(items: T[], size: number): T[][] {
  const chunks: T[][] = []
  for (let i = 0; i < items.length; i += size) {
    chunks.push(items.slice(i, i + size))
  }
  return chunks
}

export async function fetchSellerListings(params: ListingQueryParams = {}): Promise<ListingSyncResult> {
  const config = getMercadoLibreConfig()
  const query = {
    seller_id: config.sellerId,
    limit: String(params.limit ?? 20),
    offset: String(params.offset ?? 0),
    ...(params.status ? { status: params.status } : {})
  }

  const search = await callMercadoLibreAPI<{
    results: string[]
    paging: { total: number; limit: number; offset: number }
  }>({
    path: `/users/${config.sellerId}/items/search`,
    query
  })

  const listings: MercadoLibreListing[] = []
  const ids = search.results || []

  if (ids.length) {
    const idChunks = chunk(ids, MAX_ITEMS_PER_REQUEST)
    for (const idChunk of idChunks) {
      const detailResponse = await callMercadoLibreAPI<
        Array<{
          code: number
          body: MercadoLibreListing
        }>
      >({
        path: '/items',
        query: { ids: idChunk.join(',') }
      })

      detailResponse
        .filter((entry) => entry.code === 200 && !!entry.body)
        .forEach((entry) => listings.push(entry.body))
    }
  }

  return {
    listings,
    paging: search.paging || {
      total: listings.length,
      limit: params.limit ?? listings.length,
      offset: params.offset ?? 0
    }
  }
}

export async function getListing(listingId: string): Promise<MercadoLibreListing> {
  if (!listingId) {
    throw new Error('listingId es requerido')
  }

  return callMercadoLibreAPI<MercadoLibreListing>({
    path: `/items/${listingId}`
  })
}

export async function createListing(payload: Partial<MercadoLibreListing>) {
  if (!payload.title || !payload.price || !payload.currency_id || !payload.available_quantity) {
    throw new Error('Campos mínimos requeridos: title, price, currency_id, available_quantity')
  }

  return callMercadoLibreAPI<MercadoLibreListing>({
    method: 'POST',
    path: '/items',
    body: payload
  })
}

export async function updateListing(listingId: string, payload: Partial<MercadoLibreListing>) {
  if (!listingId) {
    throw new Error('listingId es requerido')
  }

  return callMercadoLibreAPI<MercadoLibreListing>({
    method: 'PUT',
    path: `/items/${listingId}`,
    body: payload
  })
}

export async function changeListingStatus(
  listingId: string,
  status: 'active' | 'paused' | 'closed'
) {
  if (!listingId) {
    throw new Error('listingId es requerido')
  }

  return callMercadoLibreAPI<MercadoLibreListing>({
    method: 'PUT',
    path: `/items/${listingId}`,
    body: { status }
  })
}

