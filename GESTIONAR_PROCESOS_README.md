# 🎛️ Guía de Gestión de Procesos del Proyecto BMC

Esta guía te ayuda a gestionar todos los procesos y servicios del proyecto desde Cursor.

## 📋 Estado Actual

Para ver el estado actual de todos los procesos y servicios:

```bash
# Opción 1: Script bash simple y rápido
./check_processes.sh

# Opción 2: Script Python con más funcionalidades
python3 gestionar_procesos.py status
```

## 🚀 Iniciar Servicios

### Chat Interactivo
```bash
python3 chat_interactivo.py
```

### API Server
```bash
python3 api_server.py
```

### Sistema Completo Integrado
```bash
python3 sistema_completo_integrado.py
```

### Sistema Automatizado con Agentes
```bash
python3 automated_agent_system.py
```

## 🛑 Detener Procesos

### Modo Interactivo (Recomendado)
```bash
python3 gestionar_procesos.py stop
```
Te mostrará una lista de procesos activos y podrás seleccionar cuál detener.

### Detener por PID
```bash
# Detención elegante
python3 gestionar_procesos.py stop <PID>

# Forzar detención
python3 gestionar_procesos.py kill <PID>

# Detención manual
kill <PID>
kill -9 <PID>  # Forzar
```

### Detener Todos los Procesos Python del Proyecto
```bash
pkill -f "chat_interactivo.py"
pkill -f "api_server.py"
pkill -f "sistema_completo_integrado.py"
```

## 🐳 Gestionar Contenedores Docker

### Ver Contenedores
```bash
docker ps -a | grep -E "(bmc|mongo|n8n)"
```

### Iniciar MongoDB
```bash
python3 gestionar_servicios.py
# o manualmente:
docker start bmc-mongodb
```

### Detener Contenedores
```bash
docker stop bmc-mongodb
docker stop <nombre-contenedor>
```

### Ver Logs
```bash
docker logs bmc-mongodb
docker logs -f bmc-mongodb  # Seguir logs en tiempo real
```

## 🌐 Verificar Puertos en Uso

```bash
# Ver todos los puertos en escucha
lsof -i -P -n | grep LISTEN

# Ver puerto específico
lsof -i :3000
lsof -i :5000
lsof -i :8000
lsof -i :27017  # MongoDB

# Liberar puerto (detener proceso)
lsof -ti :3000 | xargs kill
```

## 🔍 Diagnóstico de Problemas

### Ver Procesos que Consumen Recursos
```bash
# Ordenados por CPU
ps aux | sort -nrk 3 | head -10

# Ordenados por Memoria
ps aux | sort -nrk 4 | head -10

# Herramienta interactiva
htop
```

### Ver Logs del Sistema
```bash
# Logs recientes
tail -f ~/.cursor.log

# Logs de Python (si se configuraron)
tail -f /tmp/bmc-chatbot.log
```

### Verificar Conexiones de Red
```bash
# Ver todas las conexiones
netstat -tulpn

# Conexiones establecidas
ss -t
```

## 🎯 Casos de Uso Comunes

### Problema: Puerto ya en uso
```bash
# 1. Identificar qué está usando el puerto
lsof -i :5000

# 2. Detener el proceso
kill <PID>

# 3. Si no se detiene, forzar
kill -9 <PID>

# 4. Reiniciar tu servicio
python3 api_server.py
```

### Problema: Proceso no responde
```bash
# 1. Ver estado del proceso
python3 gestionar_procesos.py status

# 2. Intentar detención elegante
python3 gestionar_procesos.py stop <PID>

# 3. Si no funciona, forzar
python3 gestionar_procesos.py kill <PID>
```

### Problema: MongoDB no conecta
```bash
# 1. Verificar si el contenedor existe
docker ps -a | grep mongo

# 2. Iniciar si está detenido
docker start bmc-mongodb

# 3. Verificar logs
docker logs bmc-mongodb

# 4. Verificar conexión
nc -zv localhost 27017
```

### Limpiar Todo y Empezar de Nuevo
```bash
# 1. Detener todos los procesos Python del proyecto
pkill -f "chat_interactivo"
pkill -f "api_server"
pkill -f "sistema_completo"
pkill -f "automated_agent"

# 2. Detener contenedores Docker
docker stop $(docker ps -q --filter "name=bmc")
docker stop $(docker ps -q --filter "name=mongo")

# 3. Verificar que todo esté limpio
./check_processes.sh

# 4. Reiniciar servicios necesarios
python3 gestionar_servicios.py  # MongoDB
python3 chat_interactivo.py     # Tu aplicación
```

## 🎨 Alias Útiles

Carga los alias predefinidos:

```bash
source /workspace/.gestionar_alias.sh
```

Después podrás usar:
- `ps-bmc` - Ver estado rápido
- `status-bmc` - Ver estado detallado
- `stop-bmc` - Detener procesos interactivamente
- `kill-bmc <PID>` - Detener proceso específico
- `start-chat` - Iniciar chat interactivo
- `start-api` - Iniciar API server
- `start-system` - Iniciar sistema completo

## 📝 Notas Importantes

1. **Detención Elegante vs Forzada**
   - `kill` o `gestionar_procesos.py stop` → Detención elegante (SIGTERM)
   - `kill -9` o `gestionar_procesos.py kill` → Forzar detención (SIGKILL)
   - Siempre intenta la detención elegante primero

2. **Permisos**
   - Solo puedes detener procesos de tu usuario
   - Para procesos del sistema necesitas `sudo`

3. **Contenedores Docker**
   - Docker puede no estar disponible en todos los entornos
   - El proyecto puede funcionar sin MongoDB (sin persistencia)

4. **Puertos Comunes**
   - 3000: Next.js frontend
   - 5000: API Flask/FastAPI
   - 8000: Servicios alternativos
   - 27017: MongoDB
   - 5678: n8n

## 🆘 Ayuda Rápida

```bash
# Ver ayuda completa del gestor
python3 gestionar_procesos.py help

# Ver este README
cat /workspace/GESTIONAR_PROCESOS_README.md
```

## 🔗 Enlaces Útiles

- [Documentación Principal](README.md)
- [Guía de Instalación](INSTALAR_Y_EJECUTAR.md)
- [Guía de Setup](SETUP_COMPLETE_GUIDE.md)

---

**💡 Tip**: Mantén esta guía abierta mientras trabajas con el proyecto para referencias rápidas.
