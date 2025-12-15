import { getValidAccessToken } from './client';
import { getMercadoLibreConfig } from './config';
import { connectDB } from '../mongodb';

const ORDERS_COLLECTION = 'mercado_libre_orders';

/**
 * Gets orders stored in MongoDB
 */
export async function getStoredOrders(limit: number = 20): Promise<any[]> {
    const db = await connectDB();
    const orders = await db
        .collection(ORDERS_COLLECTION)
        .find({})
        .sort({ date_created: -1 })
        .limit(limit)
        .toArray();

    return orders;
}

/**
 * Gets a summary of orders by status
 */
export async function getOrdersSummary(): Promise<any> {
    const db = await connectDB();
    const orders = await db.collection(ORDERS_COLLECTION).find({}).toArray();

    const summary = {
        total: orders.length,
        pending: 0,
        paid: 0,
        confirmed: 0,
        shipped: 0,
        delivered: 0,
        cancelled: 0,
    };

    orders.forEach((order: any) => {
        const status = order.status;
        if (status === 'paid') summary.paid++;
        else if (status === 'confirmed') summary.confirmed++;
        else if (status === 'payment_in_process') summary.pending++;
        else if (status === 'shipped') summary.shipped++;
        else if (status === 'delivered') summary.delivered++;
        else if (status === 'cancelled') summary.cancelled++;
        else summary.pending++;
    });

    return summary;
}

/**
 * Syncs seller orders from Mercado Libre API to MongoDB
 */
export async function syncSellerOrders(params: any = {}): Promise<any> {
    const config = getMercadoLibreConfig();
    const accessToken = await getValidAccessToken();

    const searchParams = new URLSearchParams({
        seller: config.sellerId,
        sort: 'date_desc',
        limit: String(params.limit || 50),
        offset: String(params.offset || 0),
    });

    const response = await fetch(
        `${config.apiBaseUrl}/orders/search?${searchParams}`,
        {
            headers: {
                'Authorization': `Bearer ${accessToken}`,
            },
        }
    );

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to fetch orders: ${response.statusText} - ${errorText}`);
    }

    const data = await response.json();
    const orders = data.results || [];

    // Store orders in MongoDB
    const db = await connectDB();
    let synced = 0;
    let updated = 0;
    let newOrders = 0;

    for (const order of orders) {
        const existing = await db.collection(ORDERS_COLLECTION).findOne({ id: order.id });

        if (existing) {
            await db.collection(ORDERS_COLLECTION).updateOne(
                { id: order.id },
                {
                    $set: {
                        ...order,
                        lastSync: new Date(),
                    },
                }
            );
            updated++;
        } else {
            await db.collection(ORDERS_COLLECTION).insertOne({
                ...order,
                lastSync: new Date(),
            });
            newOrders++;
        }
        synced++;
    }

    return {
        synced,
        updated,
        new: newOrders,
        total: data.paging?.total || 0,
    };
}

/**
 * Fetches a single order by ID and stores it in MongoDB
 */
export async function syncOrderById(orderId: number): Promise<any> {
    const config = getMercadoLibreConfig();
    const accessToken = await getValidAccessToken();

    const response = await fetch(
        `${config.apiBaseUrl}/orders/${orderId}`,
        {
            headers: {
                'Authorization': `Bearer ${accessToken}`,
            },
        }
    );

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to fetch order ${orderId}: ${response.statusText} - ${errorText}`);
    }

    const order = await response.json();

    // Store in MongoDB
    const db = await connectDB();
    await db.collection(ORDERS_COLLECTION).updateOne(
        { id: order.id },
        {
            $set: {
                ...order,
                lastSync: new Date(),
            },
        },
        { upsert: true }
    );

    return { id: orderId, synced: true, order };
}

/**
 * Acknowledges an order (marks it as seen/processed)
 */
export async function acknowledgeOrder(orderId: number): Promise<any> {
    // Note: Mercado Libre doesn't have a direct "acknowledge" endpoint
    // This is typically done by reading the order, which we already did
    // We can mark it as acknowledged in our database
    const db = await connectDB();
    await db.collection(ORDERS_COLLECTION).updateOne(
        { id: orderId },
        {
            $set: {
                acknowledged: true,
                acknowledgedAt: new Date(),
            },
        }
    );

    return { id: orderId, status: 'acknowledged' };
}

/**
 * Marks an order as ready to ship (updates shipping info)
 */
export async function markOrderReadyToShip(orderId: number, trackingNumber?: string): Promise<any> {
    const config = getMercadoLibreConfig();
    const accessToken = await getValidAccessToken();

    // First, get the shipment ID from the order
    const order = await syncOrderById(orderId);
    const shipmentId = order.order?.shipping?.id;

    if (!shipmentId) {
        throw new Error(`Order ${orderId} has no shipment associated`);
    }

    // Update shipment status
    const body: any = {
        status: 'ready_to_ship',
    };

    if (trackingNumber) {
        body.tracking_number = trackingNumber;
    }

    const response = await fetch(
        `${config.apiBaseUrl}/shipments/${shipmentId}`,
        {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(body),
        }
    );

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to update shipment ${shipmentId}: ${response.statusText} - ${errorText}`);
    }

    const shipment = await response.json();

    // Update in MongoDB
    const db = await connectDB();
    await db.collection(ORDERS_COLLECTION).updateOne(
        { id: orderId },
        {
            $set: {
                'shipping.status': 'ready_to_ship',
                'shipping.tracking_number': trackingNumber,
                readyToShip: true,
                readyToShipAt: new Date(),
            },
        }
    );

    return {
        id: orderId,
        status: 'ready_to_ship',
        tracking_number: trackingNumber,
        shipment,
    };
}
