
import { GoogleSheetsEnhancedClient } from '../lib/google-sheets-enhanced';
import { initializeSecureConfig } from '../lib/secure-config';
import * as fs from 'fs';
import * as path from 'path';

// MANUAL ENV LOADING
const envPath = path.resolve(process.cwd(), '.env'); // Changed to .env
if (fs.existsSync(envPath)) {
    console.log(`Loading env from ${envPath}`);
    const envConfig = fs.readFileSync(envPath, 'utf8');
    envConfig.split('\n').forEach(line => {
        const [key, ...values] = line.split('=');
        if (key && values.length > 0) {
            const val = values.join('=').trim().replace(/^["'](.*)["']$/, '$1'); // simple unquote
            if (!process.env[key.trim()]) {
                process.env[key.trim()] = val;
            }
        }
    });
} else {
    console.warn('.env not found');
}

// Force development mode to ensure credentials.json is loaded if present
// process.env.NODE_ENV = 'development';

async function analyzeSheet() {
    console.log('🔍 Starting Google Sheet Analysis...');

    try {
        // 1. Initialize Configuration
        console.log('1. Initializing Secure Configuration...');
        await initializeSecureConfig();

        // 2. Initialize Client
        console.log('2. Connecting to Google Sheets...');
        const client = new GoogleSheetsEnhancedClient();

        // access private property (hack for diagnostic) to get sheet ID if possible, 
        // or just rely on what the client uses.
        // @ts-ignore
        const sheetId = client.spreadsheetId;
        console.log(`   Target Sheet ID: ${sheetId}`);

        // 3. Read "Admin." Tab (Headers + Sample)
        console.log('3. Reading "Admin." tab...');
        // We want raw values to see headers, but client.readAdminTab() uses a parser that assumes headers.
        // We will use the underlying sheets API if possible, or just call read and infer.
        // To get raw structure even if parsing fails, we might need to be careful.
        // Let's try the high level methods first.

        const adminRows = await client.readAdminTab();

        console.log(`   ✅ Read ${adminRows.length} rows from Admin.`);

        if (adminRows.length > 0) {
            console.log('   Sample Row (Admin):');
            console.log(JSON.stringify(adminRows[0], null, 2));
        } else {
            console.log('   ⚠️ Admin tab appears empty or parsing failed to find data rows.');
        }

        // 4. Read "Confirmado" Tab
        console.log('4. Reading "Confirmado" tab...');
        const confirmedRows = await client.readConfirmadoTab();
        console.log(`   ✅ Read ${confirmedRows.length} rows from Confirmado.`);

        if (confirmedRows.length > 0) {
            console.log('   Sample Row (Confirmado):');
            console.log(JSON.stringify(confirmedRows[0], null, 2));
        }

        // 5. Generate Report
        const report = {
            sheetId,
            timestamp: new Date().toISOString(),
            tabs: {
                admin: {
                    rowCount: adminRows.length,
                    sample: adminRows.slice(0, 3)
                },
                confirmado: {
                    rowCount: confirmedRows.length,
                    sample: confirmedRows.slice(0, 3)
                }
            }
        };

        const reportPath = path.join(process.cwd(), 'sheet_analysis_report.json');
        fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
        console.log(`\n✅ Analysis complete. Report saved to ${reportPath}`);

    } catch (error) {
        console.error('❌ Analysis Failed:', error);
        process.exit(1);
    }
}

analyzeSheet();
