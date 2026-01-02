#!/usr/bin/env node
const axios = require("axios")

const colors = {
  green: "\x1b[32m",
  red: "\x1b[31m",
  yellow: "\x1b[33m",
  blue: "\x1b[34m",
  reset: "\x1b[0m",
  bold: "\x1b[1m"
}

function log(message, color = "reset") {
  console.log(`${colors[color]}${message}${colors.reset}`)
}

async function testN8NWebhook() {
  log("\n🧪 Testing n8n Webhook", "bold")
  log("=" * 30, "blue")
  
  const webhookUrl = "http://localhost:5678/webhook/bmc-quote"
  const testMessage = {
    body: {
      message: "Necesito cotizar Isodec 100mm para galpón de 50m2",
      from: "+59891234567"
    }
  }
  
  try {
    log(`📤 Enviando mensaje a: ${webhookUrl}`, "cyan")
    log(`📝 Mensaje: "${testMessage.body.message}"`, "cyan")
    
    const response = await axios.post(webhookUrl, testMessage, {
      timeout: 10000,
      headers: { "Content-Type": "application/json" }
    })
    
    log(`✅ Respuesta recibida:`, "green")
    log(`   Status: ${response.status}`, "blue")
    log(`   Data: ${JSON.stringify(response.data, null, 2)}`, "blue")
    
    return { success: true, response: response.data }
    
  } catch (error) {
    log(`❌ Error: ${error.message}`, "red")
    if (error.response) {
      log(`   Status: ${error.response.status}`, "red")
      log(`   Data: ${JSON.stringify(error.response.data, null, 2)}`, "red")
    }
    return { success: false, error: error.message }
  }
}

async function runTests() {
  log("🚀 Iniciando Tests SIMPLES", "bold")
  log("=" * 30, "blue")
  
  const result = await testN8NWebhook()
  
  if (result.success) {
    log("\n🎉 ¡TEST EXITOSO!", "green")
    log("El workflow n8n está funcionando correctamente.", "green")
  } else {
    log("\n⚠️  Test falló", "yellow")
    log("Revisar configuración de n8n", "yellow")
  }
}

if (require.main === module) {
  runTests()
    .then(() => process.exit(0))
    .catch(error => {
      log(`💥 Error fatal: ${error.message}`, "red")
      process.exit(1)
    })
}

module.exports = { testN8NWebhook, runTests }
