# 📋 Scripts de Instalación, Configuración y Ejecución

## 🎯 Scripts Principales (Recomendados)

### 1. **`ejecutor_completo.py`** ⭐ **RECOMENDADO - TODO EN UNO**

**Descripción:** Ejecutor unificado que hace TODO automáticamente:
- ✅ Review del sistema (verificación pre-instalación)
- ✅ Instalación automática (dependencias faltantes)
- ✅ Configuración automática (MongoDB, servicios)
- ✅ Ejecución del sistema completo
- ✅ Auto-reparación de problemas detectados
- ✅ Carga automática de secretos desde archivo local

**Uso:**
```bash
python ejecutor_completo.py
```

**Características:**
- Verifica Python, Node.js, dependencias
- Instala automáticamente lo que falta
- Configura MongoDB con Docker
- Carga secretos desde `~/.bmc-secrets/` o `.env.local`
- Auto-repara problemas comunes
- Ejecuta el sistema en modo unified/chat/api

**Ubicación:** `/Users/matias/chatbot2511/chatbot-2311/ejecutor_completo.py`

---

### 2. **`unified_launcher.py`** ⭐ **ALTERNATIVA - LAUNCHER UNIFICADO**

**Descripción:** Launcher unificado para todos los servicios del sistema

**Uso:**
```bash
python unified_launcher.py
```

**Características:**
- Inicia todos los servicios necesarios
- Gestiona procesos en background
- Maneja señales de sistema
- Logging estructurado

**Ubicación:** `/Users/matias/chatbot2511/chatbot-2311/unified_launcher.py`

---

## 🔧 Scripts de Instalación

### 3. **`instalar_dependencias_automatico.py`**

**Descripción:** Instala automáticamente todas las dependencias de Python desde `requirements.txt`

**Uso:**
```bash
python instalar_dependencias_automatico.py
```

**Características:**
- Actualiza pip automáticamente
- Instala todas las dependencias de `requirements.txt`
- Manejo de errores

**Ubicación:** `/Users/matias/chatbot2511/chatbot-2311/instalar_dependencias_automatico.py`

---

### 4. **`instalar.py`**

**Descripción:** Instalador completo del sistema con verificaciones

**Uso:**
```bash
python instalar.py
```

**Características:**
- Verifica versión de Python
- Verifica dependencias básicas y opcionales
- Instala dependencias faltantes
- Configuración inicial

**Ubicación:** `/Users/matias/chatbot2511/chatbot-2311/instalar.py`

---

### 5. **`verificar_instalacion.py`**

**Descripción:** Verifica que la instalación esté completa

**Uso:**
```bash
python verificar_instalacion.py
```

**Características:**
- Verifica Python y Node.js
- Verifica módulos instalados
- Verifica archivos necesarios
- Reporta estado de instalación

**Ubicación:** `/Users/matias/chatbot2511/chatbot-2311/verificar_instalacion.py`

---

## ⚙️ Scripts de Configuración

### 6. **`configurar_auto.py`**

**Descripción:** Configuración automática con valores por defecto para desarrollo local

**Uso:**
```bash
python configurar_auto.py
```

**Características:**
- Crea `.env.local` automáticamente
- Usa valores por defecto seguros
- Genera tokens aleatorios
- Configuración para desarrollo local

**Ubicación:** `/Users/matias/chatbot2511/chatbot-2311/configurar_auto.py`

---

### 7. **`configurar_completo.py`**

**Descripción:** Configuración interactiva completa del sistema

**Uso:**
```bash
python configurar_completo.py
```

**Características:**
- Guía paso a paso
- Configuración de todas las APIs
- Validación de credenciales
- Guarda en `.env.local`

**Ubicación:** `/Users/matias/chatbot2511/chatbot-2311/configurar_completo.py`

---

### 8. **`configurar_env.py`**

**Descripción:** Configuración interactiva de variables de entorno

**Uso:**
```bash
python configurar_env.py
```

**Características:**
- Crea/actualiza `.env.local`
- Interfaz interactiva
- Validación de valores

**Ubicación:** `/Users/matias/chatbot2511/chatbot-2311/configurar_env.py`

---

### 9. **`configurar_entorno.py`**

**Descripción:** Configuración del entorno de desarrollo

**Uso:**
```bash
python configurar_entorno.py
```

**Ubicación:** `/Users/matias/chatbot2511/chatbot-2311/configurar_entorno.py`

---

### 10. **`setup_secrets.py`** 🔐

**Descripción:** Setup interactivo de secretos locales cifrados

**Uso:**
```bash
python setup_secrets.py
```

**Características:**
- Crea archivo de secretos cifrado en `~/.bmc-secrets/`
- Interfaz interactiva para ingresar secretos
- Cifrado con contraseña maestra
- Backup automático
- Opción de exportar a `.env.local`

**Ubicación:** `/Users/matias/chatbot2511/chatbot-2311/setup_secrets.py`

---

### 11. **`verificar_configuracion.py`**

**Descripción:** Verifica que la configuración esté completa

**Uso:**
```bash
python verificar_configuracion.py
```

**Características:**
- Verifica variables de entorno requeridas
- Reporta configuraciones faltantes
- Valida formato de credenciales

**Ubicación:** `/Users/matias/chatbot2511/chatbot-2311/verificar_configuracion.py`

---

### 12. **`setup_gemini.py`**

**Descripción:** Configuración específica para Google Gemini API

**Uso:**
```bash
python setup_gemini.py
```

**Ubicación:** `/Users/matias/chatbot2511/chatbot-2311/setup_gemini.py`

---

### 13. **`setup_grok_env.py`**

**Descripción:** Configuración específica para Grok API

**Uso:**
```bash
python setup_grok_env.py
```

**Ubicación:** `/Users/matias/chatbot2511/chatbot-2311/setup_grok_env.py`

---

### 14. **`setup_n8n_credentials.py`**

**Descripción:** Configuración de credenciales para n8n

**Uso:**
```bash
python setup_n8n_credentials.py
```

**Ubicación:** `/Users/matias/chatbot2511/chatbot-2311/setup_n8n_credentials.py`

---

## 🚀 Scripts de Ejecución

### 15. **`ejecutar_sistema.py`**

**Descripción:** Ejecuta el sistema con menú de opciones

**Uso:**
```bash
python ejecutar_sistema.py
```

**Características:**
- Menú interactivo
- Opciones: demo, sistema interactivo, mapeador
- Verificación de dependencias

**Ubicación:** `/Users/matias/chatbot2511/chatbot-2311/ejecutar_sistema.py`

---

### 16. **`verify_setup.py`**

**Descripción:** Verifica que el setup esté completo antes de ejecutar

**Uso:**
```bash
python verify_setup.py
```

**Ubicación:** `/Users/matias/chatbot2511/chatbot-2311/verify_setup.py`

---

## 📦 Scripts Adicionales

### 17. **`setup_mongodb_docker.sh`**

**Descripción:** Script para configurar MongoDB con Docker

**Uso:**
```bash
bash setup_mongodb_docker.sh
```

**Características:**
- Crea contenedor Docker de MongoDB
- Configura puerto 27017
- Gestiona contenedores existentes
- Inicia automáticamente

**Ubicación:** `/Users/matias/chatbot2511/chatbot-2311/setup_mongodb_docker.sh`

---

### 18. **`load_secrets_automatically.py`**

**Descripción:** Módulo para cargar secretos automáticamente (usado por ejecutor_completo.py)

**Uso:**
```python
from load_secrets_automatically import load_secrets_automatically
load_secrets_automatically()
```

**Características:**
- Carga desde `~/.bmc-secrets/secrets.encrypted`
- Fallback a `.env.local`
- No interactivo (no pide password)
- Usa `BMC_MASTER_PASSWORD` si está disponible

**Ubicación:** `/Users/matias/chatbot2511/chatbot-2311/load_secrets_automatically.py`

---

### 19. **`secrets_manager.py`** 🔐

**Descripción:** Gestor de secretos local cifrado

**Uso:**
```bash
# Crear archivo de secretos
python secrets_manager.py create

# Agregar secreto
python secrets_manager.py add --key OPENAI_API_KEY --value sk-...

# Obtener secreto
python secrets_manager.py get --key OPENAI_API_KEY

# Listar secretos
python secrets_manager.py list

# Exportar a .env.local
python secrets_manager.py export

# Crear backup
python secrets_manager.py backup
```

**Características:**
- Cifrado con Fernet (AES 128)
- Almacenamiento local en `~/.bmc-secrets/`
- Backup automático
- Exportación a `.env.local`

**Ubicación:** `/Users/matias/chatbot2511/chatbot-2311/secrets_manager.py`

---

## 🎯 Flujo Recomendado

### Opción 1: Todo Automático (Recomendado)

```bash
# 1. Ejecutar el ejecutor completo (hace TODO)
python ejecutor_completo.py
```

Esto hace:
- ✅ Review del sistema
- ✅ Instalación automática
- ✅ Configuración automática
- ✅ Ejecución del sistema

---

### Opción 2: Paso a Paso

```bash
# 1. Instalar dependencias
python instalar_dependencias_automatico.py

# 2. Configurar secretos (opcional, si quieres usar cifrado)
python setup_secrets.py

# O configurar .env.local directamente
python configurar_auto.py

# 3. Verificar instalación
python verificar_instalacion.py

# 4. Verificar configuración
python verificar_configuracion.py

# 5. Ejecutar sistema
python ejecutor_completo.py
# O
python unified_launcher.py
```

---

## 📊 Comparación de Scripts

| Script | Instalación | Configuración | Ejecución | Auto-reparación | Recomendado |
|-------|-------------|---------------|-----------|-----------------|-------------|
| `ejecutor_completo.py` | ✅ | ✅ | ✅ | ✅ | ⭐⭐⭐⭐⭐ |
| `unified_launcher.py` | ⚠️ | ⚠️ | ✅ | ❌ | ⭐⭐⭐⭐ |
| `instalar_dependencias_automatico.py` | ✅ | ❌ | ❌ | ❌ | ⭐⭐⭐ |
| `configurar_auto.py` | ❌ | ✅ | ❌ | ❌ | ⭐⭐⭐ |
| `setup_secrets.py` | ❌ | ✅ | ❌ | ❌ | ⭐⭐⭐⭐ |
| `ejecutar_sistema.py` | ❌ | ❌ | ✅ | ❌ | ⭐⭐ |

---

## 🔍 Scripts por Categoría

### Instalación
- `ejecutor_completo.py` (todo en uno)
- `instalar_dependencias_automatico.py`
- `instalar.py`
- `verificar_instalacion.py`

### Configuración
- `ejecutor_completo.py` (incluye configuración)
- `configurar_auto.py`
- `configurar_completo.py`
- `configurar_env.py`
- `setup_secrets.py` (cifrado)
- `verificar_configuracion.py`
- `setup_gemini.py`
- `setup_grok_env.py`
- `setup_n8n_credentials.py`

### Ejecución
- `ejecutor_completo.py` (recomendado)
- `unified_launcher.py`
- `ejecutar_sistema.py`

### Gestión de Secretos
- `setup_secrets.py` (setup interactivo)
- `secrets_manager.py` (gestión CLI)
- `load_secrets_automatically.py` (carga automática)

---

## ✅ Recomendación Final

**Para la mayoría de casos: Usar `ejecutor_completo.py`**

```bash
python ejecutor_completo.py
```

**Ventajas:**
- ✅ Hace TODO automáticamente
- ✅ Auto-repara problemas
- ✅ Carga secretos automáticamente
- ✅ Verifica e instala dependencias
- ✅ Configura servicios (MongoDB, etc.)
- ✅ Ejecuta el sistema

**Es el script más completo y recomendado** ⭐

---

## 📚 Documentación Relacionada

- `INSTALAR_Y_EJECUTAR.md` - Guía rápida
- `SECRETS_SETUP_GUIDE.md` - Guía de secretos
- `BEST_PRACTICES_EJECUTOR.md` - Mejores prácticas
- `SECRETS_MANAGEMENT_BEST_PRACTICES.md` - Gestión de secretos

