import { getValidAccessToken } from './client';
import { getMercadoLibreConfig } from './config';
import { MercadoLibreListing } from './types';

interface ListingParams {
    status?: string;
    limit?: number;
    offset?: number;
}

/**
 * Fetches seller listings from Mercado Libre
 */
export async function fetchSellerListings(params: ListingParams = {}): Promise<any> {
    const config = getMercadoLibreConfig();
    const accessToken = await getValidAccessToken();

    const searchParams = new URLSearchParams({
        status: params.status || 'active',
        limit: String(params.limit || 50),
        offset: String(params.offset || 0),
    });

    const response = await fetch(
        `${config.apiBaseUrl}/users/${config.sellerId}/items/search?${searchParams}`,
        {
            headers: {
                'Authorization': `Bearer ${accessToken}`,
            },
        }
    );

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to fetch listings: ${response.statusText} - ${errorText}`);
    }

    const data = await response.json();

    // Fetch full details for each listing
    const listingIds = data.results || [];
    const listings = await Promise.all(
        listingIds.slice(0, params.limit || 50).map((id: string) => getListing(id))
    );

    return {
        paging: data.paging || { total: 0, limit: params.limit || 50, offset: params.offset || 0 },
        results: listings,
    };
}

/**
 * Gets details for a specific listing
 */
export async function getListing(id: string): Promise<MercadoLibreListing> {
    const config = getMercadoLibreConfig();
    const accessToken = await getValidAccessToken();

    const response = await fetch(
        `${config.apiBaseUrl}/items/${id}`,
        {
            headers: {
                'Authorization': `Bearer ${accessToken}`,
            },
        }
    );

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to fetch listing ${id}: ${response.statusText} - ${errorText}`);
    }

    return response.json();
}

/**
 * Creates a new listing on Mercado Libre
 */
export async function createListing(data: any): Promise<MercadoLibreListing> {
    const config = getMercadoLibreConfig();
    const accessToken = await getValidAccessToken();

    const response = await fetch(
        `${config.apiBaseUrl}/items`,
        {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        }
    );

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to create listing: ${response.statusText} - ${errorText}`);
    }

    return response.json();
}

/**
 * Updates an existing listing
 */
export async function updateListing(id: string, data: any): Promise<MercadoLibreListing> {
    const config = getMercadoLibreConfig();
    const accessToken = await getValidAccessToken();

    const response = await fetch(
        `${config.apiBaseUrl}/items/${id}`,
        {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        }
    );

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to update listing ${id}: ${response.statusText} - ${errorText}`);
    }

    return response.json();
}

/**
 * Changes the status of a listing (active, paused, closed)
 */
export async function changeListingStatus(id: string, status: string): Promise<MercadoLibreListing> {
    return updateListing(id, { status });
}
