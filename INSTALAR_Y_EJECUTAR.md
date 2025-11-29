# 🚀 Instalación y Ejecución del Chatbot BMC

## ⭐ Recomendado: Unified Launcher

El **Unified Launcher** es la forma más fácil y completa de ejecutar el sistema. Maneja automáticamente la instalación, configuración y ejecución.

### Inicio Rápido

**Windows:**
```batch
launch.bat
```

**Linux/Mac:**
```bash
./launch.sh
```

**Directo:**
```bash
python unified_launcher.py
```

### ¿Qué hace el Unified Launcher?

- ✅ Verifica requisitos (Python 3.11+, Node.js)
- ✅ Instala dependencias automáticamente
- ✅ Configura entorno (.env)
- ✅ Menú interactivo con todos los modos
- ✅ Gestión de servicios (API, MongoDB, Next.js)

### Ejecución Directa de Modos

```bash
# Chat interactivo
python unified_launcher.py --mode chat

# API Server
python unified_launcher.py --mode api

# Simulador
python unified_launcher.py --mode simulator

# Full Stack (API + Dashboard)
python unified_launcher.py --mode fullstack
```

Para documentación completa, ver **[UNIFIED_LAUNCHER.md](./UNIFIED_LAUNCHER.md)**

---

## Alternativas

### Opción 1: Script Batch Legacy (Deprecado)

⚠️ **Nota:** Este script está deprecado. Usa `launch.bat` en su lugar.

```batch
run_chatbot.bat
```

Este script:
- ✅ Detecta Python automáticamente
- ✅ Configura el encoding UTF-8
- ✅ Ejecuta el chatbot con todas las configuraciones correctas

### Opción 2: Ejecución Directa

```bash
python chat_interactivo.py
```

O si usas el launcher de Python:
```bash
py chat_interactivo.py
```

## Verificación de Instalación

Antes de ejecutar, puedes verificar que todo esté correcto:

```bash
python verificar_instalacion.py
```

Este script verifica:
- ✅ Módulos básicos requeridos
- ✅ Módulos opcionales (IA, base de conocimiento)
- ✅ Archivos de conocimiento disponibles

## Dependencias

### Módulos Básicos (Incluidos en Python)
- `json`, `datetime`, `decimal`, `re`, `sys`, `os`
- ✅ No requieren instalación

### Módulos del Proyecto
- `sistema_cotizaciones.py` - Sistema de cotizaciones
- `utils_cotizaciones.py` - Utilidades
- ✅ Ya están en el proyecto

### Módulos Opcionales (para IA completa)
- `base_conocimiento_dinamica.py` - Base de conocimiento
- `ia_conversacional_integrada.py` - IA conversacional
- ✅ Ya están en el proyecto

### Dependencias Externas (Opcionales)

Solo necesitas instalar dependencias externas si quieres usar:
- **OpenAI**: Para IA avanzada
- **MongoDB**: Para persistencia de datos
- **FastAPI**: Para API REST

Para instalar dependencias opcionales:
```bash
pip install -r requirements.txt
```

## Funcionamiento

### Modo Simple (Sin IA)
El chatbot funciona con módulos básicos de Python. No requiere dependencias externas.

### Modo Completo (Con IA y Conocimiento)
El chatbot carga automáticamente:
1. Base de conocimiento desde archivos JSON
2. Patrones de venta exitosos
3. Recomendaciones inteligentes
4. Casos de uso aprendidos

## Archivos de Conocimiento

El sistema busca conocimiento en este orden:
1. `base_conocimiento_final.json` (prioridad más alta)
2. `conocimiento_completo.json`
3. `base_conocimiento_exportada.json`
4. `base_conocimiento_demo.json`

Si no encuentra ningún archivo, el sistema funciona sin conocimiento previo.

## Solución de Problemas

### Error: "Python not found"
- Instala Python 3.11 o 3.12
- Durante la instalación, marca "Add Python to PATH"
- O instala desde Microsoft Store: "Python 3.11"

### Error: "ModuleNotFoundError"
- Verifica que estés en el directorio correcto del proyecto
- Ejecuta: `python verificar_instalacion.py`

### Error de Encoding (emojis)
- El sistema ya está configurado para Windows
- Si ves caracteres raros, el sistema funciona igual

## Uso del Chatbot

Una vez ejecutado, puedes:
- 👋 Saludar al chatbot
- 📋 Solicitar cotizaciones
- ℹ️ Consultar información de productos
- 💰 Preguntar precios

Para salir, escribe: `salir`, `exit`, `chau`, `adios`, o `bye`

## Características Integradas

✅ **Sistema de Cotizaciones Inteligente**
- Usa base de conocimiento para precios
- Aplica patrones de venta exitosos
- Genera recomendaciones personalizadas

✅ **IA Conversacional**
- Aprende de cada interacción
- Proporciona respuestas contextuales
- Mejora continuamente

✅ **Base de Conocimiento Dinámica**
- Carga conocimiento entrenado
- Aprende de nuevas interacciones
- Genera insights automáticos

