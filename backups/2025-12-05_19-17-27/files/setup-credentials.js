#!/usr/bin/env node

/**
 * 🔐 Script para configurar credenciales
 * Copia el template y permite editar las credenciales
 */

const fs = require('fs');
const path = require('path');
const colors = require('colors');

console.log('🔐 CONFIGURANDO CREDENCIALES DEL SISTEMA BMC\n'.cyan.bold);

function setupCredentials() {
  const templatePath = path.join(process.cwd(), 'credentials-template.json');
  const credentialsPath = path.join(process.cwd(), 'credentials.json');
  
  try {
    // Verificar si el template existe
    if (!fs.existsSync(templatePath)) {
      console.log('❌ credentials-template.json no encontrado'.red);
      return false;
    }
    
    // Leer template
    const template = fs.readFileSync(templatePath, 'utf8');
    
    // Copiar template a credentials.json
    fs.writeFileSync(credentialsPath, template);
    console.log('✅ credentials.json creado desde template'.green);
    
    console.log('\n📋 PRÓXIMOS PASOS:'.yellow.bold);
    console.log('1. Edita credentials.json con tus credenciales reales'.blue);
    console.log('2. Para Google Sheets:'.blue);
    console.log('   - Crea Service Account en Google Cloud Console'.gray);
    console.log('   - Descarga JSON y copia email y private_key'.gray);
    console.log('   - Comparte el Sheet con el email del Service Account'.gray);
    console.log('3. Para MongoDB:'.blue);
    console.log('   - Crea cluster en MongoDB Atlas'.gray);
    console.log('   - Copia la connection string'.gray);
    console.log('4. Ejecuta: node start-mvp.js'.blue);
    
    console.log('\n📁 Archivos:'.yellow);
    console.log(`   Template: ${templatePath}`.gray);
    console.log(`   Credenciales: ${credentialsPath}`.gray);
    
    return true;
  } catch (error) {
    console.log('❌ Error configurando credenciales:', error.message.red);
    return false;
  }
}

setupCredentials();
