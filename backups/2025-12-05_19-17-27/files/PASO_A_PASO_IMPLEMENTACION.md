# Paso a Paso - Implementación y Pruebas MercadoLibre

Esta guía te lleva paso a paso para implementar y probar las mejoras de MercadoLibre.

## 📋 Pre-requisitos

Antes de empezar, verifica que tienes:

- [ ] Servidor Next.js funcionando (o capacidad de iniciarlo)
- [ ] Variables de entorno configuradas (al menos las básicas)
- [ ] Acceso a la terminal/consola
- [ ] Python 3.8+ instalado (para scripts Python)

---

## 🚀 PASO 1: Verificar que los cambios estén aplicados

### 1.1 Verificar archivos nuevos

```bash
# Navega al directorio del proyecto
cd /Users/matias/chatbot2511/chatbot-2311

# Verifica que existan los archivos nuevos
ls -la src/lib/mercado-libre/config-validator.ts
ls -la src/app/api/mercado-libre/config/status/route.ts
ls -la MERCADOLIBRE_ENV.md
```

**✅ Si los archivos existen:** Continúa al Paso 2  
**❌ Si faltan archivos:** Los cambios no se aplicaron correctamente

### 1.2 Verificar cambios en archivos existentes

```bash
# Verifica que el cliente use el validador
grep -n "validateMercadoLibreConfig" src/lib/mercado-libre/client.ts

# Verifica que los scripts Python usen MERCADO_LIBRE_*
grep -n "MERCADO_LIBRE" python-scripts/fetch_mercadolibre_questions.py | head -5
```

**✅ Deberías ver referencias a `validateMercadoLibreConfig` y `MERCADO_LIBRE`**

---

## 🔧 PASO 2: Configurar Variables de Entorno

### 2.1 Revisar variables actuales

```bash
# Verifica qué variables tienes configuradas
grep -E "MERCADO_LIBRE_|MELI_" .env.local 2>/dev/null || grep -E "MERCADO_LIBRE_|MELI_" .env 2>/dev/null
```

### 2.2 Migrar a variables estandarizadas (opcional pero recomendado)

Si tienes variables `MELI_*`, puedes migrarlas:

```bash
# Opción 1: Agregar MERCADO_LIBRE_* manteniendo MELI_* (compatibilidad)
# Edita tu .env.local y agrega:
MERCADO_LIBRE_ACCESS_TOKEN=${MELI_ACCESS_TOKEN}
MERCADO_LIBRE_REFRESH_TOKEN=${MELI_REFRESH_TOKEN}
MERCADO_LIBRE_SELLER_ID=${MELI_SELLER_ID}

# Opción 2: Renombrar directamente (si estás seguro)
# Simplemente renombra MELI_* a MERCADO_LIBRE_* en tu .env
```

**📝 Nota:** Las variables `MELI_*` seguirán funcionando, pero recibirás un warning.

### 2.3 Verificar variables requeridas

Asegúrate de tener estas variables mínimas:

```env
MERCADO_LIBRE_APP_ID=tu_app_id
MERCADO_LIBRE_CLIENT_SECRET=tu_client_secret
MERCADO_LIBRE_REDIRECT_URI=http://localhost:3000/api/mercado-libre/auth/callback
MERCADO_LIBRE_SELLER_ID=tu_seller_id
```

**✅ Si tienes estas 4 variables:** Continúa al Paso 3  
**❌ Si faltan:** Configúralas antes de continuar

---

## 🧪 PASO 3: Probar el Endpoint de Verificación (MÁS FÁCIL)

Este es el paso más rápido para verificar que todo funciona.

### 3.1 Iniciar el servidor (si no está corriendo)

```bash
# En una terminal
cd /Users/matias/chatbot2511/chatbot-2311
npm run dev
```

Espera a ver: `✓ Ready on http://localhost:3000`

### 3.2 Probar el endpoint de status

**Opción A: Desde el navegador (más fácil)**
```
1. Abre tu navegador
2. Ve a: http://localhost:3000/api/mercado-libre/config/status
3. Deberías ver un JSON con el estado de tu configuración
```

**Opción B: Desde terminal**
```bash
curl http://localhost:3000/api/mercado-libre/config/status | jq
```

### 3.3 Interpretar la respuesta

**✅ Si ves `"isValid": true`:**
```json
{
  "config": {
    "isValid": true,
    "errors": [],
    "configured": ["MERCADO_LIBRE_APP_ID", ...]
  }
}
```
**→ ¡Perfecto! Tu configuración es válida. Continúa al Paso 4.**

**❌ Si ves `"isValid": false`:**
```json
{
  "config": {
    "isValid": false,
    "errors": ["Variable requerida faltante: MERCADO_LIBRE_APP_ID"],
    "missing": ["MERCADO_LIBRE_APP_ID"]
  }
}
```
**→ Configura las variables faltantes y vuelve a probar.**

**⚠️ Si ves warnings sobre `MELI_*`:**
```json
{
  "warnings": ["Se detectaron variables con prefijo MELI_*..."]
}
```
**→ No es crítico, pero considera migrar a `MERCADO_LIBRE_*`**

---

## 📊 PASO 4: Verificar Logging Mejorado

### 4.1 Probar logging en TypeScript

**Método 1: Usar el dashboard (si tienes uno)**
```
1. Abre el dashboard de MercadoLibre en tu app
2. Intenta sincronizar órdenes o publicaciones
3. Observa la consola del servidor (donde corre `npm run dev`)
4. Deberías ver logs estructurados como:
   [MercadoLibre] Solicitando token (grant_type: refresh_token) {...}
```

**Método 2: Llamar API directamente**
```bash
# Intenta sincronizar órdenes (requiere autenticación)
curl -X POST http://localhost:3000/api/mercado-libre/orders/sync \
  -H "Content-Type: application/json" \
  -d '{"limit": 10}'
```

**Observa la consola del servidor** - deberías ver logs con contexto completo.

### 4.2 Probar logging en Python

```bash
# Ejecuta el script de sincronización
python python-scripts/fetch_mercadolibre_questions.py
```

**✅ Deberías ver:**
```
2025-01-27 12:00:00 - __main__ - INFO - Iniciando sincronización de preguntas de MercadoLibre
2025-01-27 12:00:00 - __main__ - INFO - Sincronizando desde API: https://api.mercadolibre.com
2025-01-27 12:00:00 - __main__ - INFO - Seller ID: 123456789
...
```

**❌ Si no ves logs:** Verifica que tengas las variables de entorno configuradas.

---

## 🔄 PASO 5: Probar Compatibilidad de Variables

### 5.1 Probar con variables legacy (MELI_*)

```bash
# Temporalmente, configura solo variables MELI_*
export MELI_ACCESS_TOKEN="tu_token_si_lo_tienes"
export MELI_SELLER_ID="tu_seller_id"

# Ejecuta el script
python python-scripts/fetch_mercadolibre_questions.py
```

**✅ Debería funcionar** (con un warning en el endpoint de status)

### 5.2 Probar con variables nuevas (MERCADO_LIBRE_*)

```bash
# Configura variables nuevas
export MERCADO_LIBRE_ACCESS_TOKEN="tu_token"
export MERCADO_LIBRE_SELLER_ID="tu_seller_id"

# Ejecuta el script
python python-scripts/fetch_mercadolibre_questions.py
```

**✅ Debería funcionar sin warnings**

### 5.3 Probar OAuth Helper

```bash
# Si necesitas generar tokens nuevos
python python-scripts/mercadolibre_oauth_helper.py --print-url

# Sigue las instrucciones para obtener el código
# Luego:
python python-scripts/mercadolibre_oauth_helper.py --code TU_CODIGO --output-env .env.local
```

**✅ Verifica que `.env.local` tenga ambas versiones de variables**

---

## 🎯 PASO 6: Prueba Completa End-to-End

### 6.1 Checklist de verificación

Ejecuta estos comandos y verifica cada uno:

```bash
# 1. Verificar configuración
curl http://localhost:3000/api/mercado-libre/config/status | jq '.data.config.isValid'
# Debería retornar: true

# 2. Verificar conexión OAuth
curl http://localhost:3000/api/mercado-libre/config/status | jq '.data.connection.connected'
# Debería retornar: true (si ya completaste OAuth)

# 3. Probar script Python
python python-scripts/fetch_mercadolibre_questions.py
# Debería ejecutarse sin errores (o con errores de autenticación si no tienes token válido)

# 4. Verificar logs en consola del servidor
# Deberías ver logs estructurados cuando hay actividad
```

### 6.2 Probar manejo de errores

```bash
# Temporalmente configura un token inválido
export MERCADO_LIBRE_ACCESS_TOKEN="token_invalido"

# Intenta usar la API
curl -X POST http://localhost:3000/api/mercado-libre/orders/sync \
  -H "Content-Type: application/json" \
  -d '{"limit": 10}'

# Observa los logs del servidor
# Deberías ver errores estructurados con contexto completo
```

---

## 🐛 Solución de Problemas Comunes

### Problema: "Cannot find module './config-validator'"

**Solución:**
```bash
# Verifica que el archivo existe
ls -la src/lib/mercado-libre/config-validator.ts

# Si no existe, los cambios no se aplicaron. Verifica el estado del repositorio.
```

### Problema: Endpoint de status retorna 404

**Solución:**
```bash
# Verifica que la ruta sea correcta
ls -la src/app/api/mercado-libre/config/status/route.ts

# Reinicia el servidor Next.js
# Ctrl+C para detener, luego:
npm run dev
```

### Problema: "Missing environment variable"

**Solución:**
```bash
# Verifica qué variables faltan
curl http://localhost:3000/api/mercado-libre/config/status | jq '.data.config.missing'

# Agrega las variables faltantes a tu .env.local
# Reinicia el servidor
```

### Problema: Scripts Python no encuentran variables

**Solución:**
```bash
# Verifica que las variables estén exportadas o en .env
echo $MERCADO_LIBRE_ACCESS_TOKEN

# O carga desde .env
export $(cat .env.local | grep MERCADO_LIBRE | xargs)
```

---

## ✅ Checklist Final

Marca cada item cuando esté funcionando:

- [ ] Endpoint `/api/mercado-libre/config/status` responde
- [ ] Configuración se valida correctamente
- [ ] Logs estructurados aparecen en consola (TypeScript)
- [ ] Logs detallados aparecen en scripts Python
- [ ] Variables `MELI_*` funcionan (compatibilidad)
- [ ] Variables `MERCADO_LIBRE_*` funcionan
- [ ] OAuth helper guarda ambas versiones
- [ ] Errores muestran contexto completo

---

## 🎉 ¡Listo!

Si todos los pasos funcionan, las mejoras están completamente implementadas y funcionando.

**Próximos pasos sugeridos:**
1. Migrar completamente a `MERCADO_LIBRE_*` (eliminar `MELI_*`)
2. Usar el endpoint de status en tu dashboard para mostrar estado de conexión
3. Monitorear los logs mejorados para debugging

---

## 📞 ¿Necesitas ayuda?

Si algo no funciona:
1. Revisa los logs del servidor
2. Usa el endpoint de status para diagnosticar
3. Verifica que todos los archivos estén en su lugar
4. Consulta `MERCADOLIBRE_ENV.md` para detalles de configuración

