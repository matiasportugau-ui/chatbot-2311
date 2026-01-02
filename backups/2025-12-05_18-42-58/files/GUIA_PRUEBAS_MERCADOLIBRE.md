# Guía de Pruebas - Mejoras MercadoLibre

Esta guía te ayudará a probar las mejoras implementadas en la integración con MercadoLibre.

## ✅ Verificación Rápida

### 1. Verificar Configuración (Nuevo Endpoint)

El nuevo endpoint te permite verificar el estado de tu configuración:

```bash
# Desde la terminal
curl http://localhost:3000/api/mercado-libre/config/status

# O desde el navegador
# Abre: http://localhost:3000/api/mercado-libre/config/status
```

**Respuesta esperada:**
```json
{
  "success": true,
  "data": {
    "config": {
      "isValid": true,
      "errors": [],
      "warnings": [],
      "missing": [],
      "configured": [
        "MERCADO_LIBRE_APP_ID",
        "MERCADO_LIBRE_CLIENT_SECRET",
        "MERCADO_LIBRE_REDIRECT_URI",
        "MERCADO_LIBRE_SELLER_ID"
      ],
      "summary": "✅ Configuración válida (4 variables configuradas)"
    },
    "connection": {
      "connected": true,
      "expiresAt": "2025-01-28T10:00:00.000Z",
      "scope": ["offline_access", "read", "write"],
      "sellerId": "123456789",
      "userId": 123456789
    },
    "timestamp": "2025-01-27T12:00:00.000Z"
  }
}
```

### 2. Probar Validación de Configuración

Si falta alguna variable, verás errores claros:

```bash
# Temporalmente renombra una variable para probar
# En tu .env, comenta: MERCADO_LIBRE_APP_ID

# Luego verifica:
curl http://localhost:3000/api/mercado-libre/config/status
```

Deberías ver:
```json
{
  "config": {
    "isValid": false,
    "errors": [
      "Variable requerida faltante: MERCADO_LIBRE_APP_ID - ID de la aplicación en MercadoLibre"
    ],
    "missing": ["MERCADO_LIBRE_APP_ID"]
  }
}
```

### 3. Probar Logging Mejorado

#### En TypeScript (Cliente)

1. **Inicia tu servidor Next.js:**
```bash
npm run dev
```

2. **Intenta usar cualquier endpoint de MercadoLibre** (por ejemplo, sincronizar órdenes)

3. **Revisa los logs en la consola** - deberías ver logs estructurados como:
```
[MercadoLibre] Solicitando token (grant_type: refresh_token) {
  "service": "mercadolibre",
  "timestamp": "2025-01-27T12:00:00.000Z",
  "endpoint": "/oauth/token",
  "grantType": "refresh_token",
  "sellerId": "123456789"
}
```

#### En Python (Scripts)

1. **Ejecuta el script de sincronización:**
```bash
python python-scripts/fetch_mercadolibre_questions.py
```

2. **Deberías ver logs detallados:**
```
2025-01-27 12:00:00 - __main__ - INFO - Iniciando sincronización de preguntas de MercadoLibre
2025-01-27 12:00:00 - __main__ - INFO - Sincronizando desde API: https://api.mercadolibre.com
2025-01-27 12:00:00 - __main__ - INFO - Seller ID: 123456789
2025-01-27 12:00:00 - __main__ - INFO - Iniciando fetch de preguntas (limit por página: 50)
2025-01-27 12:00:01 - __main__ - INFO - Página 1: 25 preguntas obtenidas (total acumulado: 25)
```

### 4. Probar Estandarización de Variables

#### Compatibilidad hacia atrás

Las variables `MELI_*` siguen funcionando, pero se recomienda usar `MERCADO_LIBRE_*`:

```bash
# Prueba con variables legacy (debería funcionar)
export MELI_ACCESS_TOKEN="tu_token"
export MELI_SELLER_ID="tu_seller_id"
python python-scripts/fetch_mercadolibre_questions.py

# Prueba con variables nuevas (recomendado)
export MERCADO_LIBRE_ACCESS_TOKEN="tu_token"
export MERCADO_LIBRE_SELLER_ID="tu_seller_id"
python python-scripts/fetch_mercadolibre_questions.py
```

Ambos deberían funcionar. El script prioriza `MERCADO_LIBRE_*` si ambas están presentes.

### 5. Probar OAuth Helper

El helper ahora guarda ambas versiones de variables:

```bash
# Genera tokens y guarda en .env.local
python python-scripts/mercadolibre_oauth_helper.py --code TU_CODIGO --output-env .env.local
```

Verifica que el archivo `.env.local` contenga:
```env
MERCADO_LIBRE_ACCESS_TOKEN=tu_token
MERCADO_LIBRE_REFRESH_TOKEN=tu_refresh_token
MERCADO_LIBRE_SELLER_ID=tu_seller_id
MELI_ACCESS_TOKEN=tu_token
MELI_REFRESH_TOKEN=tu_refresh_token
MELI_SELLER_ID=tu_seller_id
```

### 6. Probar Manejo de Errores Mejorado

#### Probar con token inválido

1. **Configura un token inválido temporalmente:**
```bash
export MERCADO_LIBRE_ACCESS_TOKEN="token_invalido"
```

2. **Intenta sincronizar órdenes desde el dashboard o API:**
```bash
curl -X POST http://localhost:3000/api/mercado-libre/orders/sync \
  -H "Content-Type: application/json" \
  -d '{"limit": 10}'
```

3. **Revisa los logs** - deberías ver errores estructurados con contexto completo:
```
[MercadoLibre Orders] Error en POST sync: {
  "action": "sync",
  "method": "POST",
  "url": "http://localhost:3000/api/mercado-libre/orders/sync",
  "body": {"limit": 10},
  "error": "Token de Mercado Libre inválido o expirado",
  "details": {...}
}
```

## 🧪 Checklist de Pruebas

- [ ] Endpoint `/api/mercado-libre/config/status` responde correctamente
- [ ] Validación detecta variables faltantes
- [ ] Logs estructurados aparecen en consola (TypeScript)
- [ ] Logs detallados aparecen en scripts Python
- [ ] Variables `MELI_*` siguen funcionando (compatibilidad)
- [ ] Variables `MERCADO_LIBRE_*` funcionan correctamente
- [ ] OAuth helper guarda ambas versiones de variables
- [ ] Errores muestran contexto completo en logs
- [ ] Códigos de estado HTTP son apropiados (401 para auth, 400 para validación, etc.)

## 🔍 Verificación de Archivos

Verifica que estos archivos existan y estén actualizados:

```bash
# Validador de configuración
ls -la src/lib/mercado-libre/config-validator.ts

# Cliente actualizado
grep -n "validateMercadoLibreConfig" src/lib/mercado-libre/client.ts

# Endpoint de status
ls -la src/app/api/mercado-libre/config/status/route.ts

# Scripts Python actualizados
grep -n "MERCADO_LIBRE" python-scripts/fetch_mercadolibre_questions.py
grep -n "MERCADO_LIBRE" python-scripts/mercadolibre_oauth_helper.py

# Documentación
ls -la MERCADOLIBRE_ENV.md
```

## 🚀 Prueba Completa End-to-End

1. **Verifica configuración:**
```bash
curl http://localhost:3000/api/mercado-libre/config/status | jq
```

2. **Sincroniza preguntas (si tienes tokens):**
```bash
python python-scripts/fetch_mercadolibre_questions.py
```

3. **Revisa logs en consola del servidor Next.js** mientras usas el dashboard

4. **Intenta sincronizar órdenes desde el dashboard** y observa los logs mejorados

## 📝 Notas

- Los logs mejorados solo aparecen cuando hay actividad (no en idle)
- El endpoint de status es seguro y no expone información sensible
- Las variables legacy (`MELI_*`) seguirán funcionando pero generarán warnings
- Todos los cambios son retrocompatibles

## ❓ Solución de Problemas

### El endpoint de status no responde

**Verifica:**
- Que el servidor Next.js esté corriendo
- Que la ruta esté correcta: `/api/mercado-libre/config/status`
- Revisa los logs del servidor para errores

### Los logs no aparecen

**Verifica:**
- Que estés ejecutando acciones que usen MercadoLibre
- Que el nivel de logging esté configurado correctamente
- Revisa la consola del servidor (no solo el navegador)

### Variables no se reconocen

**Verifica:**
- Que estén en el archivo `.env` o `.env.local` correcto
- Que el servidor se haya reiniciado después de cambiar variables
- Usa el endpoint de status para ver qué variables faltan

