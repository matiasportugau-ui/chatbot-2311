#!/bin/bash

# Script para gestionar procesos del proyecto

case "$1" in
    listar|list)
        echo "=== Procesos de Cursor ==="
        ps aux | grep -E "(cursor|exec-daemon)" | grep -v grep
        echo ""
        echo "=== Procesos del Proyecto ==="
        ps aux | grep -E "(api_server|chatbot|demo|sistema|nextjs|python.*main|node.*start)" | grep -v grep
        echo ""
        echo "=== Puertos en uso ==="
        ss -tlnp | grep -E ":(3000|5000|8000|8080|26053|5173)" || netstat -tlnp 2>/dev/null | grep -E ":(3000|5000|8000|8080|26053|5173)"
        ;;
    
    detener|stop)
        if [ -z "$2" ]; then
            echo "Uso: $0 detener <PID o nombre>"
            echo "Ejemplo: $0 detener 1234"
            echo "Ejemplo: $0 detener api_server"
            exit 1
        fi
        
        if [[ "$2" =~ ^[0-9]+$ ]]; then
            echo "Deteniendo proceso PID: $2"
            kill "$2" 2>/dev/null || echo "No se pudo detener el proceso $2"
        else
            echo "Deteniendo procesos que coinciden con: $2"
            pkill -f "$2" || echo "No se encontraron procesos que coincidan con '$2'"
        fi
        ;;
    
    matar|kill)
        if [ -z "$2" ]; then
            echo "Uso: $0 matar <PID o nombre>"
            exit 1
        fi
        
        if [[ "$2" =~ ^[0-9]+$ ]]; then
            echo "Forzando detención del proceso PID: $2"
            kill -9 "$2" 2>/dev/null || echo "No se pudo forzar la detención del proceso $2"
        else
            echo "Forzando detención de procesos que coinciden con: $2"
            pkill -9 -f "$2" || echo "No se encontraron procesos que coincidan con '$2'"
        fi
        ;;
    
    puerto|port)
        if [ -z "$2" ]; then
            echo "Uso: $0 puerto <número_puerto>"
            exit 1
        fi
        echo "Procesos usando el puerto $2:"
        lsof -i :"$2" || ss -tlnp | grep ":$2" || echo "No se encontraron procesos usando el puerto $2"
        ;;
    
    logs)
        if [ -z "$2" ]; then
            echo "Buscando archivos de log..."
            find . -name "*.log" -type f 2>/dev/null | head -10
            echo ""
            echo "Últimas líneas del log de Cursor:"
            tail -20 ~/.cursor.log 2>/dev/null || echo "No se encontró el log de Cursor"
        else
            if [ -f "$2" ]; then
                tail -f "$2"
            else
                echo "Archivo no encontrado: $2"
            fi
        fi
        ;;
    
    ayuda|help|--help|-h)
        echo "Gestor de Procesos - Uso:"
        echo ""
        echo "  $0 listar              - Lista todos los procesos relevantes"
        echo "  $0 detener <PID|nombre> - Detiene un proceso de forma suave"
        echo "  $0 matar <PID|nombre>   - Fuerza la detención de un proceso"
        echo "  $0 puerto <número>      - Muestra qué proceso usa un puerto"
        echo "  $0 logs [archivo]       - Muestra logs (o sigue un archivo de log)"
        echo ""
        echo "Ejemplos:"
        echo "  $0 listar"
        echo "  $0 detener 1234"
        echo "  $0 detener api_server"
        echo "  $0 puerto 3000"
        echo "  $0 logs"
        ;;
    
    *)
        echo "Comando no reconocido: $1"
        echo "Usa '$0 ayuda' para ver los comandos disponibles"
        exit 1
        ;;
esac
