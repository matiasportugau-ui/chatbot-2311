#!/usr/bin/env node
/**
 * Helper script to generate Mercado Libre OAuth authorization URL
 * Run this script and visit the URL to authorize your app
 */

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

// Load .env file
const envPath = path.resolve(process.cwd(), '.env');
if (fs.existsSync(envPath)) {
  const envConfig = fs.readFileSync(envPath, 'utf8');
  envConfig.split('\n').forEach(line => {
    const match = line.match(/^([^=]+)=(.*)$/);
    if (match) {
      const key = match[1].trim();
      const value = match[2].trim();
      if (!key.startsWith('#')) {
        process.env[key] = value;
      }
    }
  });
}

const APP_ID = process.env.MERCADO_LIBRE_APP_ID;
const REDIRECT_URI = process.env.MERCADO_LIBRE_REDIRECT_URI;
const AUTH_URL = process.env.MERCADO_LIBRE_AUTH_URL || 'https://auth.mercadolibre.com.uy';

if (!APP_ID) {
  console.error('❌ MERCADO_LIBRE_APP_ID not found in .env');
  process.exit(1);
}

if (!REDIRECT_URI) {
  console.error('❌ MERCADO_LIBRE_REDIRECT_URI not found in .env');
  process.exit(1);
}

// Generate a random state for security
const state = crypto.randomUUID();

// Build authorization URL
const params = new URLSearchParams({
  response_type: 'code',
  client_id: APP_ID,
  redirect_uri: REDIRECT_URI,
  state: state,
});

const authUrl = `${AUTH_URL}/authorization?${params.toString()}`;

console.log('\n' + '='.repeat(80));
console.log('🔐 Mercado Libre OAuth Authorization');
console.log('='.repeat(80));
console.log('\nApp ID:', APP_ID);
console.log('Redirect URI:', REDIRECT_URI);
console.log('State:', state);
console.log('\n' + '-'.repeat(80));
console.log('\n📋 AUTHORIZATION URL:\n');
console.log(authUrl);
console.log('\n' + '-'.repeat(80));
console.log('\n📝 Instructions:');
console.log('1. Make sure your app is running at the redirect URI');
console.log('2. Copy the URL above and paste it in your browser');
console.log('3. Login and authorize the app');
console.log('4. You will be redirected back to your app');
console.log('5. The app will automatically exchange the code for tokens');
console.log('\n' + '='.repeat(80) + '\n');

// Save state to a temporary file for verification
const stateFile = path.join(__dirname, '.meli-oauth-state.json');
fs.writeFileSync(stateFile, JSON.stringify({ state, timestamp: Date.now() }));
console.log('💾 State saved to', stateFile);
console.log('   (This will be used to verify the callback)\n');
