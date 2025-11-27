#!/usr/bin/env node

/**
 * 🚀 Preparador para Deploy en Vercel
 * Verifica configuración y prepara el proyecto para producción
 */

const fs = require('fs');
const path = require('path');
const colors = require('colors');

console.log('🚀 PREPARANDO DEPLOY EN VERCEL\n'.cyan.bold);

function createVercelConfig() {
  console.log('📝 Creando vercel.json...'.yellow);
  
  const vercelConfig = {
    "buildCommand": "npm run build",
    "devCommand": "npm run dev",
    "installCommand": "npm install",
    "framework": "nextjs",
    "regions": ["gru1"],
    "functions": {
      "src/app/api/**/*.ts": {
        "maxDuration": 30
      }
    },
    "env": {
      "NODE_ENV": "production"
    }
  };
  
  fs.writeFileSync('vercel.json', JSON.stringify(vercelConfig, null, 2));
  console.log('   ✅ vercel.json creado'.green);
}

function createEnvTemplate() {
  console.log('📝 Creando template de variables de entorno...'.yellow);
  
  const envTemplate = `# 🔐 Variables de Entorno para Vercel
# Copia estas variables en Vercel Dashboard → Settings → Environment Variables

# OpenAI API
OPENAI_API_KEY=sk-proj-...

# Google Sheets API
GOOGLE_SHEET_ID=1bs467N7FbLSHI7LpNor3wqrPZC9snqPphft8cEPHHl0
GOOGLE_SERVICE_ACCOUNT_EMAIL=bmc-sheets-service@proyecto.iam.gserviceaccount.com
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n"

# MongoDB Atlas
MONGODB_URI=mongodb+srv://bmcadmin:password@cluster.mongodb.net/

# URLs
NODE_ENV=production
NEXT_PUBLIC_APP_URL=https://tu-app.vercel.app

# Mercado Libre OAuth / API
MERCADO_LIBRE_APP_ID=tu-app-id
MERCADO_LIBRE_CLIENT_SECRET=tu-client-secret
MERCADO_LIBRE_REDIRECT_URI=https://tu-app.vercel.app/api/mercado-libre/auth/callback
MERCADO_LIBRE_SELLER_ID=tu-seller-id
MERCADO_LIBRE_WEBHOOK_SECRET=
# IMPORTANTE: MERCADO_LIBRE_AUTH_URL debe coincidir con la región donde registraste la app
# Argentina: https://auth.mercadolibre.com.ar
# México: https://auth.mercadolibre.com.mx
# Uruguay: https://auth.mercadolibre.com.uy
# Brasil: https://auth.mercadolibre.com.br
# Chile: https://auth.mercadolibre.com.cl
# Colombia: https://auth.mercadolibre.com.co
# Perú: https://auth.mercadolibre.com.pe
MERCADO_LIBRE_AUTH_URL=https://auth.mercadolibre.com.uy
MERCADO_LIBRE_API_URL=https://api.mercadolibre.com
MERCADO_LIBRE_SCOPES=offline_access read write
MERCADO_LIBRE_PKCE_ENABLED=true

# WhatsApp Business API (Opcional)
WHATSAPP_ACCESS_TOKEN=pendiente
WHATSAPP_PHONE_NUMBER_ID=pendiente
WHATSAPP_VERIFY_TOKEN=bmc_whatsapp_verify_2024

# N8N Integration (Opcional)
N8N_WEBHOOK_URL=https://tu-n8n.vercel.app/webhook/whatsapp-message
`;
  
  fs.writeFileSync('vercel-env-template.txt', envTemplate);
  console.log('   ✅ vercel-env-template.txt creado'.green);
}

function checkBuild() {
  console.log('🔨 Verificando build...'.yellow);
  
  try {
    // Verificar que package.json tiene scripts necesarios
    const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
    
    if (!packageJson.scripts.build) {
      console.log('   ❌ Script "build" no encontrado en package.json'.red);
      return false;
    }
    
    if (!packageJson.scripts.start) {
      console.log('   ❌ Script "start" no encontrado en package.json'.red);
      return false;
    }
    
    console.log('   ✅ Scripts de build configurados'.green);
    return true;
  } catch (error) {
    console.log('   ❌ Error leyendo package.json:', error.message.red);
    return false;
  }
}

function createDeployInstructions() {
  console.log('📋 Creando instrucciones de deploy...'.yellow);
  
  const instructions = `# 🚀 Instrucciones de Deploy en Vercel

## Opción 1: Deploy desde GitHub (RECOMENDADO)

### 1. Preparar repositorio
\`\`\`bash
# Asegúrate de que todo esté commiteado
git add .
git commit -m "🚀 Ready for Vercel deploy"
git push origin main
\`\`\`

### 2. Conectar con Vercel
1. Ve a https://vercel.com
2. Inicia sesión con GitHub
3. Click "New Project"
4. Selecciona tu repositorio: \`bmc-cotizacion-inteligente\`
5. Framework: Next.js (detectado automáticamente)
6. Click "Deploy"

### 3. Configurar variables de entorno
1. En Vercel Dashboard → Settings → Environment Variables
2. Agrega todas las variables del archivo \`vercel-env-template.txt\`
3. **IMPORTANTE**: Para \`GOOGLE_PRIVATE_KEY\`, escapa los \\n correctamente
4. Click "Save"

### 4. Verificar deploy
1. Ve a tu dominio: https://tu-app.vercel.app
2. Prueba: https://tu-app.vercel.app/api/health
3. Verifica dashboard: https://tu-app.vercel.app

---

## Opción 2: Deploy con Vercel CLI

### 1. Instalar Vercel CLI
\`\`\`bash
npm i -g vercel
\`\`\`

### 2. Login y deploy
\`\`\`bash
vercel login
vercel --prod
\`\`\`

### 3. Configurar variables
\`\`\`bash
vercel env add OPENAI_API_KEY
vercel env add GOOGLE_SHEET_ID
vercel env add GOOGLE_SERVICE_ACCOUNT_EMAIL
vercel env add GOOGLE_PRIVATE_KEY
vercel env add MONGODB_URI
vercel env add NEXT_PUBLIC_APP_URL
\`\`\`

---

## ✅ Checklist Post-Deploy

- [ ] Dashboard accesible en producción
- [ ] Health check responde correctamente
- [ ] Google Sheets sincroniza datos
- [ ] Sistema integrado procesa consultas
- [ ] Chat interface funciona
- [ ] No hay errores en logs de Vercel

---

## 🔧 Troubleshooting

### Error: "Module not found"
- Verifica que todas las dependencias estén en \`package.json\`
- Ejecuta \`npm install\` localmente

### Error: "Environment variables not found"
- Verifica que todas las variables estén en Vercel Dashboard
- Revisa que los nombres coincidan exactamente

### Error: "Google Sheets API"
- Verifica que el Service Account tenga acceso al Sheet
- Revisa que \`GOOGLE_PRIVATE_KEY\` esté correctamente escapado

### Error: "MongoDB connection"
- Verifica que la IP 0.0.0.0/0 esté en Network Access
- Revisa que el password no tenga caracteres especiales

---

## 📊 URLs Importantes

- **Dashboard**: https://tu-app.vercel.app
- **Health Check**: https://tu-app.vercel.app/api/health
- **Google Sheets API**: https://tu-app.vercel.app/api/sheets/enhanced-sync
- **Sistema Integrado**: https://tu-app.vercel.app/api/integrated-quote

---

## 🎯 Próximos Pasos

1. **Configurar WhatsApp Business** (Post-MVP)
2. **Implementar n8n workflows** (Opcional)
3. **Agregar métricas avanzadas**
4. **Implementar notificaciones**
5. **Optimizar performance**
`;
  
  fs.writeFileSync('VERCEL_DEPLOY_GUIDE.md', instructions);
  console.log('   ✅ VERCEL_DEPLOY_GUIDE.md creado'.green);
}

async function prepareVercel() {
  let allOk = true;
  
  // 1. Crear vercel.json
  createVercelConfig();
  
  // 2. Crear template de variables
  createEnvTemplate();
  
  // 3. Verificar build
  if (!checkBuild()) {
    allOk = false;
  }
  
  // 4. Crear instrucciones
  createDeployInstructions();
  
  // Resumen
  console.log('\n' + '='.repeat(50).cyan);
  console.log('📊 RESUMEN DE PREPARACIÓN'.cyan.bold);
  console.log('='.repeat(50).cyan);
  
  if (allOk) {
    console.log('🎉 ¡PROYECTO LISTO PARA VERCEL!'.green.bold);
    console.log('\n📋 Archivos creados:');
    console.log('   ✅ vercel.json'.green);
    console.log('   ✅ vercel-env-template.txt'.green);
    console.log('   ✅ VERCEL_DEPLOY_GUIDE.md'.green);
    
    console.log('\n🚀 Próximos pasos:');
    console.log('   1. Configura .env.local (si no lo has hecho)'.blue);
    console.log('   2. Ejecuta: npm run dev (para testing local)'.blue);
    console.log('   3. Ejecuta: node test-complete-system.js'.blue);
    console.log('   4. Sigue VERCEL_DEPLOY_GUIDE.md para deploy'.blue);
  } else {
    console.log('⚠️ Revisa los errores antes de continuar'.yellow.bold);
  }
}

prepareVercel().catch(console.error);

