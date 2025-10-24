#!/usr/bin/env node

/**
 * 🧪 Test Completo del Sistema BMC
 * Verifica todos los componentes: Health, Google Sheets, MongoDB, OpenAI
 */

const axios = require('axios');
const colors = require('colors');

const BASE_URL = 'http://localhost:3000';
const TEST_QUERY = 'Test Isodec 100mm para galpón de 50m2';

console.log('🚀 INICIANDO TEST COMPLETO DEL SISTEMA BMC\n'.cyan.bold);

async function testHealthCheck() {
  console.log('1️⃣ Probando Health Check...'.yellow);
  try {
    const response = await axios.get(`${BASE_URL}/api/health`);
    const data = response.data;
    
    console.log('   ✅ Health Check Status:', data.status.green);
    console.log('   📊 Servicios:');
    console.log(`      - OpenAI: ${data.services.openai.status}`.green);
    console.log(`      - Google Sheets: ${data.services.googleSheets.status}`.green);
    console.log(`      - MongoDB: ${data.services.mongodb.status}`.green);
    console.log(`      - WhatsApp: ${data.services.whatsapp.status}`.blue);
    
    return data.status === 'healthy';
  } catch (error) {
    console.log('   ❌ Health Check Error:', error.message.red);
    return false;
  }
}

async function testGoogleSheets() {
  console.log('\n2️⃣ Probando Google Sheets...'.yellow);
  try {
    const response = await axios.get(`${BASE_URL}/api/sheets/enhanced-sync?action=all`);
    const data = response.data;
    
    console.log('   ✅ Google Sheets conectado');
    console.log(`   📊 Total cotizaciones: ${data.total}`);
    console.log(`   📋 Admin: ${data.admin.length}, Enviados: ${data.enviados.length}, Confirmados: ${data.confirmados.length}`);
    
    return true;
  } catch (error) {
    console.log('   ❌ Google Sheets Error:', error.message.red);
    return false;
  }
}

async function testIntegratedQuote() {
  console.log('\n3️⃣ Probando Sistema Integrado...'.yellow);
  try {
    const response = await axios.post(`${BASE_URL}/api/integrated-quote`, {
      action: 'process',
      consulta: TEST_QUERY,
      userPhone: '+59891234567',
      userName: 'Cliente Test'
    });
    
    const data = response.data;
    console.log('   ✅ Sistema Integrado funcionando');
    console.log(`   🎯 Confianza: ${data.confidence}%`);
    console.log(`   📝 Producto detectado: ${data.producto || 'N/A'}`);
    console.log(`   📏 Dimensiones: ${data.dimensiones || 'N/A'}`);
    console.log(`   💰 Cotización: ${data.cotizacion ? 'Generada' : 'No generada'}`);
    
    return true;
  } catch (error) {
    console.log('   ❌ Sistema Integrado Error:', error.message.red);
    return false;
  }
}

async function testParseQuote() {
  console.log('\n4️⃣ Probando Parser de Cotizaciones...'.yellow);
  try {
    const response = await axios.post(`${BASE_URL}/api/parse-quote`, {
      consulta: TEST_QUERY,
      userPhone: '+59891234567',
      userName: 'Cliente Test'
    });
    
    const data = response.data;
    console.log('   ✅ Parser funcionando');
    console.log(`   🎯 Confianza: ${data.confidence}%`);
    console.log(`   📝 Producto: ${data.producto || 'N/A'}`);
    console.log(`   📏 Dimensiones: ${data.dimensiones || 'N/A'}`);
    console.log(`   🏗️ Servicios: ${data.servicios ? data.servicios.join(', ') : 'N/A'}`);
    
    return true;
  } catch (error) {
    console.log('   ❌ Parser Error:', error.message.red);
    return false;
  }
}

async function testDashboard() {
  console.log('\n5️⃣ Probando Dashboard...'.yellow);
  try {
    const response = await axios.get(`${BASE_URL}/`);
    
    if (response.status === 200) {
      console.log('   ✅ Dashboard accesible');
      console.log('   🌐 URL: http://localhost:3000');
      return true;
    } else {
      console.log('   ❌ Dashboard no accesible');
      return false;
    }
  } catch (error) {
    console.log('   ❌ Dashboard Error:', error.message.red);
    return false;
  }
}

async function runCompleteTest() {
  const results = {
    health: false,
    sheets: false,
    integrated: false,
    parser: false,
    dashboard: false
  };
  
  // Test 1: Health Check
  results.health = await testHealthCheck();
  
  if (!results.health) {
    console.log('\n❌ CRÍTICO: Health Check falló. Verifica credenciales.'.red.bold);
    return;
  }
  
  // Test 2: Google Sheets
  results.sheets = await testGoogleSheets();
  
  // Test 3: Sistema Integrado
  results.integrated = await testIntegratedQuote();
  
  // Test 4: Parser
  results.parser = await testParseQuote();
  
  // Test 5: Dashboard
  results.dashboard = await testDashboard();
  
  // Resumen final
  console.log('\n' + '='.repeat(50).cyan);
  console.log('📊 RESUMEN DE TESTS'.cyan.bold);
  console.log('='.repeat(50).cyan);
  
  const passed = Object.values(results).filter(Boolean).length;
  const total = Object.keys(results).length;
  
  console.log(`✅ Tests pasados: ${passed}/${total}`.green);
  console.log(`❌ Tests fallidos: ${total - passed}/${total}`.red);
  
  console.log('\n📋 Detalle:');
  console.log(`   Health Check: ${results.health ? '✅' : '❌'}`);
  console.log(`   Google Sheets: ${results.sheets ? '✅' : '❌'}`);
  console.log(`   Sistema Integrado: ${results.integrated ? '✅' : '❌'}`);
  console.log(`   Parser: ${results.parser ? '✅' : '❌'}`);
  console.log(`   Dashboard: ${results.dashboard ? '✅' : '❌'}`);
  
  if (passed === total) {
    console.log('\n🎉 ¡SISTEMA COMPLETAMENTE FUNCIONAL!'.green.bold);
    console.log('🚀 Listo para deploy a producción'.green);
  } else if (passed >= 3) {
    console.log('\n⚠️ Sistema parcialmente funcional'.yellow.bold);
    console.log('🔧 Revisa los tests fallidos antes del deploy'.yellow);
  } else {
    console.log('\n❌ Sistema no funcional'.red.bold);
    console.log('🔧 Configura credenciales y reinicia servidor'.red);
  }
  
  console.log('\n🌐 Dashboard: http://localhost:3000'.blue);
  console.log('📊 Health Check: http://localhost:3000/api/health'.blue);
}

// Ejecutar tests
runCompleteTest().catch(console.error);
