export async function fetchSellerListings(params: any): Promise<any> {
    return {
        paging: { total: 0, limit: params.limit || 20, offset: params.offset || 0 },
        results: []
    }
}

export async function getListing(id: string): Promise<any> {
    return { id, title: 'Mock Listing', price: 100, status: 'active' }
}

export async function createListing(data: any): Promise<any> {
    return { id: `MLA${Date.now()}`, ...data, status: 'active' }
}

export async function updateListing(id: string, data: any): Promise<any> {
    return { id, ...data }
}

export async function changeListingStatus(id: string, status: string): Promise<any> {
    return { id, status }
}
