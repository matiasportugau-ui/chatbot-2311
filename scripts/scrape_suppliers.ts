import axios from 'axios';
import * as cheerio from 'cheerio';
import fs from 'fs';
import path from 'path';

const SUPPLIERS = [
    { name: 'BMC Uruguay', url: 'https://bmcuruguay.com.uy', type: 'primary' },
    { name: 'Montfrio', url: 'https://montfrio.com.uy', type: 'competitor' },
    { name: 'Bromyros', url: 'https://bromyros.com.uy', type: 'competitor' },
    { name: 'Cibulis', url: 'https://cibulis.com.uy', type: 'competitor' }
];

const OUTPUT_FILE = path.join(process.cwd(), 'data/supplier_knowledge.json');

async function scrapeSite(supplier: { name: string, url: string, type: string }) {
    console.log(`\n🕷️ Scraping ${supplier.name} (${supplier.url})...`);
    try {
        const response = await axios.get(supplier.url, {
            headers: { 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36' }
        });
        const $ = cheerio.load(response.data);

        const pageTitle = $('title').text().trim();
        console.log(`   📄 Title: ${pageTitle}`);

        const products: any[] = [];

        // Generic heuristics to find products
        // Looking for common e-commerce structures
        $('a[href*="product"], a[href*="producto"], .product, .woocommerce-loop-product__title').each((i, el) => {
            if (products.length > 20) return; // Limit for now

            const link = $(el).attr('href');
            const text = $(el).text().trim();
            const title = $(el).attr('title') || text;

            if (title && link && !products.find(p => p.link === link)) {
                // Try to find price near the link
                let price = '';
                const parent = $(el).closest('.product, li, div');
                if (parent.length) {
                    price = parent.find('.price, .amount').text().trim();
                    // Check for add into cart link
                    const addLink = parent.find('a[href*="add-to-cart"]').attr('href');
                    if (addLink) {
                        console.log(`      🛒 Found Add to Cart: ${addLink}`);
                    }
                }

                products.push({
                    title,
                    link: link.startsWith('http') ? link : `${supplier.url}${link}`,
                    price,
                    source: supplier.name
                });
            }
        });

        console.log(`   ✅ Found ${products.length} potential products/links.`);
        return {
            supplier: supplier.name,
            url: supplier.url,
            title: pageTitle,
            products
        };

    } catch (error: any) {
        console.error(`   ❌ Error scraping ${supplier.name}: ${error.message}`);
        return null;
    }
}

async function main() {
    // Ensure data directory exists
    const dataDir = path.dirname(OUTPUT_FILE);
    if (!fs.existsSync(dataDir)) {
        fs.mkdirSync(dataDir, { recursive: true });
    }

    const results = [];
    for (const supplier of SUPPLIERS) {
        const result = await scrapeSite(supplier);
        if (result) results.push(result);
    }

    fs.writeFileSync(OUTPUT_FILE, JSON.stringify(results, null, 2));
    console.log(`\n💾 Saved supplier knowledge to ${OUTPUT_FILE}`);
}

main();
