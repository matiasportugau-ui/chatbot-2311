import axios from 'axios';
import * as cheerio from 'cheerio';

const URL = 'https://bmcuruguay.com.uy/products/isodec%C2%AE-pir';

async function main() {
    console.log(`🕷️ Scraping variants from ${URL}...`);
    try {
        const response = await axios.get(URL);
        // Look for JSON data often found in Shopify products scripts
        // usually inside <script id="ProductJson-..." type="application/json"> or similar
        // or just regex for "variants": [...]

        const html = response.data;
        const jsonMatch = html.match(/var meta = (\{[\s\S]*?\});/) || html.match(/"variants":\s*(\[[\s\S]*?\])/);

        if (jsonMatch) {
            // This might be partial. Let's look for known Shopify `product` JSON
            // Often it's in a script tag `window.ShopifyAnalytics.meta.product`
            // Or just search for `sku` and `id` pattern.

            // heuristic: find "id": 123456... and "title": "50mm"
            const variantsRegex = /"id":\s*(\d+),\s*"title":\s*"([^"]+)"/g;
            let match;
            console.log("Found variants:");
            while ((match = variantsRegex.exec(html)) !== null) {
                console.log(` - ID: ${match[1]}, Title: ${match[2]}`);
            }
        } else {
            console.log("⚠️ No JSON variants found. Trying Cheerio selectors...");
            const $ = cheerio.load(html);
            $('select[name="id"] option').each((i, el) => {
                console.log(` - ID: $(el).val(), Title: $(el).text()`);
            });
        }

    } catch (e: any) {
        console.error(e.message);
    }
}

main();
