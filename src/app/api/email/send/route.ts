import { NextRequest, NextResponse } from 'next/server';
import { sendCustomEmail, isEmailConfigured } from '@/lib/email';

/**
 * POST /api/email/send
 * Send a custom email
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
    const { to, subject, html, text } = body;

    if (!to || !subject || !html) {
      return NextResponse.json(
        { error: 'Missing required fields: to, subject, html' },
        { status: 400 }
      );
    }

    // Send custom email
    await sendCustomEmail({
      to,
      subject,
      html,
      text,
    });

    return NextResponse.json({
      success: true,
      message: `Email sent successfully to ${to}`,
    });
  } catch (error) {
    console.error('Error sending custom email:', error);
    return NextResponse.json(
      {
        error: 'Failed to send email',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
