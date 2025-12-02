#!/bin/bash
# Script simple para verificar procesos del proyecto BMC

echo "================================================================================"
echo "🔍 ESTADO DE PROCESOS DEL PROYECTO BMC"
echo "================================================================================"
echo ""

# Procesos Python del proyecto
echo "📊 PROCESOS PYTHON ACTIVOS:"
echo "--------------------------------------------------------------------------------"
PYTHON_PROCS=$(ps aux | grep -E "(chat_interactivo|api_server|sistema_completo|automated_agent|ejecutar_sistema|simulate_chat)" | grep -v grep)

if [ -z "$PYTHON_PROCS" ]; then
    echo "✅ No hay procesos Python del proyecto corriendo actualmente"
else
    echo "$PYTHON_PROCS" | while read line; do
        PID=$(echo $line | awk '{print $2}')
        CPU=$(echo $line | awk '{print $3}')
        MEM=$(echo $line | awk '{print $4}')
        CMD=$(echo $line | awk '{for(i=11;i<=NF;i++) printf "%s ", $i; print ""}')
        echo "  PID: $PID | CPU: $CPU% | Memoria: $MEM%"
        echo "  Comando: $CMD"
        echo "--------------------------------------------------------------------------------"
    done
fi
echo ""

# Puertos en escucha
echo "🌐 PUERTOS EN ESCUCHA (comunes del proyecto):"
echo "--------------------------------------------------------------------------------"
for PORT in 3000 5000 5678 8000 8080 27017; do
    LISTENING=$(lsof -i :$PORT -sTCP:LISTEN -t 2>/dev/null)
    if [ ! -z "$LISTENING" ]; then
        PROC_INFO=$(ps -p $LISTENING -o comm= 2>/dev/null)
        echo "  Puerto $PORT: $PROC_INFO (PID: $LISTENING)"
    fi
done
echo ""

# Contenedores Docker
echo "🐳 CONTENEDORES DOCKER:"
echo "--------------------------------------------------------------------------------"
if command -v docker &> /dev/null; then
    CONTAINERS=$(docker ps -a --filter "name=bmc" --filter "name=mongo" --filter "name=n8n" --format "{{.Names}}|{{.Status}}|{{.Ports}}" 2>/dev/null)
    if [ -z "$CONTAINERS" ]; then
        echo "📦 No hay contenedores Docker del proyecto"
    else
        echo "$CONTAINERS" | while IFS='|' read NAME STATUS PORTS; do
            if [[ $STATUS == Up* ]]; then
                echo "  🟢 $NAME - $STATUS"
            else
                echo "  🔴 $NAME - $STATUS"
            fi
            [ ! -z "$PORTS" ] && echo "     Puertos: $PORTS"
        done
    fi
else
    echo "Docker no está instalado o no está disponible"
fi
echo ""

echo "================================================================================"
echo "💡 COMANDOS ÚTILES:"
echo "--------------------------------------------------------------------------------"
echo "  Para detener un proceso Python:   kill <PID>"
echo "  Para forzar detención:            kill -9 <PID>"
echo "  Para detener un contenedor:       docker stop <nombre>"
echo "  Para ver logs de un contenedor:   docker logs <nombre>"
echo "================================================================================"
