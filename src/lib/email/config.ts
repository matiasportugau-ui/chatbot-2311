/**
 * Email service configuration
 * Loads SMTP settings from environment variables
 */

export interface EmailConfig {
  smtp: {
    host: string;
    port: number;
    secure: boolean;
    auth: {
      user: string;
      pass: string;
    };
  };
  from: {
    name: string;
    email: string;
  };
  enabled: boolean;
}

/**
 * Gets email configuration from environment variables
 */
export function getEmailConfig(): EmailConfig {
  const smtpUser = process.env.SMTP_USER || '';
  const smtpPass = process.env.SMTP_APP_PASSWORD || '';

  return {
    smtp: {
      host: process.env.SMTP_HOST || 'smtp.gmail.com',
      port: parseInt(process.env.SMTP_PORT || '587', 10),
      secure: process.env.SMTP_SECURE === 'true', // true for 465, false for other ports
      auth: {
        user: smtpUser,
        pass: smtpPass,
      },
    },
    from: {
      name: process.env.SMTP_FROM_NAME || 'BMC Chatbot',
      email: smtpUser, // Use SMTP user as from email
    },
    enabled: !!(smtpUser && smtpPass),
  };
}

/**
 * Checks if email service is configured
 */
export function isEmailConfigured(): boolean {
  const config = getEmailConfig();
  return config.enabled;
}
