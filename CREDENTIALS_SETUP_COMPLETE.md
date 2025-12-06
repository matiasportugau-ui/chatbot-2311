# ✅ Sistema Unificado de Credenciales - Configuración Completa

## 🎯 Problema Resuelto

**ANTES:** Tenías que configurar credenciales en múltiples lugares:
- `.env`
- `.env.local`
- Variables de entorno del sistema
- Archivos de configuración individuales
- Scripts de setup separados

**AHORA:** Configuras TODO UNA SOLA VEZ y se carga automáticamente en todos los scripts.

## 🚀 Solución Implementada

### Sistema Unificado de Credenciales

1. **`unified_credentials_manager.py`** - Sistema centralizado
   - Almacena TODAS las credenciales en un solo lugar
   - Carga automáticamente desde múltiples fuentes
   - Integración automática con todos los scripts

2. **`setup_credentials_once.py`** - Configuración única
   - Wizard interactivo para configurar todas las credenciales
   - Una sola vez, funciona para siempre

3. **`init_credentials.py`** - Carga automática
   - Se ejecuta automáticamente al importar cualquier módulo
   - No necesitas hacer nada manualmente

## 📋 Cómo Usar (UNA SOLA VEZ)

### Opción 1: Wizard Interactivo (Recomendado)

```bash
python3 setup_credentials_once.py
```

O simplemente:

```bash
python3 unified_credentials_manager.py wizard
```

### Opción 2: Configuración Manual

```bash
# Ver estado actual
python3 unified_credentials_manager.py status

# Configurar una credencial específica
python3 unified_credentials_manager.py set --key GITHUB_TOKEN --value tu_token

# Verificar credenciales
python3 unified_credentials_manager.py check --required GITHUB_TOKEN OPENAI_API_KEY
```

## 🔄 Uso Automático en Scripts

Después de configurar UNA VEZ, todos los scripts cargan automáticamente:

```python
# En cualquier script, simplemente:
from unified_credentials_manager import get_credential

# Obtener cualquier credencial:
token = get_credential('GITHUB_TOKEN')
api_key = get_credential('OPENAI_API_KEY')
```

**No necesitas configurar nada más - se carga automáticamente.**

## 📦 Credenciales Soportadas

El sistema maneja automáticamente:

### GitHub
- `GITHUB_TOKEN` - Token de GitHub
- `GITHUB_OWNER` - Propietario/organización

### IA Providers
- `OPENAI_API_KEY` - OpenAI
- `GROQ_API_KEY` - Groq
- `GEMINI_API_KEY` - Google Gemini
- `XAI_API_KEY` / `GROK_API_KEY` - xAI/Grok

### Bases de Datos
- `MONGODB_URI` - MongoDB connection string
- `MONGODB_DATABASE` - Nombre de base de datos

### Integraciones
- `WHATSAPP_API_KEY` - WhatsApp Business
- `GOOGLE_SHEETS_CREDENTIALS` - Google Sheets
- `N8N_API_KEY` - N8N

### Otros
- `BMC_MASTER_PASSWORD` - Contraseña maestra para cifrado

## 🔐 Fuentes de Credenciales (Orden de Prioridad)

1. **Variables de entorno del sistema** (más alta prioridad)
2. **Archivo cifrado local** (`~/.bmc-secrets/secrets.encrypted`)
3. **`.env.local`** (desarrollo local)
4. **`.env`** (fallback)

## ✅ Integración Automática

Los siguientes scripts ya están integrados:

- ✅ `repo_research_agent.py` - Carga automática de GITHUB_TOKEN
- ✅ `local_repo_research_agent.py` - Carga automática
- ✅ `github_analyzer.py` - Usa credenciales automáticamente
- ✅ `model_integrator.py` - Carga API keys automáticamente
- ✅ `ejecutor_completo.py` - Carga automática al iniciar

## 🎯 Flujo de Trabajo

### Primera Vez (Configuración)

```bash
# 1. Ejecutar wizard
python3 setup_credentials_once.py

# 2. Ingresar todas las credenciales
# 3. ¡Listo! Ya no necesitas configurar nada más
```

### Uso Diario

```bash
# Simplemente ejecuta tus scripts - las credenciales se cargan automáticamente
python3 local_repo_research_agent.py
python3 ejecutor_completo.py
# etc.
```

## 🔍 Verificar Estado

```bash
# Ver todas las credenciales
python3 unified_credentials_manager.py status

# Verificar credenciales específicas
python3 unified_credentials_manager.py check --required GITHUB_TOKEN OPENAI_API_KEY
```

## 📝 Agregar Nuevas Credenciales

Si necesitas agregar una nueva credencial:

1. Agrega a `ALL_CREDENTIALS` en `unified_credentials_manager.py`
2. Configúrala con el wizard o manualmente
3. Todos los scripts la cargarán automáticamente

## 🛡️ Seguridad

- ✅ Credenciales nunca en Git (`.gitignore` configurado)
- ✅ Cifrado local opcional (archivo cifrado)
- ✅ Permisos restrictivos (600) en archivos de credenciales
- ✅ Variables de entorno como fallback seguro

## 💡 Tips

1. **Configura UNA VEZ** - Usa el wizard y olvídate
2. **Verifica periódicamente** - `python3 unified_credentials_manager.py status`
3. **Backup del archivo cifrado** - Si usas cifrado, haz backup de `~/.bmc-secrets/`
4. **No compartas** - Nunca compartas tu archivo de credenciales

## ❓ Preguntas Frecuentes

**P: ¿Tengo que ejecutar algo cada vez?**
R: NO. Se carga automáticamente al importar cualquier módulo.

**P: ¿Qué pasa si cambio una credencial?**
R: Usa `python3 unified_credentials_manager.py set --key KEY --value VALUE`

**P: ¿Funciona en producción?**
R: Sí, pero para producción se recomienda usar gestores de secretos profesionales (AWS Secrets Manager, etc.)

**P: ¿Puedo usar solo .env.local?**
R: Sí, el sistema lo detecta y carga automáticamente.

---

## ✅ Resumen

**ANTES:** Configuración repetida en múltiples lugares ❌

**AHORA:** Configuración única, carga automática, funciona en todos los scripts ✅

**Ejecuta UNA VEZ:**
```bash
python3 setup_credentials_once.py
```

**Y nunca más tendrás que configurar credenciales manualmente.** 🎉

