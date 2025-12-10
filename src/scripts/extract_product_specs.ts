
import * as fs from 'fs';
import * as path from 'path';

interface Product {
    title: string;
    body_html: string;
    variants: { title: string }[];
    product_type: string;
}

interface ShopifyData {
    products: Product[];
}

const dataPath = path.resolve(process.cwd(), 'data/shopify_products.json');

function extractSpecs() {
    if (!fs.existsSync(dataPath)) {
        console.error('File not found:', dataPath);
        return;
    }

    const rawData = fs.readFileSync(dataPath, 'utf8');
    const data: ShopifyData = JSON.parse(rawData);

    const productSpecs: any[] = [];

    data.products.forEach(p => {
        // Simple regex to find mm dimensions
        const mmMatches = p.body_html.match(/(\d+)\s*mm/gi);
        const thicknesses = mmMatches ? Array.from(new Set(mmMatches)).map(m => m.toLowerCase().replace(/\s/g, '')) : [];

        // Check variants for thickness
        p.variants.forEach(v => {
            const vMatch = v.title.match(/(\d+)\s*mm/gi);
            if (vMatch) {
                vMatch.forEach(m => thicknesses.push(m.toLowerCase().replace(/\s/g, '')));
            }
        });

        const uniqueThicknesses = Array.from(new Set(thicknesses)).sort();

        if (uniqueThicknesses.length > 0 || p.title.toLowerCase().includes("panel") || p.title.toLowerCase().includes("iso")) {
            productSpecs.push({
                title: p.title,
                type: p.product_type,
                thicknesses: uniqueThicknesses
            });
        }
    });

    console.log(JSON.stringify(productSpecs, null, 2));
}

extractSpecs();
