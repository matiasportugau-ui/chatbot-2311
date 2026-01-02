# 📋 Cómo Cargar Credenciales desde Variables de Entorno

## ✅ Implementación Completada

Se ha agregado soporte completo para cargar credenciales desde archivos `.env` usando `python-dotenv`.

---

## 🔧 Configuración

### 1. Instalar python-dotenv (si no está instalado)

```bash
pip install python-dotenv
```

O si usas requirements.txt:
```bash
pip install -r requirements.txt
```

### 2. Crear archivo de variables de entorno

Crea un archivo `.env.local` o `.env` en la raíz del proyecto:

```bash
# Google Sheets API
GOOGLE_SHEET_ID=1bs467N7FbLSHI7LpNor3wqrPZC9snqPphft8cEPHHl0
GOOGLE_SERVICE_ACCOUNT_EMAIL=bmc-sheets-service@tu-proyecto.iam.gserviceaccount.com
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nTU_CLAVE_PRIVADA_AQUI\n-----END PRIVATE KEY-----\n"

# OpenAI API (opcional)
OPENAI_API_KEY=sk-proj-tu-api-key-aqui

# MongoDB (opcional)
MONGODB_URI=mongodb+srv://usuario:password@cluster.mongodb.net/bmc_quotes
```

**⚠️ IMPORTANTE**: 
- El archivo `.env.local` tiene prioridad sobre `.env`
- Estos archivos NO deben subirse a Git (están en .gitignore)
- La clave privada debe incluir los saltos de línea como `\n`

---

## 🚀 Uso Automático

Las credenciales se cargan automáticamente cuando importas los módulos:

### En `integracion_google_sheets.py`:
```python
from integracion_google_sheets import IntegracionGoogleSheets

# Las credenciales se cargan automáticamente desde .env
sheets = IntegracionGoogleSheets()
```

### En `chat_interactivo.py`:
```python
from chat_interactivo import AgenteInteractivo

# Las credenciales se cargan automáticamente
agente = AgenteInteractivo()
```

---

## 🛠️ Script de Configuración

Se ha creado un script de ayuda para configurar las variables:

```bash
# Crear o actualizar .env.local
python configurar_env.py

# Verificar variables configuradas
python configurar_env.py verificar
```

---

## 📝 Orden de Prioridad

El sistema busca credenciales en este orden:

1. **Variables de entorno del sistema** (más alta prioridad)
   - `GOOGLE_SERVICE_ACCOUNT_EMAIL`
   - `GOOGLE_PRIVATE_KEY`
   - `GOOGLE_SHEET_ID`

2. **Archivo `.env.local`** (desarrollo local)
   - Se carga primero si existe

3. **Archivo `.env`** (desarrollo)
   - Se carga si no existe `.env.local`

4. **Archivo JSON** (`credenciales.json`, `google-credentials.json`, `service-account.json`)
   - Para desarrollo local con archivo de credenciales

5. **Modo simulado** (si no hay credenciales)
   - El sistema funciona pero no guarda en Google Sheets

---

## 🔍 Verificación

Para verificar que las credenciales se están cargando correctamente:

```python
import os
from dotenv import load_dotenv

# Cargar variables
load_dotenv('.env.local')  # o .env

# Verificar
print("GOOGLE_SHEET_ID:", os.getenv('GOOGLE_SHEET_ID'))
print("GOOGLE_SERVICE_ACCOUNT_EMAIL:", os.getenv('GOOGLE_SERVICE_ACCOUNT_EMAIL'))
print("GOOGLE_PRIVATE_KEY:", "✅ Configurada" if os.getenv('GOOGLE_PRIVATE_KEY') else "❌ No configurada")
```

O usa el script de verificación:
```bash
python configurar_env.py verificar
```

---

## ⚠️ Troubleshooting

### Error: "python-dotenv no instalado"
```bash
pip install python-dotenv
```

### Las variables no se cargan
1. Verifica que el archivo `.env.local` o `.env` esté en la raíz del proyecto
2. Verifica que no tenga errores de sintaxis
3. Asegúrate de que las comillas estén correctas en `GOOGLE_PRIVATE_KEY`

### La clave privada no funciona
- Asegúrate de incluir los saltos de línea como `\n`
- La clave debe estar entre comillas dobles
- Debe incluir `-----BEGIN PRIVATE KEY-----` y `-----END PRIVATE KEY-----`

---

## 📚 Ejemplo Completo

### Archivo `.env.local`:
```bash
GOOGLE_SHEET_ID=1bs467N7FbLSHI7LpNor3wqrPZC9snqPphft8cEPHHl0
GOOGLE_SERVICE_ACCOUNT_EMAIL=bmc-sheets-service@mi-proyecto.iam.gserviceaccount.com
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n-----END PRIVATE KEY-----\n"
```

### Uso en código:
```python
# Las credenciales se cargan automáticamente
from integracion_google_sheets import IntegracionGoogleSheets

sheets = IntegracionGoogleSheets()
sheets.conectar_google_sheets()  # ✅ Conectado usando credenciales de .env
```

---

## ✅ Estado Actual

- ✅ Carga automática desde `.env.local` y `.env`
- ✅ Soporte para variables de entorno del sistema
- ✅ Script de configuración interactivo
- ✅ Script de verificación
- ✅ Mensajes informativos de carga
- ✅ Manejo de errores robusto

¡Todo listo para usar! 🎉

