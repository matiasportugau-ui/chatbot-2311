# Configuración de Variables de Entorno - MercadoLibre

Esta guía documenta todas las variables de entorno necesarias para la integración con MercadoLibre.

## Variables Requeridas

Estas variables son **obligatorias** y deben estar configuradas para que la integración funcione:

### `MERCADO_LIBRE_APP_ID`
- **Descripción:** ID de la aplicación registrada en MercadoLibre Developers
- **Ejemplo:** `1234567890123456`
- **Dónde obtenerlo:** [MercadoLibre Developers](https://developers.mercadolibre.com/) → Tu aplicación → Credenciales
- **Nota:** Debe coincidir con el `client_id` de tu aplicación

### `MERCADO_LIBRE_CLIENT_SECRET`
- **Descripción:** Client Secret de la aplicación (credencial confidencial)
- **Ejemplo:** `tu_client_secret_aqui`
- **Dónde obtenerlo:** [MercadoLibre Developers](https://developers.mercadolibre.com/) → Tu aplicación → Credenciales
- **Seguridad:** ⚠️ Nunca compartas este valor públicamente

### `MERCADO_LIBRE_REDIRECT_URI`
- **Descripción:** URI de redirección configurada en la aplicación de MercadoLibre
- **Ejemplo:** `http://localhost:3000/api/mercado-libre/auth/callback`
- **Producción:** `https://tudominio.com/api/mercado-libre/auth/callback`
- **Importante:** Debe coincidir **exactamente** con la URI registrada en MercadoLibre

### `MERCADO_LIBRE_SELLER_ID`
- **Descripción:** ID del vendedor en MercadoLibre
- **Ejemplo:** `123456789`
- **Dónde obtenerlo:** Se obtiene automáticamente después de la primera autenticación OAuth, o puedes encontrarlo en tu perfil de vendedor

## Variables Opcionales

Estas variables tienen valores por defecto pero pueden ser configuradas:

### `MERCADO_LIBRE_AUTH_URL`
- **Descripción:** URL base de autenticación (varía por país)
- **Valor por defecto:** `https://auth.mercadolibre.com.ar`
- **Opciones por país:**
  - Argentina: `https://auth.mercadolibre.com.ar`
  - México: `https://auth.mercadolibre.com.mx`
  - Uruguay: `https://auth.mercadolibre.com.uy`
  - Brasil: `https://auth.mercadolibre.com.br`
  - Chile: `https://auth.mercadolibre.com.cl`
  - Colombia: `https://auth.mercadolibre.com.co`
  - Perú: `https://auth.mercadolibre.com.pe`

### `MERCADO_LIBRE_API_URL`
- **Descripción:** URL base de la API de MercadoLibre
- **Valor por defecto:** `https://api.mercadolibre.com`
- **Nota:** Generalmente no necesita cambiarse

### `MERCADO_LIBRE_SCOPES`
- **Descripción:** Scopes OAuth separados por espacios
- **Valor por defecto:** `offline_access read write`
- **Scopes comunes:**
  - `offline_access`: Permite obtener refresh tokens
  - `read`: Permite leer datos
  - `write`: Permite escribir/modificar datos

### `MERCADO_LIBRE_PKCE_ENABLED`
- **Descripción:** Habilita PKCE (Proof Key for Code Exchange) para mayor seguridad
- **Valor por defecto:** `true`
- **Valores válidos:** `true` o `false`
- **Recomendación:** Mantener en `true` para mayor seguridad

### `MERCADO_LIBRE_WEBHOOK_SECRET`
- **Descripción:** Secret para validar la firma de webhooks de MercadoLibre
- **Valor por defecto:** (vacío)
- **Generación:** Puede ser cualquier string aleatorio seguro
- **Ejemplo:** Generar con: `openssl rand -hex 32`

### `MERCADO_LIBRE_ACCESS_TOKEN`
- **Descripción:** Token de acceso actual (se obtiene automáticamente via OAuth)
- **Nota:** Se genera automáticamente durante el flujo OAuth, no es necesario configurarlo manualmente

### `MERCADO_LIBRE_REFRESH_TOKEN`
- **Descripción:** Token de refresco para renovar el access token (se obtiene automáticamente via OAuth)
- **Nota:** Se genera automáticamente durante el flujo OAuth, no es necesario configurarlo manualmente

### `MERCADO_LIBRE_PAGE_SIZE`
- **Descripción:** Tamaño de página para paginación de resultados (usado en scripts Python)
- **Valor por defecto:** `50`
- **Rango recomendado:** 10-100

## Variables Legacy (Compatibilidad)

Las siguientes variables con prefijo `MELI_*` siguen siendo soportadas para compatibilidad hacia atrás, pero se recomienda migrar a `MERCADO_LIBRE_*`:

- `MELI_ACCESS_TOKEN` → Usar `MERCADO_LIBRE_ACCESS_TOKEN`
- `MELI_REFRESH_TOKEN` → Usar `MERCADO_LIBRE_REFRESH_TOKEN`
- `MELI_SELLER_ID` → Usar `MERCADO_LIBRE_SELLER_ID`
- `MELI_PAGE_SIZE` → Usar `MERCADO_LIBRE_PAGE_SIZE`

## Ejemplo de Archivo `.env`

```env
# MercadoLibre - Variables Requeridas
MERCADO_LIBRE_APP_ID=1234567890123456
MERCADO_LIBRE_CLIENT_SECRET=tu_client_secret_aqui
MERCADO_LIBRE_REDIRECT_URI=http://localhost:3000/api/mercado-libre/auth/callback
MERCADO_LIBRE_SELLER_ID=123456789

# MercadoLibre - Variables Opcionales
MERCADO_LIBRE_AUTH_URL=https://auth.mercadolibre.com.uy
MERCADO_LIBRE_API_URL=https://api.mercadolibre.com
MERCADO_LIBRE_SCOPES=offline_access read write
MERCADO_LIBRE_PKCE_ENABLED=true
MERCADO_LIBRE_WEBHOOK_SECRET=tu_webhook_secret_aqui
MERCADO_LIBRE_PAGE_SIZE=50
```

## Verificación de Configuración

### Desde la API

Puedes verificar el estado de la configuración llamando al endpoint:

```bash
GET /api/mercado-libre/config/status
```

Respuesta de ejemplo:

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

### Desde el Código

```typescript
import { validateMercadoLibreConfig } from '@/lib/mercado-libre/config-validator'

const validation = validateMercadoLibreConfig()
if (!validation.isValid) {
  console.error('Configuración inválida:', validation.errors)
}
```

## Solución de Problemas

### Error: "Missing environment variable MERCADO_LIBRE_APP_ID"

**Solución:** Asegúrate de que todas las variables requeridas estén configuradas en tu archivo `.env` o `.env.local`.

### Error: "Token de Mercado Libre inválido o expirado"

**Solución:** 
1. Verifica que `MERCADO_LIBRE_ACCESS_TOKEN` sea válido
2. El token se refresca automáticamente, pero si persiste el error, completa el flujo OAuth nuevamente
3. Verifica que `MERCADO_LIBRE_REFRESH_TOKEN` esté configurado

### Error: "Estado de autorización inválido o expirado"

**Solución:** El estado OAuth expiró (generalmente después de 10 minutos). Inicia el flujo de autorización nuevamente.

### Warning: "Se detectaron variables con prefijo MELI_*"

**Solución:** Migra las variables a `MERCADO_LIBRE_*` para consistencia. El sistema seguirá funcionando con `MELI_*` por compatibilidad.

## Seguridad

- ⚠️ **Nunca** commits archivos `.env` al repositorio
- ⚠️ **Nunca** compartas `MERCADO_LIBRE_CLIENT_SECRET` públicamente
- ✅ Usa `.env.example` para documentar variables sin valores
- ✅ Rota los secrets periódicamente
- ✅ Usa diferentes credenciales para desarrollo y producción

## Referencias

- [Documentación de MercadoLibre Developers](https://developers.mercadolibre.com/)
- [Guía de OAuth de MercadoLibre](https://developers.mercadolibre.com/es_ar/autenticacion-y-autorizacion)
- [Revisión de Conexión MercadoLibre](./REVISION_CONEXION_MERCADOLIBRE.md)

