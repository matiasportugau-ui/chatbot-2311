# 🚀 GUÍA SIMPLE N8N - BMC QUOTE SYSTEM

## ✅ ERRORES SOLUCIONADOS

1. ✅ Error de sintaxis en main-dashboard.tsx
2. ✅ Componente Table creado
3. ✅ Caché de Next.js limpiado
4. ✅ Workflow n8n válido creado
5. ✅ Docker Compose simplificado
6. ✅ Scripts de inicio y test creados
7. ✅ Servidor Next.js funcionando

## 🚀 COMANDOS PARA USAR

### 1. Iniciar n8n
./start-n8n.sh

### 2. Acceder a n8n
- URL: http://localhost:5678
- Usuario: admin
- Contraseña: bmc2024

### 3. Importar workflow
- Archivo: n8n-workflows/bmc-valid-workflow.json
- 3 nodos: Webhook → HTTP Request → Response

### 4. Probar
node test-n8n.js

## 📱 WEBHOOK

URL: http://localhost:5678/webhook/bmc-quote
Método: POST

Ejemplo:
curl -X POST http://localhost:5678/webhook/bmc-quote \
  -H "Content-Type: application/json" \
  -d "{\"body\":{\"message\":\"Test Isodec 100mm\",\"from\":\"+59812345678\"}}"

## 🎯 RESULTADO ESPERADO

{
  "success": true,
  "message": "Cotización procesada",
  "data": {
    "tipo": "cotizacion",
    "mensaje": "🏗️ COTIZACIÓN BMC...",
    "cotizacion": { ... }
  }
}

¡LISTO! Simple y funcional. 🚀
