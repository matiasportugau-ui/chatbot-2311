
import { getMotorCotizacionIntegrado } from '../src/lib/integrated-quote-engine';

async function verify() {
    console.log('🚀 Starting MercadoLibre Integration Verification...');

    try {
        const engine = await getMotorCotizacionIntegrado();

        // Access private property for verification (strictly for testing purposes)
        const engineAny = engine as any;
        const interactions = engineAny.interacciones;

        console.log(`📊 Total interactions loaded: ${interactions.length}`);

        const meliInteractions = interactions.filter((i: any) => i.id.startsWith('meli_'));
        console.log(`📦 MercadoLibre interactions found: ${meliInteractions.length}`);

        if (meliInteractions.length > 0) {
            console.log('✅ SUCCESS: MercadoLibre data is visible to the engine!');
            console.log('Sample interaction:', JSON.stringify(meliInteractions[0], null, 2));
        } else {
            console.error('❌ FAILURE: No MercadoLibre interactions found in the engine.');
            process.exit(1);
        }

        // Optional: Test if the engine 'recognizes' the MercadoLibre client
        console.log('\nTesting context analysis for MercadoLibre client...');
        // We used 'MERCADOLIBRE' as the phone number in our aggregation logic
        const context = await engineAny.analizarContexto('Hola, precio?', 'MERCADOLIBRE');
        console.log('Context for "MERCADOLIBRE" user:', JSON.stringify(context.perfilCliente, null, 2));

        if (context.perfilCliente.tipo === 'cliente_recurrente') {
            console.log('✅ SUCCESS: Engine identifies MercadoLibre user as recurrent based on loaded history.');
        } else {
            console.log('⚠️ WARNING: Engine did not identify MercadoLibre user as recurrent (possibly expected if logic requires more data).');
        }

    } catch (error) {
        console.error('❌ Error during verification:', error);
        process.exit(1);
    }
}

verify();
