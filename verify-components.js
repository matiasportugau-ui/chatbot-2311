#!/usr/bin/env node

/**
 * 🔍 Verificador de Componentes del Sistema BMC
 * Verifica que todos los archivos y dependencias estén presentes
 */

const fs = require('fs');
const path = require('path');
const colors = require('colors');

console.log('🔍 VERIFICANDO COMPONENTES DEL SISTEMA BMC\n'.cyan.bold);

const requiredFiles = [
  // API Routes
  'src/app/api/health/route.ts',
  'src/app/api/integrated-quote/route.ts',
  'src/app/api/parse-quote/route.ts',
  'src/app/api/sheets/enhanced-sync/route.ts',
  
  // Libraries
  'src/lib/google-sheets-enhanced.ts',
  'src/lib/quote-parser.ts',
  'src/lib/integrated-quote-engine.ts',
  'src/lib/initialize-system.ts',
  
  // Components
  'src/components/dashboard/main-dashboard.tsx',
  'src/components/dashboard/google-sheets-dashboard.tsx',
  'src/components/dashboard/integrated-system-metrics.tsx',
  'src/components/chat/bmc-chat-interface.tsx',
  'src/components/ui/table.tsx',
  
  // Configuration
  'package.json',
  'next.config.js',
  'tailwind.config.js',
  'tsconfig.json',
  '.gitignore',
  
  // Documentation
  'SETUP_CREDENTIALS_GUIDE.md',
  'README.md'
];

const requiredDependencies = [
  'next',
  'react',
  'react-dom',
  'typescript',
  'tailwindcss',
  'openai',
  'googleapis',
  'mongodb',
  'mongoose',
  'axios',
  'lucide-react',
  'recharts'
];

function checkFile(filePath) {
  const fullPath = path.join(process.cwd(), filePath);
  const exists = fs.existsSync(fullPath);
  
  if (exists) {
    console.log(`   ✅ ${filePath}`.green);
    return true;
  } else {
    console.log(`   ❌ ${filePath}`.red);
    return false;
  }
}

function checkDependency(dep) {
  try {
    require.resolve(dep);
    console.log(`   ✅ ${dep}`.green);
    return true;
  } catch (error) {
    console.log(`   ❌ ${dep}`.red);
    return false;
  }
}

function checkEnvFile() {
  const envPath = path.join(process.cwd(), '.env.local');
  const exists = fs.existsSync(envPath);
  
  if (exists) {
    console.log('   ✅ .env.local existe'.green);
    
    // Verificar contenido básico
    const content = fs.readFileSync(envPath, 'utf8');
    const hasOpenAI = content.includes('OPENAI_API_KEY=');
    const hasGoogle = content.includes('GOOGLE_SERVICE_ACCOUNT_EMAIL=');
    const hasMongo = content.includes('MONGODB_URI=');
    
    console.log(`   📊 OpenAI configurado: ${hasOpenAI ? '✅' : '❌'}`);
    console.log(`   📊 Google configurado: ${hasGoogle ? '✅' : '❌'}`);
    console.log(`   📊 MongoDB configurado: ${hasMongo ? '✅' : '❌'}`);
    
    return hasOpenAI && hasGoogle && hasMongo;
  } else {
    console.log('   ❌ .env.local no existe'.red);
    return false;
  }
}

async function verifyComponents() {
  console.log('📁 Verificando archivos requeridos...'.yellow);
  let filesOk = 0;
  
  requiredFiles.forEach(file => {
    if (checkFile(file)) filesOk++;
  });
  
  console.log(`\n📦 Verificando dependencias...`.yellow);
  let depsOk = 0;
  
  requiredDependencies.forEach(dep => {
    if (checkDependency(dep)) depsOk++;
  });
  
  console.log(`\n🔐 Verificando configuración...`.yellow);
  const envOk = checkEnvFile();
  
  // Resumen
  console.log('\n' + '='.repeat(50).cyan);
  console.log('📊 RESUMEN DE VERIFICACIÓN'.cyan.bold);
  console.log('='.repeat(50).cyan);
  
  console.log(`📁 Archivos: ${filesOk}/${requiredFiles.length} (${Math.round(filesOk/requiredFiles.length*100)}%)`);
  console.log(`📦 Dependencias: ${depsOk}/${requiredDependencies.length} (${Math.round(depsOk/requiredDependencies.length*100)}%)`);
  console.log(`🔐 Configuración: ${envOk ? '✅' : '❌'}`);
  
  const totalScore = (filesOk + depsOk + (envOk ? 1 : 0)) / (requiredFiles.length + requiredDependencies.length + 1);
  
  if (totalScore >= 0.9) {
    console.log('\n🎉 ¡SISTEMA COMPLETO Y LISTO!'.green.bold);
    console.log('🚀 Puedes proceder con testing y deploy'.green);
  } else if (totalScore >= 0.7) {
    console.log('\n⚠️ Sistema casi listo'.yellow.bold);
    console.log('🔧 Revisa los elementos faltantes'.yellow);
  } else {
    console.log('\n❌ Sistema incompleto'.red.bold);
    console.log('🔧 Configura los elementos faltantes antes de continuar'.red);
  }
  
  console.log('\n📋 Próximos pasos:');
  if (!envOk) {
    console.log('   1. Configura .env.local siguiendo SETUP_CREDENTIALS_GUIDE.md'.blue);
  }
  console.log('   2. Ejecuta: npm run dev'.blue);
  console.log('   3. Ejecuta: node test-complete-system.js'.blue);
  console.log('   4. Deploy a Vercel'.blue);
}

verifyComponents().catch(console.error);
