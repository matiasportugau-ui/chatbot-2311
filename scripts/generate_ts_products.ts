import fs from 'fs';
import path from 'path';

const JSON_PATH = path.join(process.cwd(), 'scripts/extracted_products.json');
const TS_OUTPUT_PATH = path.join(process.cwd(), 'src/lib/generated-products.ts');

interface ProductVariant {
    source: string;
    name: string;
    price: number;
    thickness: string | null;
    unit: string;
    width?: number;
}

interface ProductGroup {
    nombre: string;
    unidad: string;
    variantes: ProductVariant[];
}

interface ExtractedData {
    [key: string]: ProductGroup;
}

function generateTS() {
    if (!fs.existsSync(JSON_PATH)) {
        console.error(`❌ JSON file not found: ${JSON_PATH}`);
        process.exit(1);
    }

    const rawData = fs.readFileSync(JSON_PATH, 'utf-8');
    const data: ExtractedData = JSON.parse(rawData);

    let tsContent = `// 🤖 ARCHIVO GENERADO AUTOMÁTICAMENTE - NO EDITAR MANUALMENTE
// Origen: scripts/extracted_products.json
// Fecha: ${new Date().toISOString()}

export interface ProductoVariante {
  source: string
  name: string
  price: number
  thickness: string | null
  unit: string
  width: number | null
}

export interface ProductoDefinicion {
  nombre: string
  unidad: string
  variantes: ProductoVariante[]
  precios?: Record<string, number> // Compatibilidad hacia atrás
  descripcion?: string // Compatibilidad hacia atrás
}

export const GENERATED_PRODUCTS: Record<string, ProductoDefinicion> = {
`;

    for (const [key, group] of Object.entries(data)) {
        // Normalize key for variable name safety if needed, but string keys are fine
        tsContent += `  '${key}': {\n`;
        tsContent += `    nombre: '${group.nombre.replace(/'/g, "\\'")}',\n`;
        tsContent += `    unidad: '${group.unidad}',\n`;
        tsContent += `    descripcion: 'Generado desde cotizaciones: ${group.variantes.length} variantes',\n`;

        // Generate "precios" map for compatibility with existing calculates
        // We'll take the first price for each thickness found
        const preciosMap: Record<string, number> = {};
        group.variantes.forEach(v => {
            if (v.thickness && v.price > 0) {
                // If duplicate thickness, maybe average? Or just take first. 
                // Taking first for now or max to be safe? 
                // Let's take the one that looks most "standard" or just the last one to overwrite.
                // Actually, let's try to find a median or just list them.
                // For simple compatibility, map thickness -> price
                const tKey = v.thickness.toLowerCase().replace(' ', '');
                if (!preciosMap[tKey]) {
                    preciosMap[tKey] = v.price;
                }
            }
        });

        tsContent += `    precios: {\n`;
        for (const [t, p] of Object.entries(preciosMap)) {
            tsContent += `      '${t}': ${p},\n`;
        }
        tsContent += `    },\n`;

        tsContent += `    variantes: [\n`;
        for (const variant of group.variantes) {
            tsContent += `      {\n`;
            tsContent += `        source: '${variant.source.replace(/'/g, "\\'")}',\n`;
            tsContent += `        name: '${variant.name.replace(/'/g, "\\'")}',\n`;
            tsContent += `        price: ${variant.price},\n`;
            tsContent += `        thickness: ${variant.thickness ? `'${variant.thickness}'` : 'null'},\n`;
            tsContent += `        unit: '${variant.unit}',\n`;
            tsContent += `        // Ancho útil detectado: ${variant.width || 'No detectado'}\n`;
            tsContent += `        width: ${variant.width || 'null'}\n`;
            tsContent += `      },\n`;
        }
        tsContent += `    ]\n`;
        tsContent += `  },\n`;
    }

    tsContent += `};\n`;

    fs.writeFileSync(TS_OUTPUT_PATH, tsContent);
    console.log(`✅ Generated TypeScript file at: ${TS_OUTPUT_PATH}`);
}

generateTS();
