export async function getStoredOrders(limit: number = 20): Promise<any[]> {
    return []
}

export async function getOrdersSummary(): Promise<any> {
    return { total: 0, pending: 0, shipped: 0, delivered: 0, cancelled: 0 }
}

export async function syncSellerOrders(params: any): Promise<any> {
    return { synced: 0, updated: 0, new: 0 }
}

export async function acknowledgeOrder(orderId: number): Promise<any> {
    return { id: orderId, status: 'processed' }
}

export async function markOrderReadyToShip(orderId: number, trackingNumber?: string): Promise<any> {
    return { id: orderId, status: 'ready_to_ship', tracking_number: trackingNumber }
}
