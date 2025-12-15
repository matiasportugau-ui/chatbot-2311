/**
 * Mercado Libre → CRM Integration
 * Automatically sync Mercado Libre customers and orders to CRM
 */

import {
  getOrCreateCustomer,
  createInteraction,
  updateCustomer,
  updateCustomerStats,
} from '../service';

/**
 * Process Mercado Libre order and update CRM
 * Call this from your Mercado Libre webhook handler
 */
export async function processMercadoLibreOrder(orderData: any): Promise<{
  customerId: string;
  customer: any;
}> {
  // Extract buyer information
  const buyer = orderData.buyer;
  const buyerEmail = buyer?.email;
  const buyerName = buyer?.nickname || buyer?.first_name || 'Mercado Libre Customer';

  if (!buyerEmail) {
    throw new Error('No buyer email found in order');
  }

  // 1. Get or create customer
  const customer = await getOrCreateCustomer({
    email: buyerEmail,
    name: buyerName,
    phone: buyer?.phone?.number,
    source: 'mercadolibre',
    status: 'customer', // ML order = already a customer!
    mercadoLibreUserId: buyer?.id?.toString(),
    mercadoLibreNickname: buyer?.nickname,
  });

  const customerId = customer._id!.toString();

  // 2. Log order interaction
  const orderTotal = orderData.total_amount || 0;
  const itemCount = orderData.order_items?.length || 0;
  const itemsList = orderData.order_items
    ?.map((item: any) => `${item.quantity}x ${item.item.title}`)
    .join(', ');

  await createInteraction({
    customerId,
    type: 'other',
    direction: 'inbound',
    subject: `Mercado Libre Order #${orderData.id}`,
    content: `Order placed on Mercado Libre. Total: $${orderTotal.toFixed(2)}. Items: ${itemsList || itemCount + ' items'}`,
    tags: ['mercadolibre', 'order', orderData.status],
    orderId: orderData.id.toString(),
  });

  // 3. Update customer stats
  await updateCustomerStats(customerId);

  return {
    customerId,
    customer,
  };
}

/**
 * Log Mercado Libre order status change
 */
export async function logOrderStatusChange(
  customerId: string,
  orderId: string,
  oldStatus: string,
  newStatus: string
): Promise<void> {
  const statusMessages: Record<string, string> = {
    paid: 'Payment received',
    confirmed: 'Order confirmed',
    shipped: 'Order shipped',
    delivered: 'Order delivered',
    cancelled: 'Order cancelled',
  };

  const message = statusMessages[newStatus] || `Status changed to ${newStatus}`;

  await createInteraction({
    customerId,
    type: 'other',
    subject: `Order Status Update #${orderId}`,
    content: `${message} (was: ${oldStatus})`,
    tags: ['mercadolibre', 'status-update', newStatus],
    orderId,
  });
}

/**
 * Log shipping notification sent
 */
export async function logShippingNotification(
  customerId: string,
  orderId: string,
  trackingNumber: string
): Promise<void> {
  await createInteraction({
    customerId,
    type: 'email',
    direction: 'outbound',
    subject: `Shipping Notification #${orderId}`,
    content: `Sent shipping notification with tracking number: ${trackingNumber}`,
    tags: ['mercadolibre', 'shipping', 'automated'],
    orderId,
  });
}

/**
 * Log customer message from Mercado Libre
 */
export async function logMercadoLibreMessage(
  customerId: string,
  orderId: string,
  messageContent: string,
  direction: 'inbound' | 'outbound'
): Promise<void> {
  await createInteraction({
    customerId,
    type: 'other',
    direction,
    subject: `Message via Mercado Libre #${orderId}`,
    content: messageContent,
    tags: ['mercadolibre', 'message'],
    orderId,
  });
}

/**
 * Sync all Mercado Libre orders to CRM
 * Call this to import existing orders
 */
export async function syncMercadoLibreOrders(
  orders: any[],
  options: {
    onProgress?: (processed: number, total: number) => void;
  } = {}
): Promise<{ processed: number; failed: number; errors: string[] }> {
  const results = {
    processed: 0,
    failed: 0,
    errors: [] as string[],
  };

  for (let i = 0; i < orders.length; i++) {
    try {
      await processMercadoLibreOrder(orders[i]);
      results.processed++;
      options.onProgress?.(i + 1, orders.length);
    } catch (error) {
      results.failed++;
      results.errors.push(
        `Order ${orders[i].id}: ${error instanceof Error ? error.message : 'Unknown error'}`
      );
      console.error(`Failed to sync order ${orders[i].id}:`, error);
    }
  }

  return results;
}

/**
 * Get customer by Mercado Libre user ID
 */
export async function getCustomerByMercadoLibreId(userId: string): Promise<any> {
  const { getMongoClient } = await import('@/lib/mongodb');
  const client = await getMongoClient();
  const db = client.db();

  return await db.collection('crm_customers').findOne({
    mercadoLibreUserId: userId,
  });
}
