import { NextRequest, NextResponse } from 'next/server';
import { sendOrderEmail, isEmailConfigured, OrderEmailData } from '@/lib/email';

/**
 * POST /api/email/order
 * Send an order confirmation email to a customer
 */
export async function POST(request: NextRequest) {
  try {
    if (!isEmailConfigured()) {
      return NextResponse.json(
        {
          error: 'Email service not configured',
          message: 'Please set SMTP_USER and SMTP_APP_PASSWORD environment variables',
        },
        { status: 400 }
      );
    }

    const body = await request.json();
    const { to, data } = body;

    if (!to || !data) {
      return NextResponse.json(
        { error: 'Missing required fields: to, data' },
        { status: 400 }
      );
    }

    // Validate order data
    const requiredFields = ['customerName', 'orderNumber', 'orderDate', 'items', 'total'];
    const missingFields = requiredFields.filter((field) => !(field in data));

    if (missingFields.length > 0) {
      return NextResponse.json(
        {
          error: 'Invalid order data',
          message: `Missing required fields: ${missingFields.join(', ')}`,
        },
        { status: 400 }
      );
    }

    // Send order email
    await sendOrderEmail(to, data as OrderEmailData);

    return NextResponse.json({
      success: true,
      message: `Order email sent successfully to ${to}`,
      orderNumber: data.orderNumber,
    });
  } catch (error) {
    console.error('Error sending order email:', error);
    return NextResponse.json(
      {
        error: 'Failed to send order email',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
