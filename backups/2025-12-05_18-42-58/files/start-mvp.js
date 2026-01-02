#!/usr/bin/env node

/**
 * 🚀 Script Maestro - Inicio del MVP BMC
 * Ejecuta todo el proceso: verificación, testing, preparación para deploy
 */

const { execSync } = require('child_process');
const colors = require('colors');

console.log('🚀 INICIANDO MVP BMC - SCRIPT MAESTRO\n'.cyan.bold);
console.log('='.repeat(60).cyan);

async function runStep(stepName, command, description) {
  console.log(`\n${stepName}`.yellow.bold);
  console.log(`📝 ${description}`.blue);
  
  try {
    if (command) {
      console.log(`⚡ Ejecutando: ${command}`.gray);
      execSync(command, { stdio: 'inherit', cwd: process.cwd() });
    }
    console.log(`✅ ${stepName} completado`.green);
    return true;
  } catch (error) {
    console.log(`❌ ${stepName} falló: ${error.message}`.red);
    return false;
  }
}

async function checkServerRunning() {
  try {
    const { default: axios } = await import('axios');
    await axios.get('http://localhost:3000/api/health', { timeout: 2000 });
    return true;
  } catch (error) {
    return false;
  }
}

async function startMVPSystem() {
  console.log('🎯 OBJETIVO: Sistema BMC 100% funcional en producción HOY\n'.green.bold);
  
  // Paso 1: Verificar componentes
  const step1 = await runStep(
    '1️⃣ VERIFICACIÓN DE COMPONENTES',
    'node verify-components.js',
    'Verificando archivos, dependencias y configuración'
  );
  
  if (!step1) {
    console.log('\n❌ CRÍTICO: Componentes faltantes. Revisa verify-components.js'.red.bold);
    return;
  }
  
  // Paso 2: Preparar Vercel
  const step2 = await runStep(
    '2️⃣ PREPARACIÓN PARA VERCEL',
    'node prepare-vercel.js',
    'Creando configuración y guías para deploy'
  );
  
  // Paso 3: Verificar servidor
  console.log('\n3️⃣ VERIFICANDO SERVIDOR'.yellow.bold);
  const serverRunning = await checkServerRunning();
  
  if (!serverRunning) {
    console.log('📝 Iniciando servidor Next.js...'.blue);
    const step3 = await runStep(
      '   Iniciando servidor',
      'npm run dev &',
      'Servidor Next.js en background'
    );
    
    if (step3) {
      console.log('⏳ Esperando 10 segundos para que el servidor inicie...'.yellow);
      await new Promise(resolve => setTimeout(resolve, 10000));
    }
  } else {
    console.log('✅ Servidor ya está ejecutándose'.green);
  }
  
  // Paso 4: Testing completo
  const step4 = await runStep(
    '4️⃣ TESTING COMPLETO',
    'node test-complete-system.js',
    'Ejecutando tests de todos los componentes'
  );
  
  // Resumen final
  console.log('\n' + '='.repeat(60).cyan);
  console.log('📊 RESUMEN FINAL DEL MVP'.cyan.bold);
  console.log('='.repeat(60).cyan);
  
  const steps = [step1, step2, serverRunning || step3, step4];
  const passed = steps.filter(Boolean).length;
  
  console.log(`✅ Pasos completados: ${passed}/${steps.length}`);
  
  if (passed === steps.length) {
    console.log('\n🎉 ¡MVP COMPLETAMENTE FUNCIONAL!'.green.bold);
    console.log('\n🌐 URLs disponibles:');
    console.log('   📊 Dashboard: http://localhost:3000'.blue);
    console.log('   🔍 Health Check: http://localhost:3000/api/health'.blue);
    console.log('   📋 Google Sheets: http://localhost:3000/api/sheets/enhanced-sync'.blue);
    console.log('   🤖 Sistema Integrado: http://localhost:3000/api/integrated-quote'.blue);
    
    console.log('\n🚀 PRÓXIMOS PASOS:');
    console.log('   1. Revisa VERCEL_DEPLOY_GUIDE.md'.yellow);
    console.log('   2. Deploy a Vercel siguiendo las instrucciones'.yellow);
    console.log('   3. Configura variables de entorno en Vercel'.yellow);
    console.log('   4. ¡Sistema en producción! 🎉'.yellow);
    
  } else {
    console.log('\n⚠️ MVP parcialmente funcional'.yellow.bold);
    console.log('🔧 Revisa los pasos fallidos antes del deploy'.yellow);
  }
  
  console.log('\n📚 Documentación creada:');
  console.log('   📖 SETUP_CREDENTIALS_GUIDE.md - Configuración de credenciales');
  console.log('   🚀 VERCEL_DEPLOY_GUIDE.md - Guía de deploy');
  console.log('   🧪 test-complete-system.js - Testing completo');
  console.log('   🔍 verify-components.js - Verificación de componentes');
  
  console.log('\n💡 TIP: Si necesitas ayuda, revisa los archivos de documentación creados'.blue);
}

// Ejecutar sistema MVP
startMVPSystem().catch(console.error);


