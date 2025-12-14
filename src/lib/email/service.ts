/**
 * Email service using Nodemailer
 * Sends transactional emails for quotes, orders, and notifications
 */

import nodemailer, { Transporter } from 'nodemailer';
import { getEmailConfig } from './config';
import {
  generateQuoteEmail,
  generateQuoteTextEmail,
  generateOrderEmail,
  generateOrderTextEmail,
  QuoteEmailData,
  OrderEmailData,
} from './templates';

let transporter: Transporter | null = null;

/**
 * Initialize email transporter
 */
function getTransporter(): Transporter {
  if (transporter) {
    return transporter;
  }

  const config = getEmailConfig();

  if (!config.enabled) {
    throw new Error('Email service is not configured. Please set SMTP_USER and SMTP_APP_PASSWORD environment variables.');
  }

  transporter = nodemailer.createTransport({
    host: config.smtp.host,
    port: config.smtp.port,
    secure: config.smtp.secure,
    auth: {
      user: config.smtp.auth.user,
      pass: config.smtp.auth.pass,
    },
  });

  return transporter;
}

/**
 * Send a test email to verify configuration
 */
export async function sendTestEmail(to: string): Promise<void> {
  const config = getEmailConfig();
  const transporter = getTransporter();

  await transporter.sendMail({
    from: `"${config.from.name}" <${config.from.email}>`,
    to,
    subject: 'BMC Email Service - Test Email',
    html: `
      <div style="font-family: Arial, sans-serif; padding: 20px; max-width: 600px; margin: 0 auto;">
        <h1 style="color: #059669;">Email Service Active! ✅</h1>
        <p>This is a test email from your BMC Chatbot system.</p>
        <p>If you're receiving this, your email configuration is working correctly.</p>
        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
        <p style="color: #6b7280; font-size: 14px;">
          SMTP Host: ${config.smtp.host}<br>
          From: ${config.from.name} &lt;${config.from.email}&gt;
        </p>
      </div>
    `,
    text: `
BMC Email Service - Test Email

Email Service Active! ✅

This is a test email from your BMC Chatbot system.
If you're receiving this, your email configuration is working correctly.

---
SMTP Host: ${config.smtp.host}
From: ${config.from.name} <${config.from.email}>
    `.trim(),
  });
}

/**
 * Send quote confirmation email
 */
export async function sendQuoteEmail(to: string, data: QuoteEmailData): Promise<void> {
  const config = getEmailConfig();
  const transporter = getTransporter();

  await transporter.sendMail({
    from: `"${config.from.name}" <${config.from.email}>`,
    to,
    subject: `Quote Confirmation - #${data.quoteNumber}`,
    html: generateQuoteEmail(data),
    text: generateQuoteTextEmail(data),
  });
}

/**
 * Send order confirmation email
 */
export async function sendOrderEmail(to: string, data: OrderEmailData): Promise<void> {
  const config = getEmailConfig();
  const transporter = getTransporter();

  await transporter.sendMail({
    from: `"${config.from.name}" <${config.from.email}>`,
    to,
    subject: `Order Confirmation - #${data.orderNumber}`,
    html: generateOrderEmail(data),
    text: generateOrderTextEmail(data),
  });
}

/**
 * Send custom email
 */
export async function sendCustomEmail(options: {
  to: string;
  subject: string;
  html: string;
  text?: string;
}): Promise<void> {
  const config = getEmailConfig();
  const transporter = getTransporter();

  await transporter.sendMail({
    from: `"${config.from.name}" <${config.from.email}>`,
    to: options.to,
    subject: options.subject,
    html: options.html,
    text: options.text || options.html.replace(/<[^>]*>/g, ''), // Strip HTML if no text provided
  });
}

/**
 * Verify email service connection
 */
export async function verifyEmailService(): Promise<boolean> {
  try {
    const transporter = getTransporter();
    await transporter.verify();
    return true;
  } catch (error) {
    console.error('Email service verification failed:', error);
    return false;
  }
}
