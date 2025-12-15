import connectMongoose from '../lib/mongoose';
import Product from '../models/Product';

const PRODUCTS = [
    {
        slug: 'isodec',
        name: 'Isodec',
        description: 'Panel aislante térmico con núcleo EPS (Poliestireno Expandido). Excelente para techos y muros.',
        basePrice: 150.00, // AUTHORITATIVE PRICE FROM PYTHON ($150 vs $65 in TS)
        currency: 'USD',
        specifications: {
            availableThicknesses: ['50mm', '100mm', '150mm', '200mm'],
            hasColorOptions: true,
            availableColors: ['Blanco', 'Gris', 'Arena']
        },
        metadata: {
            tags: ['aislante', 'techo', 'muro', 'eps'],
            useCases: ['Residencial', 'Industrial', 'Comercial']
        }
    },
    {
        slug: 'poliestireno',
        name: 'Poliestireno Expandido',
        description: 'Aislante térmico económico y versátil (Espuma Plast). Ideal para contrapisos y rellenos.',
        basePrice: 120.00, // AUTHORITATIVE PRICE FROM PYTHON ($120 vs $45 in TS)
        currency: 'USD',
        specifications: {
            availableThicknesses: ['20mm', '30mm', '50mm', '100mm'],
            hasColorOptions: false,
            availableColors: []
        },
        metadata: {
            tags: ['aislante', 'economico', 'eps'],
            useCases: ['Construcción', 'Embalaje', 'Manualidades']
        }
    },
    {
        slug: 'lana_roca',
        name: 'Lana de Roca',
        description: 'Aislante térmico y acústico incombustible. Ideal para protección contra fuego y reducción de ruido.',
        basePrice: 140.00, // AUTHORITATIVE PRICE FROM PYTHON ($140 vs $50 in TS)
        currency: 'USD',
        specifications: {
            availableThicknesses: ['50mm', '75mm', '100mm'],
            hasColorOptions: false,
            availableColors: []
        },
        metadata: {
            tags: ['aislante', 'acustico', 'ignifugo'],
            useCases: ['Tabiques', 'Cielorrasos', 'Industria']
        }
    }
];

async function seed() {
    try {
        console.log('🌱 Connecting to MongoDB...');
        await connectMongoose();

        console.log('🧹 Clearing existing products...');
        await Product.deleteMany({});

        console.log('🚀 Seeding products...');
        for (const p of PRODUCTS) {
            await Product.create(p);
            console.log(`✅ Created: ${p.name} at $${p.basePrice}`);
        }

        console.log('✨ Seeding complete!');
        process.exit(0);
    } catch (error) {
        console.error('❌ Seeding failed:', error);
        process.exit(1);
    }
}

seed();
