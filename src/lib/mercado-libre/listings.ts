/**
 * Mercado Libre Listings Module
 * Handles product listing operations for Mercado Libre
 */

import { meliRequest } from './client'

interface ListingItem {
  id: string
  title: string
  price: number
  currency_id: string
  available_quantity: number
  sold_quantity: number
  status: string
  permalink: string
  thumbnail: string
  condition: string
  listing_type_id: string
  date_created: string
  last_updated: string
  attributes?: Array<{
    id: string
    name: string
    value_name: string
  }>
}

interface ListingsResponse {
  seller_id: string
  results: string[]
  paging: {
    total: number
    offset: number
    limit: number
  }
}

interface FetchListingsOptions {
  limit?: number
  offset?: number
  status?: string
}

interface CreateListingPayload {
  title: string
  price: number
  currency_id?: string
  available_quantity: number
  buying_mode?: string
  condition?: string
  listing_type_id?: string
  category_id: string
  description?: {
    plain_text: string
  }
  pictures?: Array<{ source: string }>
  attributes?: Array<{
    id: string
    value_name: string
  }>
}

/**
 * Fetch seller's listings
 */
export async function fetchSellerListings(
  options: FetchListingsOptions = {}
): Promise<{ items: ListingItem[]; paging: ListingsResponse['paging'] }> {
  const { limit = 20, offset = 0, status } = options
  const sellerId = process.env.MERCADO_LIBRE_SELLER_ID

  if (!sellerId) {
    throw new Error('MERCADO_LIBRE_SELLER_ID is not configured')
  }

  // Build query params
  const params = new URLSearchParams({
    limit: limit.toString(),
    offset: offset.toString(),
  })
  if (status) {
    params.set('status', status)
  }

  // Get listing IDs
  const response = await meliRequest<ListingsResponse>(
    `/users/${sellerId}/items/search?${params}`
  )

  if (!response.results || response.results.length === 0) {
    return {
      items: [],
      paging: response.paging,
    }
  }

  // Fetch details for each listing (in batches)
  const itemIds = response.results.slice(0, 20) // API limit
  const itemsResponse = await meliRequest<ListingItem[]>(
    `/items?ids=${itemIds.join(',')}`
  )

  return {
    items: itemsResponse,
    paging: response.paging,
  }
}

/**
 * Get a single listing by ID
 */
export async function getListing(listingId: string): Promise<ListingItem> {
  return meliRequest<ListingItem>(`/items/${listingId}`)
}

/**
 * Create a new listing
 */
export async function createListing(
  payload: CreateListingPayload
): Promise<ListingItem> {
  // Set defaults
  const listingData = {
    currency_id: 'UYU',
    buying_mode: 'buy_it_now',
    condition: 'new',
    listing_type_id: 'gold_special',
    ...payload,
  }

  return meliRequest<ListingItem>('/items', {
    method: 'POST',
    body: JSON.stringify(listingData),
  })
}

/**
 * Update an existing listing
 */
export async function updateListing(
  listingId: string,
  payload: Partial<CreateListingPayload>
): Promise<ListingItem> {
  return meliRequest<ListingItem>(`/items/${listingId}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}

/**
 * Change listing status (pause, active, closed)
 */
export async function changeListingStatus(
  listingId: string,
  status: 'paused' | 'active' | 'closed'
): Promise<ListingItem> {
  return meliRequest<ListingItem>(`/items/${listingId}`, {
    method: 'PUT',
    body: JSON.stringify({ status }),
  })
}

/**
 * Get listing description
 */
export async function getListingDescription(
  listingId: string
): Promise<{ text: string; plain_text: string }> {
  return meliRequest(`/items/${listingId}/description`)
}

/**
 * Update listing description
 */
export async function updateListingDescription(
  listingId: string,
  plainText: string
): Promise<void> {
  await meliRequest(`/items/${listingId}/description`, {
    method: 'PUT',
    body: JSON.stringify({ plain_text: plainText }),
  })
}
