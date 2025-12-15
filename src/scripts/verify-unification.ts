import connectMongoose from '../lib/mongoose';
import { calculateFullQuote } from '../lib/knowledge-base';

async function verify() {
    try {
        console.log('🧪 Connecting to DB...');
        await connectMongoose();

        console.log('🧪 Testing calculateFullQuote with "Isodec"...');
        // Isodec price in DB is 150. Dimensions 10x10 = 100m2. Total should be 15000.
        const result = await calculateFullQuote({
            producto: 'isodec',
            dimensiones: { ancho: 10, largo: 10, espesor: 100 },
            cantidad: 1
        });

        console.log('📄 Quote Result:', JSON.stringify(result, null, 2));

        if (result.precioUnitario === 150) {
            console.log('✅ PASSED: Price matched MongoDB authoritative price ($150).');
        } else {
            console.error(`❌ FAILED: Price mismatch. Expected 150, got ${result.precioUnitario}`);
        }

        process.exit(0);
    } catch (e: any) {
        console.error('❌ Error during verification:', e.message);
        process.exit(1);
    }
}

verify();
