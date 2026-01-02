#!/usr/bin/env node

/**
 * 🧪 Script de Testing para Google Sheets Integration
 * 
 * Este script prueba la integración completa con Google Sheets
 * del "Administrador de Cotizaciones" de BMC.
 */

const axios = require('axios')

const BASE_URL = 'http://localhost:3000'
const API_ENDPOINTS = {
  enhancedSync: `${BASE_URL}/api/sheets/enhanced-sync`,
  integratedQuote: `${BASE_URL}/api/integrated-quote`
}

// Colores para output
const colors = {
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  reset: '\x1b[0m',
  bold: '\x1b[1m'
}

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`)
}

function logTest(testName, status, details = '') {
  const statusIcon = status === 'PASS' ? '✅' : status === 'FAIL' ? '❌' : '⏳'
  const statusColor = status === 'PASS' ? 'green' : status === 'FAIL' ? 'red' : 'yellow'
  
  log(`${statusIcon} ${testName}`, statusColor)
  if (details) {
    log(`   ${details}`, 'blue')
  }
}

// Casos de prueba para Google Sheets
const testCases = [
  {
    name: 'Obtener todas las cotizaciones',
    endpoint: `${API_ENDPOINTS.enhancedSync}?action=all`,
    method: 'GET'
  },
  {
    name: 'Obtener cotizaciones pendientes',
    endpoint: `${API_ENDPOINTS.enhancedSync}?action=admin`,
    method: 'GET'
  },
  {
    name: 'Obtener cotizaciones enviadas',
    endpoint: `${API_ENDPOINTS.enhancedSync}?action=enviados`,
    method: 'GET'
  },
  {
    name: 'Obtener cotizaciones confirmadas',
    endpoint: `${API_ENDPOINTS.enhancedSync}?action=confirmados`,
    method: 'GET'
  },
  {
    name: 'Obtener estadísticas',
    endpoint: `${API_ENDPOINTS.enhancedSync}?action=statistics`,
    method: 'GET'
  }
]

async function testGoogleSheetsConnection() {
  log('\n📊 Testing Conexión con Google Sheets', 'bold')
  log('=' * 40, 'blue')
  
  let passed = 0
  let failed = 0
  
  for (const testCase of testCases) {
    try {
      log(`\n📝 ${testCase.name}`, 'yellow')
      
      const response = await axios({
        method: testCase.method,
        url: testCase.endpoint,
        timeout: 30000
      })
      
      if (response.data.success) {
        logTest(testCase.name, 'PASS', `Datos obtenidos: ${JSON.stringify(response.data.data).length} caracteres`)
        
        // Mostrar detalles específicos según el tipo de datos
        if (testCase.name.includes('todas')) {
          const data = response.data.data
          log(`   📋 Admin: ${data.admin?.length || 0} registros`, 'blue')
          log(`   📤 Enviados: ${data.enviados?.length || 0} registros`, 'blue')
          log(`   ✅ Confirmados: ${data.confirmados?.length || 0} registros`, 'blue')
        } else if (testCase.name.includes('estadísticas')) {
          const stats = response.data.data.statistics
          log(`   📊 Total Pendientes: ${stats.totalPendientes}`, 'blue')
          log(`   📊 Total Enviados: ${stats.totalEnviados}`, 'blue')
          log(`   📊 Total Confirmados: ${stats.totalConfirmados}`, 'blue')
          log(`   📊 Total Cotizaciones: ${stats.totalCotizaciones}`, 'blue')
        }
        
        passed++
      } else {
        logTest(testCase.name, 'FAIL', 'Respuesta no exitosa del servidor')
        failed++
      }
      
    } catch (error) {
      logTest(testCase.name, 'FAIL', `Error: ${error.message}`)
      failed++
    }
  }
  
  return { passed, failed }
}

async function testAddQuote() {
  log('\n➕ Testing Agregar Cotización', 'bold')
  log('=' * 30, 'blue')
  
  try {
    const testQuote = {
      action: 'add_quote',
      data: {
        arg: `TEST${Date.now()}`,
        estado: 'Pendiente',
        fecha: new Date().toLocaleDateString('es-UY'),
        cliente: 'Cliente Test',
        origen: 'WA',
        telefono: '+59899999999',
        direccion: 'Montevideo, Uruguay',
        consulta: 'Test de integración con Google Sheets - Isodec 100mm para galpón de 50m2'
      }
    }
    
    const response = await axios.post(API_ENDPOINTS.enhancedSync, testQuote, {
      headers: { 'Content-Type': 'application/json' },
      timeout: 30000
    })
    
    if (response.data.success) {
      logTest('Agregar Cotización', 'PASS', `Código: ${response.data.data.arg}`)
      return { passed: 1, failed: 0, testQuote }
    } else {
      logTest('Agregar Cotización', 'FAIL', 'Error en la respuesta')
      return { passed: 0, failed: 1, testQuote: null }
    }
    
  } catch (error) {
    logTest('Agregar Cotización', 'FAIL', `Error: ${error.message}`)
    return { passed: 0, failed: 1, testQuote: null }
  }
}

async function testSearchFunctionality() {
  log('\n🔍 Testing Funcionalidad de Búsqueda', 'bold')
  log('=' * 35, 'blue')
  
  let passed = 0
  let failed = 0
  
  // Test búsqueda por teléfono
  try {
    const response = await axios.get(`${API_ENDPOINTS.enhancedSync}?action=search&phone=+59899999999`, {
      timeout: 15000
    })
    
    if (response.data.success) {
      logTest('Búsqueda por Teléfono', 'PASS', `Encontrados: ${response.data.data.total} registros`)
      passed++
    } else {
      logTest('Búsqueda por Teléfono', 'FAIL', 'Error en búsqueda')
      failed++
    }
  } catch (error) {
    logTest('Búsqueda por Teléfono', 'FAIL', `Error: ${error.message}`)
    failed++
  }
  
  // Test búsqueda por código Arg
  try {
    const response = await axios.get(`${API_ENDPOINTS.enhancedSync}?action=search&arg=TEST`, {
      timeout: 15000
    })
    
    if (response.data.success) {
      logTest('Búsqueda por Código', 'PASS', `Encontrado: ${response.data.data.found ? 'Sí' : 'No'}`)
      passed++
    } else {
      logTest('Búsqueda por Código', 'FAIL', 'Error en búsqueda')
      failed++
    }
  } catch (error) {
    logTest('Búsqueda por Código', 'FAIL', `Error: ${error.message}`)
    failed++
  }
  
  return { passed, failed }
}

async function testSystemHealth() {
  log('\n🏥 Testing Salud del Sistema', 'bold')
  log('=' * 25, 'blue')
  
  try {
    const response = await axios.get(`${API_ENDPOINTS.integratedQuote}?action=health`, {
      timeout: 5000
    })
    
    if (response.data.success && response.data.data?.status === 'healthy') {
      logTest('Salud del Sistema', 'PASS', 'Sistema funcionando correctamente')
      
      const data = response.data.data
      log(`   🟢 Estado: ${data.status}`, 'blue')
      log(`   ⏱️  Uptime: ${Math.round(data.uptime)}s`, 'blue')
      log(`   💾 Memoria: ${Math.round(data.memory.used / 1024 / 1024)}MB`, 'blue')
      
      return { passed: 1, failed: 0 }
    } else {
      logTest('Salud del Sistema', 'FAIL', 'Sistema no saludable')
      return { passed: 0, failed: 1 }
    }
    
  } catch (error) {
    logTest('Salud del Sistema', 'FAIL', `Error: ${error.message}`)
    return { passed: 0, failed: 1 }
  }
}

async function runAllTests() {
  log('🚀 Iniciando Tests de Google Sheets Integration', 'bold')
  log('=' * 50, 'blue')
  log(`🌐 URL Base: ${BASE_URL}`, 'blue')
  log(`⏰ Timestamp: ${new Date().toISOString()}`, 'blue')
  
  let totalPassed = 0
  let totalFailed = 0
  
  // Ejecutar todos los tests
  const results = await Promise.all([
    testGoogleSheetsConnection(),
    testAddQuote(),
    testSearchFunctionality(),
    testSystemHealth()
  ])
  
  // Sumar resultados
  results.forEach(result => {
    totalPassed += result.passed
    totalFailed += result.failed
  })
  
  // Mostrar resumen final
  log('\n📊 RESUMEN FINAL', 'bold')
  log('=' * 20, 'blue')
  log(`✅ Tests Exitosos: ${totalPassed}`, 'green')
  log(`❌ Tests Fallidos: ${totalFailed}`, totalFailed > 0 ? 'red' : 'green')
  log(`📈 Tasa de Éxito: ${((totalPassed / (totalPassed + totalFailed)) * 100).toFixed(1)}%`, 
      totalFailed === 0 ? 'green' : 'yellow')
  
  if (totalFailed === 0) {
    log('\n🎉 ¡TODOS LOS TESTS PASARON! La integración con Google Sheets está funcionando correctamente.', 'green')
  } else {
    log('\n⚠️  Algunos tests fallaron. Revisar logs para más detalles.', 'yellow')
  }
  
  return { totalPassed, totalFailed }
}

// Ejecutar tests si se llama directamente
if (require.main === module) {
  runAllTests()
    .then(({ totalPassed, totalFailed }) => {
      process.exit(totalFailed === 0 ? 0 : 1)
    })
    .catch(error => {
      log(`\n💥 Error fatal: ${error.message}`, 'red')
      process.exit(1)
    })
}

module.exports = {
  runAllTests,
  testGoogleSheetsConnection,
  testAddQuote,
  testSearchFunctionality,
  testSystemHealth
}
