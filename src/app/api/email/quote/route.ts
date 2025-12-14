import { NextRequest, NextResponse } from 'next/server';
import { sendQuoteEmail, isEmailConfigured, QuoteEmailData } from '@/lib/email';

/**
 * POST /api/email/quote
 * Send a quote confirmation email to a customer
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

    // Validate quote data
    const requiredFields = ['customerName', 'quoteNumber', 'items', 'subtotal', 'iva', 'total'];
    const missingFields = requiredFields.filter((field) => !(field in data));

    if (missingFields.length > 0) {
      return NextResponse.json(
        {
          error: 'Invalid quote data',
          message: `Missing required fields: ${missingFields.join(', ')}`,
        },
        { status: 400 }
      );
    }

    // Send quote email
    await sendQuoteEmail(to, data as QuoteEmailData);

    return NextResponse.json({
      success: true,
      message: `Quote email sent successfully to ${to}`,
      quoteNumber: data.quoteNumber,
    });
  } catch (error) {
    console.error('Error sending quote email:', error);
    return NextResponse.json(
      {
        error: 'Failed to send quote email',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
