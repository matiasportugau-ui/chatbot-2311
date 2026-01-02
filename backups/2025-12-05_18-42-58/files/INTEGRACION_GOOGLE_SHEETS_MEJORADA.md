# 📊 Integración Google Sheets - Mejoras Implementadas

## ✅ Cambios Realizados

### 1. **Configuración de Credenciales Mejorada**

La integración ahora soporta múltiples formas de configurar credenciales:

#### Opción A: Variables de Entorno (Recomendado para Producción)
```bash
GOOGLE_SHEET_ID=1bs467N7FbLSHI7LpNor3wqrPZC9snqPphft8cEPHHl0
GOOGLE_SERVICE_ACCOUNT_EMAIL=bmc-sheets-service@proyecto.iam.gserviceaccount.com
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
```

#### Opción B: Archivo JSON (Desarrollo Local)
Coloca un archivo `credenciales.json` o `google-credentials.json` en la raíz del proyecto con el formato:
```json
{
  "type": "service_account",
  "project_id": "tu-proyecto",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "bmc-sheets-service@proyecto.iam.gserviceaccount.com",
  ...
}
```

#### Opción C: Modo Simulado
Si no hay credenciales configuradas, el sistema funciona en modo simulado (solo para desarrollo/testing).

---

### 2. **Integración con Chat Interactivo**

El chat interactivo ahora guarda automáticamente las cotizaciones en Google Sheets:

- ✅ **Guardado automático**: Cada cotización generada se guarda en la pestaña "Admin."
- ✅ **Código Arg generado**: Se genera automáticamente un código único para cada cotización
- ✅ **Formato estándar**: Los datos se guardan en el formato esperado por el sistema
- ✅ **Manejo de errores**: Si no hay conexión, el chat sigue funcionando normalmente

#### Formato del Código Arg:
```
{origen}{día}{hora}{últimos4dígitos}
Ejemplo: CH24151234 (Chat, día 24, hora 15, teléfono ...1234)
```

---

### 3. **Nuevos Métodos Agregados**

#### `generar_codigo_arg(telefono, origen)`
Genera un código único para identificar cotizaciones.

#### `guardar_cotizacion_en_sheets(cotizacion_data)`
Guarda una cotización completa en Google Sheets. Acepta:
- `cliente`: Nombre del cliente
- `telefono`: Teléfono de contacto
- `direccion`: Dirección o zona
- `consulta`: Descripción de la consulta
- `origen`: Origen de la cotización (CH=Chat, WA=WhatsApp, etc.)
- `estado`: Estado inicial (default: "Pendiente")

#### `construir_consulta_cotizacion(datos_cliente, datos_especificaciones)`
Construye una descripción estructurada de la consulta a partir de los datos de la cotización.

---

## 🚀 Cómo Usar

### Configuración Inicial

1. **Configurar credenciales** (elige una opción):
   - Variables de entorno (producción)
   - Archivo JSON (desarrollo)
   - Modo simulado (testing)

2. **Compartir Google Sheet** con el Service Account:
   - Abre el Sheet: https://docs.google.com/spreadsheets/d/1bs467N7FbLSHI7LpNor3wqrPZC9snqPphft8cEPHHl0
   - Click en "Compartir"
   - Agrega el email del Service Account (bmc-sheets-service@...)
   - Da permisos de "Editor"

### Uso en Chat Interactivo

```python
from chat_interactivo import AgenteInteractivo

# El agente ahora guarda automáticamente en Google Sheets
agente = AgenteInteractivo()

# Cuando el usuario completa una cotización, se guarda automáticamente
respuesta = agente.procesar_mensaje("cotizar")
```

### Uso Directo de la Integración

```python
from integracion_google_sheets import IntegracionGoogleSheets

# Crear instancia (puede funcionar sin IA)
sheets = IntegracionGoogleSheets()

# Conectar
sheets.conectar_google_sheets()

# Guardar cotización
datos = {
    'cliente': 'Juan Pérez',
    'telefono': '099123456',
    'direccion': 'Montevideo',
    'consulta': 'Isodec 100mm / 50 m² / blanco / completo',
    'origen': 'CH',
    'estado': 'Pendiente'
}

resultado = sheets.guardar_cotizacion_en_sheets(datos)
print(resultado['mensaje'])  # ✅ Cotización guardada con código CH24151234
```

---

## 📋 Estructura de Datos en Google Sheets

Las cotizaciones se guardan en la pestaña "Admin." con esta estructura:

| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| A: Arg | Código único | CH24151234 |
| B: Estado | Estado de la cotización | Pendiente |
| C: Fecha | Fecha de creación | 24-10 |
| D: Cliente | Nombre del cliente | Juan Pérez |
| E: Orig. | Origen | CH (Chat) |
| F: Telefono-Contacto | Teléfono | 099123456 |
| G: Direccion / Zona | Ubicación | Montevideo |
| H: Consulta | Descripción | Isodec 100mm / 50 m² / blanco |

---

## 🔍 Verificación

Para verificar que la integración funciona:

1. **Ejecutar chat interactivo**:
   ```bash
   python chat_interactivo.py
   ```

2. **Completar una cotización**:
   - Iniciar con "cotizar"
   - Completar todos los pasos
   - Al finalizar, deberías ver: "📊 Guardado en Google Sheets: Código CH..."

3. **Verificar en Google Sheets**:
   - Abre el Sheet
   - Ve a la pestaña "Admin."
   - Deberías ver la nueva cotización al final

---

## ⚠️ Troubleshooting

### Error: "No se pudo conectar a Google Sheets"
- Verifica que las credenciales estén configuradas correctamente
- Asegúrate de que el Sheet esté compartido con el Service Account
- Revisa que las variables de entorno estén cargadas

### Error: "Credenciales no configuradas"
- El sistema funcionará en modo simulado
- Las cotizaciones no se guardarán realmente
- Configura las credenciales para producción

### Error: "Permission denied"
- Verifica que el Service Account tenga permisos de "Editor" en el Sheet
- Asegúrate de haber compartido el Sheet con el email correcto

---

## 🎯 Próximos Pasos Recomendados

1. ✅ **Configurar credenciales reales** para producción
2. ✅ **Probar guardado automático** desde el chat
3. ⏳ **Implementar sincronización bidireccional** (leer desde Sheets)
4. ⏳ **Agregar notificaciones** cuando cambie el estado
5. ⏳ **Implementar historial de cambios**

---

## 📝 Notas

- El sistema funciona en modo simulado si no hay credenciales (útil para desarrollo)
- Las cotizaciones se guardan automáticamente sin interrumpir el flujo del chat
- El código Arg se genera automáticamente para evitar duplicados
- La integración es opcional: el chat funciona perfectamente sin Google Sheets

