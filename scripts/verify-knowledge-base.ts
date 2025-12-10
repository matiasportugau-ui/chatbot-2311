import { PRODUCTOS, buscarProducto, calculateFullQuote } from '../src/lib/knowledge-base';

console.log('🔍 Verificando Knowledge Base...');

const totalProductos = Object.keys(PRODUCTOS).length;
console.log(`✅ Total de productos cargados: ${totalProductos}`);

// Verificar un producto conocido del ODS
const testSlug = '01082025'; // From extraction
const product = PRODUCTOS[testSlug];

if (product) {
    console.log(`✅ Producto encontrado: ${product.nombre}`);
    console.log(`   Variantes: ${product.variantes.length}`);
    console.log(`   Precios Map keys: ${Object.keys(product.precios).join(', ')}`);
} else {
    console.error(`❌ Error: No se encontró el producto ${testSlug}`);
}

// Probar búsqueda
const searchTerms = ['isodec', 'teja', 'poliestireno'];
console.log('\n🔎 Probando búsqueda de productos:');
searchTerms.forEach(term => {
    const key = buscarProducto(term);
    if (key) {
        console.log(`   ✅ "${term}" -> encontrado como key: "${key}" (${PRODUCTOS[key].nombre})`);
    } else {
        console.log(`   ⚠️ "${term}" -> No encontrado`);
    }
});

// Probar cotización
console.log('\n💰 Probando cálculo de cotización:');
try {
    const quote = calculateFullQuote({
        producto: 'isodec', // This should match a key in PRODUCTOS. My extraction has 'isodec' group?
        // Wait, did I extract 'isodec'? Let's check the extracted JSON keys.
        // If "isodec" key exists in my generated file, it should work.
        dimensiones: { ancho: 10, largo: 10, espesor: 100 },
        cantidad: 1
    });
    console.log('   ✅ Cotización exitosa para Isodec:', quote.total);
    console.log('   ℹ️  Detalles:', quote.detalles);
    console.log('   📦 Cantidad calc:', quote.cantidad);
    console.log('   🛒 Link Carrito:', quote.cartLink);
} catch (e) {
    console.error('   ❌ Error calculando cotización:', e);
}

// Dump keys to see what we have
// console.log('Keys disponibles:', Object.keys(PRODUCTOS));
