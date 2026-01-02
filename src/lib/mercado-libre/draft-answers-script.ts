
import { MongoClient, Db } from 'mongodb';
import fs from 'fs';
import path from 'path';
import https from 'https';
import http from 'http';

// --- Load .env manually ---
try {
  const envPath = path.resolve(process.cwd(), '.env');
  if (fs.existsSync(envPath)) {
    const envConfig = fs.readFileSync(envPath, 'utf8');
    envConfig.split('\n').forEach(line => {
      const match = line.match(/^([^=]+)=(.*)$/);
      if (match) {
        const key = match[1].trim();
        const value = match[2].trim();
        // Handle unquoted values with spaces? The regex captures rest of line.
        // We should ignore comments.
        if (!key.startsWith('#')) {
             process.env[key] = value;
        }
      }
    });
    console.log('.env loaded successfully');
  } else {
      console.warn('.env not found at ' + envPath);
  }
} catch (e) {
  console.error('Error loading .env:', e);
}

// --- Configuration ---
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/bmc-cotizaciones';
const PY_API_URL = process.env.PY_CHAT_SERVICE_URL || 'http://localhost:8000';
const INTERNAL_API_KEY = process.env.INTERNAL_API_KEY;
const SELLER_ID = process.env.MERCADO_LIBRE_SELLER_ID;

// --- Interfaces ---
interface MercadoLibreGrant {
  accessToken: string;
  refreshToken: string;
  expiresAt: Date;
  sellerId: string;
}

// --- MongoDB ---
let client: MongoClient | null = null;
let db: Db | null = null;

async function connectDB(): Promise<Db> {
  if (db) return db;
  client = new MongoClient(MONGODB_URI);
  await client.connect();
  db = client.db('bmc_quotes'); // Changed from bmc_chat
  return db;
}

async function closeDB() {
  if (client) await client.close();
}

// --- Token Store ---
async function getActiveGrant(): Promise<MercadoLibreGrant | null> {
  const database = await connectDB();
  const grant = await database
    .collection('mercado_libre_grants')
    .find({ sellerId: { $exists: true } })
    .sort({ updatedAt: -1 })
    .limit(1)
    .next();

  if (grant) {
      return grant as unknown as MercadoLibreGrant;
  }

  // Fallback to environment variables
  const accessToken = process.env.MERCADO_LIBRE_ACCESS_TOKEN || process.env.MELI_ACCESS_TOKEN;
  const refreshToken = process.env.MERCADO_LIBRE_REFRESH_TOKEN || process.env.MELI_REFRESH_TOKEN;
  const sellerId = process.env.MERCADO_LIBRE_SELLER_ID || process.env.MELI_SELLER_ID;

  if (accessToken && sellerId) {
      console.log('Using access token from environment variables.');
      return {
          accessToken: accessToken,
          refreshToken: refreshToken || '',
          expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000), // valid for 24h
          sellerId: sellerId
      };
  }

  return null;
}

// --- API Helpers ---
function httpsRequest(options: any, body?: any): Promise<any> {
  return new Promise((resolve, reject) => {
    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try {
          resolve({ status: res.statusCode, data: JSON.parse(data) });
        } catch (e) {
          resolve({ status: res.statusCode, data });
        }
      });
    });
    req.on('error', reject);
    if (body) req.write(typeof body === 'string' ? body : JSON.stringify(body));
    req.end();
  });
}

function fetchRequest(url: string, options: any): Promise<any> {
    const lib = url.startsWith('https') ? https : http;
    return new Promise((resolve, reject) => {
        const req = lib.request(url, options, (res) => {
             let data = '';
            res.on('data', (chunk) => data += chunk);
            res.on('end', () => {
                try {
                resolve({ ok: res.statusCode && res.statusCode >= 200 && res.statusCode < 300, status: res.statusCode, json: () => JSON.parse(data) });
                } catch (e) {
                resolve({ ok: res.statusCode && res.statusCode >= 200 && res.statusCode < 300, status: res.statusCode, json: () => data });
                }
            });
        });
        req.on('error', reject);
        if (options.body) req.write(options.body);
        req.end();
    });
}

// --- Main ---
async function main() {
  try {
    console.log('--- Starting Mercado Libre Check ---');
    console.log(`Seller ID: ${SELLER_ID}`);
    // console.log(`URI: ${MONGODB_URI}`); // CAUTION: don't log secrets

    const database = await connectDB();
    console.log(`Connected to DB: ${database.databaseName}`);

    try {
        const adminDb = database.admin();
        const dbs = await adminDb.listDatabases();
        console.log('Databases:', dbs.databases.map(db => db.name));
    } catch(e) {
        console.log('Could not list databases:', e);
    }

    const collections = await database.listCollections().toArray();
    console.log('Collections:', collections.map(c => c.name));

    // 1. Get Token
    const count = await database.collection('mercado_libre_grants').countDocuments();
    console.log(`Grants count: ${count}`);

    const grant = await getActiveGrant();
    // 2. Fetch Questions
    // SIMULATION MODE CHECK
    let questions: any[] = [];
    if (!grant) {
        console.warn('⚠️ No active grant or credentials found. Running in SIMULATION MODE.');
        questions = [
            {
                id: '123456',
                text: 'Hola, ¿tienen stock del producto?',
                item_id: 'MLA87654321',
                date_created: new Date().toISOString(),
                status: 'UNANSWERED',
                from: { id: 999111 }
            },
            {
                id: '123457',
                text: '¿Hacen envíos a Cordoba?',
                item_id: 'MLA87654322',
                date_created: new Date().toISOString(),
                status: 'UNANSWERED',
                from: { id: 999222 }
            }
        ];
    } else {
         const questionsUrl = `https://api.mercadolibre.com/questions/search?seller=${SELLER_ID}&status=UNANSWERED`;
         console.log(`Fetching: ${questionsUrl}`);
         const qRes = await httpsRequest({
           method: 'GET',
           hostname: 'api.mercadolibre.com',
           path: `/questions/search?seller=${SELLER_ID}&status=UNANSWERED`,
           headers: { 'Authorization': `Bearer ${grant.accessToken}` }
         });

         if (qRes.status !== 200) {
           console.error('Error fetching questions:', qRes.data);
           return;
         }
         questions = qRes.data.questions || [];
    }
    console.log(`Found ${questions.length} unanswered questions.`);

    let output = '# Mercado Libre - Unanswered Questions & Draft Answers\n\n';

    for (const q of questions) {
      console.log(`Processing question ${q.id}: "${q.text}"`);
      output += `## Question ${q.id}\n`;
      output += `**User:** ${q.text}\n`;
      output += `**Item:** ${q.item_id}\n`;
      output += `**Date:** ${q.date_created}\n\n`;

      // 3. Generate Answer via AI
      try {
        const aiResponse = await fetchRequest(`${PY_API_URL}/api/chat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': INTERNAL_API_KEY || ''
          },
          body: JSON.stringify({
            message: q.text,
            session_id: `meli_draft_${q.id}` // Temporary session
          })
        });

        if (aiResponse.ok) {
          const aiData = await aiResponse.json();
          output += `### Proposed Answer\n${aiData.response}\n\n`;
        } else {
             const err = await aiResponse.json();
          output += `### Proposed Answer\n*Error generating AI response: ${JSON.stringify(err)}*\n\n`;
        }
      } catch (e: any) {
        output += `### Proposed Answer\n*Error calling AI service: ${e.message}*\n\n`;
      }

      output += `---\n\n`;
    }

    fs.writeFileSync('MERCADO_LIBRE_DRAFT_ANSWERS.md', output);
    console.log('Report generated: MERCADO_LIBRE_DRAFT_ANSWERS.md');

  } catch (error) {
    console.error('Script failed:', error);
  } finally {
    await closeDB();
  }
}

main();
export { main };
