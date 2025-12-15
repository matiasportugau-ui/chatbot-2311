import { MercadoLibreConfig } from './types';

/**
 * Loads and validates Mercado Libre configuration from environment variables
 */
export function getMercadoLibreConfig(): MercadoLibreConfig {
  const config: MercadoLibreConfig = {
    appId: process.env.MERCADO_LIBRE_APP_ID || process.env.MELI_APP_ID || '',
    clientSecret: process.env.MERCADO_LIBRE_CLIENT_SECRET || process.env.MELI_CLIENT_SECRET || '',
    redirectUri: process.env.MERCADO_LIBRE_REDIRECT_URI || process.env.MELI_REDIRECT_URI || '',
    sellerId: process.env.MERCADO_LIBRE_SELLER_ID || process.env.MELI_SELLER_ID || '',
    webhookSecret: process.env.MERCADO_LIBRE_WEBHOOK_SECRET || '',
    authBaseUrl: process.env.MERCADO_LIBRE_AUTH_URL || 'https://auth.mercadolibre.com.uy',
    apiBaseUrl: process.env.MERCADO_LIBRE_API_URL || 'https://api.mercadolibre.com',
    scopes: (process.env.MERCADO_LIBRE_SCOPES || 'read write offline_access').split(' '),
    pkceEnabled: process.env.MERCADO_LIBRE_PKCE_ENABLED !== 'false',
  };

  return config;
}

/**
 * Checks if the Mercado Libre integration is properly configured
 */
export function isConfigured(): boolean {
  const config = getMercadoLibreConfig();
  return !!(
    config.appId &&
    config.clientSecret &&
    config.redirectUri &&
    config.sellerId
  );
}
