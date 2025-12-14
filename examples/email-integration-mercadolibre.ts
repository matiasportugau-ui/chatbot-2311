/**
 * Example: Integrating Email with Mercado Libre Orders
 *
 * This example shows how to automatically send email confirmations
 * when Mercado Libre orders are received via webhook or manual sync.
 */

import { sendOrderEmail } from '@/lib/email';

/**
 * Example 1: Send order confirmation when webhook is received
 *
 * Integration point: /src/app/api/mercado-libre/webhook/route.ts
 */
export async function handleMercadoLibreOrderCreated(orderData: any) {
  // Extract buyer email (from Mercado Libre order data)
  const buyerEmail = orderData.buyer?.email;

  if (!buyerEmail) {
    console.warn('No buyer email found in order:', orderData.id);
    return;
  }

  // Format order items
  const items = orderData.order_items.map((item: any) => ({
    name: item.item.title,
    quantity: item.quantity,
    price: item.unit_price * item.quantity,
  }));

  // Format shipping address
  const shippingAddress = formatMercadoLibreAddress(orderData.shipping);

  // Send order confirmation email
  try {
    await sendOrderEmail(buyerEmail, {
      customerName: orderData.buyer.nickname || orderData.buyer.first_name || 'Cliente',
      orderNumber: orderData.id.toString(),
      orderDate: new Date(orderData.date_created).toLocaleDateString('es-UY'),
      items,
      total: orderData.total_amount,
      shippingAddress,
      trackingNumber: orderData.shipping?.id || undefined,
    });

    console.log(`✅ Order confirmation email sent for order ${orderData.id}`);
  } catch (error) {
    console.error(`❌ Failed to send order email for ${orderData.id}:`, error);
  }
}

/**
 * Example 2: Send order confirmation after manual order sync
 */
export async function sendOrderEmailsAfterSync() {
  const { syncSellerOrders } = await import('@/lib/mercado-libre/orders');

  // Sync orders from Mercado Libre
  const syncResult = await syncSellerOrders({ limit: 50 });

  console.log(`Synced ${syncResult.synced} orders`);

  // Get newly synced orders from MongoDB
  const newOrders = await getNewOrdersFromDB(syncResult.new);

  // Send emails for new orders
  for (const order of newOrders) {
    if (order.buyer?.email) {
      try {
        await sendOrderEmail(order.buyer.email, {
          customerName: order.buyer.nickname || 'Cliente',
          orderNumber: order.id.toString(),
          orderDate: new Date(order.date_created).toLocaleDateString('es-UY'),
          items: order.order_items.map((item: any) => ({
            name: item.item.title,
            quantity: item.quantity,
            price: item.unit_price * item.quantity,
          })),
          total: order.total_amount,
          shippingAddress: formatMercadoLibreAddress(order.shipping),
        });

        console.log(`✅ Email sent for order ${order.id}`);

        // Rate limiting
        await new Promise((resolve) => setTimeout(resolve, 1000));
      } catch (error) {
        console.error(`❌ Failed to send email for order ${order.id}:`, error);
      }
    }
  }
}

/**
 * Example 3: Send shipping notification when order is shipped
 */
export async function sendShippingNotification(orderId: string, trackingNumber: string) {
  const { sendCustomEmail } = await import('@/lib/email');

  // Get order from MongoDB
  const order = await getOrderFromDB(orderId);

  if (!order?.buyer?.email) {
    console.warn('No buyer email for order:', orderId);
    return;
  }

  await sendCustomEmail({
    to: order.buyer.email,
    subject: `Your order ${orderId} has been shipped! 📦`,
    html: `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #dcfce7; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
          <h1 style="color: #15803d; margin: 0;">Your Order is on its way! 📦</h1>
        </div>

        <p>Dear ${order.buyer.nickname || 'Customer'},</p>

        <p>Great news! Your order <strong>#${orderId}</strong> has been shipped and is on its way to you.</p>

        <div style="background-color: #f9fafb; padding: 15px; border-radius: 6px; margin: 20px 0;">
          <p style="margin: 0;"><strong>Tracking Number:</strong> ${trackingNumber}</p>
          <p style="margin: 10px 0 0 0;"><strong>Estimated Delivery:</strong> 3-5 business days</p>
        </div>

        <div style="background-color: #eff6ff; padding: 15px; border-left: 4px solid #3b82f6; margin: 20px 0;">
          <p style="margin: 0; font-weight: bold;">Track your shipment:</p>
          <p style="margin: 10px 0 0 0;">
            You can track your shipment using the tracking number above or through Mercado Libre.
          </p>
        </div>

        <p>Thank you for your purchase!</p>
        <p>BMC Team</p>
      </div>
    `,
    text: `
Your Order is on its way! 📦

Dear ${order.buyer.nickname || 'Customer'},

Great news! Your order #${orderId} has been shipped and is on its way to you.

Tracking Number: ${trackingNumber}
Estimated Delivery: 3-5 business days

You can track your shipment using the tracking number above or through Mercado Libre.

Thank you for your purchase!
BMC Team
    `.trim(),
  });

  console.log(`✅ Shipping notification sent for order ${orderId}`);
}

/**
 * Example 4: Send delivery confirmation
 */
export async function sendDeliveryConfirmation(orderId: string) {
  const { sendCustomEmail } = await import('@/lib/email');

  const order = await getOrderFromDB(orderId);

  if (!order?.buyer?.email) {
    return;
  }

  await sendCustomEmail({
    to: order.buyer.email,
    subject: `Your order ${orderId} has been delivered! ✅`,
    html: `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #dcfce7; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
          <h1 style="color: #15803d; margin: 0;">Delivered Successfully! ✅</h1>
        </div>

        <p>Dear ${order.buyer.nickname || 'Customer'},</p>

        <p>Your order <strong>#${orderId}</strong> has been successfully delivered!</p>

        <p>We hope you're satisfied with your purchase. If you have any questions or concerns, please don't hesitate to contact us.</p>

        <div style="background-color: #fef3c7; padding: 15px; border-left: 4px solid #f59e0b; margin: 20px 0;">
          <p style="margin: 0; font-weight: bold;">Leave us a review!</p>
          <p style="margin: 10px 0 0 0;">
            Your feedback helps us improve. Please consider leaving a review on Mercado Libre.
          </p>
        </div>

        <p>Thank you for choosing us!</p>
        <p>BMC Team</p>
      </div>
    `,
    text: `
Delivered Successfully! ✅

Dear ${order.buyer.nickname || 'Customer'},

Your order #${orderId} has been successfully delivered!

We hope you're satisfied with your purchase. If you have any questions or concerns, please don't hesitate to contact us.

Leave us a review!
Your feedback helps us improve. Please consider leaving a review on Mercado Libre.

Thank you for choosing us!
BMC Team
    `.trim(),
  });

  console.log(`✅ Delivery confirmation sent for order ${orderId}`);
}

/**
 * Example 5: Integration with webhook handler
 *
 * In your webhook handler:
 * // src/app/api/mercado-libre/webhook/route.ts
 *
 * export async function POST(request: Request) {
 *   const notification = await request.json();
 *
 *   if (notification.topic === 'orders_v2') {
 *     // Get order details from Mercado Libre API
 *     const order = await fetchOrderFromMercadoLibre(notification.resource);
 *
 *     // Process order status
 *     if (order.status === 'paid') {
 *       // Send order confirmation email
 *       handleMercadoLibreOrderCreated(order).catch(console.error);
 *     } else if (order.status === 'shipped') {
 *       // Send shipping notification
 *       sendShippingNotification(
 *         order.id,
 *         order.shipping.id
 *       ).catch(console.error);
 *     } else if (order.status === 'delivered') {
 *       // Send delivery confirmation
 *       sendDeliveryConfirmation(order.id).catch(console.error);
 *     }
 *   }
 *
 *   return new Response('OK', { status: 200 });
 * }
 */

/**
 * Helper: Format Mercado Libre shipping address
 */
function formatMercadoLibreAddress(shipping: any): string | undefined {
  if (!shipping?.receiver_address) {
    return undefined;
  }

  const addr = shipping.receiver_address;
  const parts = [
    addr.street_name,
    addr.street_number,
    addr.floor ? `Piso ${addr.floor}` : null,
    addr.apartment ? `Apto ${addr.apartment}` : null,
    addr.city?.name,
    addr.state?.name,
    addr.zip_code,
  ].filter(Boolean);

  return parts.join(', ');
}

/**
 * Helper: Get order from MongoDB (stub - implement based on your schema)
 */
async function getOrderFromDB(orderId: string): Promise<any> {
  const { getMongoClient } = await import('@/lib/mongodb');
  const client = await getMongoClient();
  const db = client.db();

  return await db.collection('mercado_libre_orders').findOne({
    id: parseInt(orderId),
  });
}

/**
 * Helper: Get new orders from MongoDB (stub)
 */
async function getNewOrdersFromDB(count: number): Promise<any[]> {
  const { getMongoClient } = await import('@/lib/mongodb');
  const client = await getMongoClient();
  const db = client.db();

  return await db
    .collection('mercado_libre_orders')
    .find({})
    .sort({ date_created: -1 })
    .limit(count)
    .toArray();
}
