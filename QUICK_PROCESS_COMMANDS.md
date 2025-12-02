# ⚡ Comandos Rápidos para Gestión de Procesos

## 🔍 Ver Estado (Elige uno)

```bash
# Opción 1: Rápido y simple
./check_processes.sh

# Opción 2: Detallado con Python
python3 gestionar_procesos.py status

# Opción 3: Ver solo procesos Python
ps aux | grep -E "(chat_interactivo|api_server|sistema_completo)" | grep -v grep

# Opción 4: Ver solo puertos en uso
lsof -i -P -n | grep LISTEN
```

## 🛑 Detener Proceso

```bash
# Interactivo (recomendado)
python3 gestionar_procesos.py stop

# Por PID
kill <PID>              # Elegante
kill -9 <PID>           # Forzar

# Por nombre
pkill -f chat_interactivo.py
```

## 🚀 Iniciar Servicio

```bash
# Chat interactivo
python3 chat_interactivo.py

# API Server
python3 api_server.py

# Sistema completo
python3 sistema_completo_integrado.py
```

## 🐳 Docker

```bash
# Estado
docker ps -a | grep bmc

# Iniciar MongoDB
python3 gestionar_servicios.py

# Detener
docker stop bmc-mongodb
```

## 📚 Más Info

Ver guía completa: `GESTIONAR_PROCESOS_README.md`
