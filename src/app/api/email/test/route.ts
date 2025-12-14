import { NextRequest, NextResponse } from 'next/server';
import { sendTestEmail, verifyEmailService, isEmailConfigured } from '@/lib/email';

/**
 * POST /api/email/test
 * Send a test email to verify email service configuration
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
    const { to } = body;

    if (!to) {
      return NextResponse.json({ error: 'Missing required field: to' }, { status: 400 });
    }

    // Verify connection first
    const isConnected = await verifyEmailService();
    if (!isConnected) {
      return NextResponse.json(
        {
          error: 'Email service connection failed',
          message: 'Could not connect to SMTP server. Please check your credentials.',
        },
        { status: 500 }
      );
    }

    // Send test email
    await sendTestEmail(to);

    return NextResponse.json({
      success: true,
      message: `Test email sent successfully to ${to}`,
    });
  } catch (error) {
    console.error('Error sending test email:', error);
    return NextResponse.json(
      {
        error: 'Failed to send test email',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

/**
 * GET /api/email/test
 * Check email service configuration status
 */
export async function GET() {
  try {
    const configured = isEmailConfigured();

    if (!configured) {
      return NextResponse.json({
        configured: false,
        message: 'Email service not configured',
        instructions: 'Set SMTP_USER and SMTP_APP_PASSWORD environment variables',
      });
    }

    // Verify connection
    const isConnected = await verifyEmailService();

    return NextResponse.json({
      configured: true,
      connected: isConnected,
      message: isConnected
        ? 'Email service is configured and connected'
        : 'Email service configured but connection failed',
    });
  } catch (error) {
    console.error('Error checking email configuration:', error);
    return NextResponse.json(
      {
        error: 'Failed to check email configuration',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
