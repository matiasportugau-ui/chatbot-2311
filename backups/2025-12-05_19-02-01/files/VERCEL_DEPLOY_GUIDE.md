# 🚀 Instrucciones de Deploy en Vercel

## Opción 1: Deploy desde GitHub (RECOMENDADO)

### 1. Preparar repositorio
```bash
# Asegúrate de que todo esté commiteado
git add .
git commit -m "🚀 Ready for Vercel deploy"
git push origin main
```

### 2. Conectar con Vercel
1. Ve a https://vercel.com
2. Inicia sesión con GitHub
3. Click "New Project"
4. Selecciona tu repositorio: `bmc-cotizacion-inteligente`
5. Framework: Next.js (detectado automáticamente)
6. Click "Deploy"

### 3. Configurar variables de entorno
1. En Vercel Dashboard → Settings → Environment Variables
2. Agrega todas las variables del archivo `vercel-env-template.txt`
3. **IMPORTANTE**: Para `GOOGLE_PRIVATE_KEY`, escapa los \n correctamente
4. Click "Save"

### 4. Verificar deploy
1. Ve a tu dominio: https://tu-app.vercel.app
2. Prueba: https://tu-app.vercel.app/api/health
3. Verifica dashboard: https://tu-app.vercel.app

---

## Opción 2: Deploy con Vercel CLI

### 1. Instalar Vercel CLI
```bash
npm i -g vercel
```

### 2. Login y deploy
```bash
vercel login
vercel --prod
```

### 3. Configurar variables
```bash
vercel env add OPENAI_API_KEY
vercel env add GOOGLE_SHEET_ID
vercel env add GOOGLE_SERVICE_ACCOUNT_EMAIL
vercel env add GOOGLE_PRIVATE_KEY
vercel env add MONGODB_URI
vercel env add NEXT_PUBLIC_APP_URL
```

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
- Verifica que todas las dependencias estén en `package.json`
- Ejecuta `npm install` localmente

### Error: "Environment variables not found"
- Verifica que todas las variables estén en Vercel Dashboard
- Revisa que los nombres coincidan exactamente

### Error: "Google Sheets API"
- Verifica que el Service Account tenga acceso al Sheet
- Revisa que `GOOGLE_PRIVATE_KEY` esté correctamente escapado

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
