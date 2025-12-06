#!/bin/bash
# Script para configurar MongoDB con Docker
# Recomendado para desarrollo y producción

set -e

echo "=========================================="
echo "  MongoDB Setup con Docker"
echo "=========================================="
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker no está instalado${NC}"
    echo "Instala Docker desde: https://www.docker.com/get-started"
    exit 1
fi

echo -e "${GREEN}✅ Docker encontrado${NC}"
echo ""

# Verificar si el contenedor ya existe
if docker ps -a --format '{{.Names}}' | grep -q "^mongodb$"; then
    echo -e "${YELLOW}⚠️  Contenedor MongoDB ya existe${NC}"
    read -p "¿Deseas reiniciarlo? (s/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        echo "Deteniendo contenedor existente..."
        docker stop mongodb 2>/dev/null || true
        echo "Eliminando contenedor existente..."
        docker rm mongodb 2>/dev/null || true
    else
        echo "Iniciando contenedor existente..."
        docker start mongodb
        echo -e "${GREEN}✅ MongoDB iniciado${NC}"
        exit 0
    fi
fi

# Crear volumen para persistencia
echo "Creando volumen para datos..."
docker volume create mongodb_data 2>/dev/null || echo "Volumen ya existe"

# Crear y ejecutar contenedor MongoDB
echo ""
echo "Creando contenedor MongoDB..."
docker run -d \
  --name mongodb \
  -p 27017:27017 \
  -v mongodb_data:/data/db \
  --restart unless-stopped \
  mongo:latest

# Esperar a que MongoDB esté listo
echo ""
echo "Esperando a que MongoDB esté listo..."
sleep 5

# Verificar que está corriendo
if docker ps --format '{{.Names}}' | grep -q "^mongodb$"; then
    echo -e "${GREEN}✅ MongoDB está corriendo${NC}"
else
    echo -e "${RED}❌ Error: MongoDB no está corriendo${NC}"
    echo "Revisa los logs con: docker logs mongodb"
    exit 1
fi

# Probar conexión
echo ""
echo "Probando conexión..."
if docker exec mongodb mongosh --quiet --eval "db.version()" > /dev/null 2>&1; then
    VERSION=$(docker exec mongodb mongosh --quiet --eval "db.version()")
    echo -e "${GREEN}✅ Conexión exitosa${NC}"
    echo "   Versión: $VERSION"
else
    echo -e "${YELLOW}⚠️  No se pudo verificar la versión (puede ser normal)${NC}"
fi

# Mostrar información
echo ""
echo "=========================================="
echo "  MongoDB Configurado Exitosamente"
echo "=========================================="
echo ""
echo "📋 Información:"
echo "   • Contenedor: mongodb"
echo "   • Puerto: 27017"
echo "   • Volumen: mongodb_data (persistente)"
echo ""
echo "🔧 Comandos útiles:"
echo "   • Iniciar:    docker start mongodb"
echo "   • Detener:    docker stop mongodb"
echo "   • Ver logs:   docker logs mongodb"
echo "   • Eliminar:   docker stop mongodb && docker rm mongodb"
echo ""
echo "📊 Tu configuración (.env.local):"
echo "   MONGODB_URI=mongodb://localhost:27017/bmc_chat"
echo ""
echo -e "${GREEN}✅ ¡MongoDB está listo para usar!${NC}"
echo ""

