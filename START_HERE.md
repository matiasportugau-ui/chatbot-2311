# 🚀 START HERE - BMC Chatbot System

## ⚡ Inicio Rápido - Unified Launcher (Recomendado)

El **Unified Launcher** es la forma más fácil de iniciar el sistema. Maneja automáticamente la instalación de dependencias, configuración del entorno y ejecución de todos los modos.

### Windows

```batch
launch.bat
```

O directamente:
```bash
python unified_launcher.py
```

### Linux/Mac

```bash
./launch.sh
```

O directamente:
```bash
python unified_launcher.py
```

### ¿Qué hace el Unified Launcher?

✅ **Instala dependencias automáticamente** (Python y Node.js)  
✅ **Configura el entorno** (crea .env si falta)  
✅ **Verifica requisitos** (Python 3.11+, Node.js opcional)  
✅ **Menú interactivo** con todos los modos disponibles  
✅ **Gestión de servicios** (API, MongoDB, Next.js)  

## 📋 Modos Disponibles

El launcher ofrece estos modos:

1. **Interactive Chatbot** - Chat interactivo en terminal
2. **API Server** - Servidor FastAPI (puerto 8000)
3. **Chat Simulator** - Simulador de conversaciones
4. **Enhanced CLI Simulator** - Simulador mejorado con formato
5. **Main System Menu** - Menú del sistema completo
6. **Automated Agent System** - Sistema de agentes automatizado
7. **System Complete** - Sistema completo integrado
8. **Next.js Dashboard (Dev)** - Dashboard de desarrollo
9. **Next.js Dashboard (Production)** - Dashboard de producción
10. **Full Stack** - API + Dashboard juntos

## 🚀 Ejecución Directa (Sin Menú)

También puedes ejecutar modos directamente:

```bash
# Chat interactivo
python unified_launcher.py --mode chat

# API Server
python unified_launcher.py --mode api

# Simulador
python unified_launcher.py --mode simulator

# Full Stack (API + Dashboard)
python unified_launcher.py --mode fullstack

# Solo setup (sin ejecutar nada)
python unified_launcher.py --setup-only

# Saltar setup (asume que ya está configurado)
python unified_launcher.py --skip-setup --mode chat
```

## 📚 Alternativa: Inicio Manual

Si prefieres iniciar componentes manualmente:

### Terminal 1 - API Server:
```bash
python api_server.py
```

### Terminal 2 - Simulador:
```bash
python simulate_chat_cli.py
```

O usa el script todo-en-uno:
```bash
./start_simulator.sh
```

## 💬 Tu Primera Conversación

Una vez que ambos terminales estén corriendo, en el simulador escribe:

```
Hola
Quiero cotizar Isodec
10 metros por 5 metros
100mm
Blanco
```

¡Y verás las respuestas del bot en tiempo real!

## 📚 Documentación Completa

- **`UNIFIED_LAUNCHER.md`** - ⭐ Documentación completa del Unified Launcher
- **`HOW_TO_RUN.md`** - Guía detallada de ejecución
- **`QUICK_RUN.md`** - Inicio rápido del simulador
- **`README.md`** - Documentación general del sistema
- **`README_SIMULATOR.md`** - Documentación completa del simulador
- **`QUICK_START_SIMULATOR.md`** - Inicio rápido del simulador

## 🎯 ¿Qué Puedes Hacer?

✅ Chatear con el bot usando lógica real  
✅ Probar diferentes conversaciones  
✅ Poblar knowledge base con escenarios  
✅ Iterar en prompts y mejorar respuestas  
✅ Exportar conversaciones para análisis  
✅ Ver estadísticas y métricas  

## 🆘 Problemas?

1. **Python no encontrado**: Instala Python 3.11+ desde https://www.python.org/downloads/
2. **Dependencias faltantes**: El launcher las instala automáticamente, o ejecuta `pip install -r requirements.txt`
3. **API no conecta**: Usa `python unified_launcher.py --mode fullstack` para iniciar todo junto
4. **OpenAI errors**: Configura `OPENAI_API_KEY` en el archivo `.env` (el launcher te ayuda)
5. **MongoDB errors**: El sistema funciona sin MongoDB (sin persistencia)
6. **Puerto ocupado**: El launcher detecta puertos ocupados y te avisa

## ✨ Comandos Útiles del CLI

Cuando uses `simulate_chat_cli.py`:

- `/help` - Ver comandos
- `/new` - Nueva sesión  
- `/history` - Ver historial
- `/export` - Exportar conversación
- `/stats` - Estadísticas KB
- `/exit` - Salir

## 📚 Referencias de Comandos

Para una guía completa de comandos Git, Node.js, deployment y más:
- **[CHEAT_SHEET_CLI.md](../CHEAT_SHEET_CLI.md)** - ⚡ Cheat sheet completo con todos los comandos organizados

**Comandos rápidos más usados:**
```bash
# Desarrollo
npm run dev              # Iniciar servidor de desarrollo
npm run build            # Compilar para producción
npm run lint             # Ejecutar linter

# Git
git status -sb           # Estado resumido
git switch -c <RAMA>     # Crear nueva rama
git commit -m "<MSG>"    # Hacer commit
git push -u origin <RAMA> # Push con upstream
```

---

**¡Listo para empezar!** 🎉

Ejecuta los 3 pasos de arriba y estarás chateando con el bot en minutos.

