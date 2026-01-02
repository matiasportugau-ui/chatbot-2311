#!/usr/bin/env node

// Auto‑run wrapper for the MercadoLibre draft‑answers script
// This file simply imports the main function from the existing script
// and executes it. It can be invoked directly or via an npm bin.

import path from 'path';
import { fileURLToPath } from 'url';

// Resolve the location of the original TypeScript file (compiled to JS at runtime via ts-node)
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Use ts-node/register to allow on‑the‑fly TypeScript execution
require('ts-node/register');

// Import the script's main function using CommonJS require
const { main: draftMain } = require('./draft-answers-script');

(async () => {
  try {
    await draftMain();
    console.log('✅ MercadoLibre draft answers completed');
  } catch (err) {
    console.error('❌ Error running draft answers:', err);
    process.exit(1);
  }
})();
