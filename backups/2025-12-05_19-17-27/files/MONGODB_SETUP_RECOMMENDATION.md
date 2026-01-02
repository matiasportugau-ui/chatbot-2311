# 🗄️ Recomendación: MongoDB Setup

## ✅ **RECOMENDACIÓN: Usar Docker**

### ¿Por qué Docker?

1. **✅ Facilidad de instalación**
   - No necesitas instalar MongoDB manualmente
   - Un solo comando y está listo
   - Funciona igual en Mac, Linux y Windows

2. **✅ Aislamiento**
   - No contamina tu sistema
   - Fácil de eliminar si no lo necesitas
   - No interfiere con otras aplicaciones

3. **✅ Portabilidad**
   - Misma configuración en desarrollo y producción
   - Fácil de compartir con el equipo
   - Versionado controlado

4. **✅ Gestión simple**
   - Iniciar: `docker start mongodb`
   - Detener: `docker stop mongodb`
   - Ver logs: `docker logs mongodb`

5. **✅ Ya tienes Docker instalado**
   - Docker v29.0.1 detectado ✅
   - No necesitas instalar nada más

---

## 📊 Comparación

| Característica | Docker | MongoDB Local |
|---------------|--------|---------------|
| **Instalación** | ⭐⭐⭐⭐⭐ 1 comando | ⭐⭐ Manual, múltiples pasos |
| **Mantenimiento** | ⭐⭐⭐⭐⭐ Automático | ⭐⭐⭐ Requiere actualizaciones |
| **Aislamiento** | ⭐⭐⭐⭐⭐ Completo | ⭐⭐ Comparte sistema |
| **Portabilidad** | ⭐⭐⭐⭐⭐ Excelente | ⭐⭐⭐ Limitada |
| **Rendimiento** | ⭐⭐⭐⭐ Muy bueno | ⭐⭐⭐⭐⭐ Óptimo |
| **Recomendado para** | Desarrollo y producción | Solo producción avanzada |

---

## 🚀 Setup con Docker (Recomendado)

### Opción 1: Script Automático

```bash
# Ejecuta este script
./setup_mongodb_docker.sh
```

### Opción 2: Manual

```bash
# 1. Crear contenedor MongoDB
docker run -d \
  --name mongodb \
  -p 27017:27017 \
  -v mongodb_data:/data/db \
  mongo:latest

# 2. Verificar que está corriendo
docker ps | grep mongodb

# 3. Probar conexión
docker exec -it mongodb mongosh --eval "db.version()"
```

---

## 📝 Setup MongoDB Local (Alternativa)

Si prefieres MongoDB local:

### macOS (Homebrew)
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

### Desventajas
- Requiere instalación manual
- Actualizaciones más complejas
- Puede interferir con otras apps
- Configuración más compleja

---

## 🎯 Recomendación Final

**Para tu caso: Usa Docker** porque:

1. ✅ Ya tienes Docker instalado
2. ✅ Es más fácil de mantener
3. ✅ Tu `.env.local` ya está configurado para `localhost:27017`
4. ✅ Funciona perfectamente con Docker
5. ✅ Fácil de eliminar si no lo necesitas

---

## 🔧 Configuración Actual

Tu `.env.local` ya tiene:
```
MONGODB_URI=mongodb://localhost:27017/bmc_chat
```

Esta configuración funciona perfectamente con Docker. Solo necesitas iniciar el contenedor.

---

## 📚 Próximos Pasos

1. Ejecuta el script de setup: `./setup_mongodb_docker.sh`
2. Verifica la conexión: `python verificacion_completa_ejecucion.py`
3. ¡Listo! El chatbot puede usar MongoDB

---

## ❓ ¿Cuándo usar MongoDB Local?

Solo si:
- Necesitas máximo rendimiento
- Tienes experiencia administrando MongoDB
- Requieres configuración avanzada
- Es para producción en servidor dedicado

Para desarrollo y la mayoría de casos: **Docker es la mejor opción** ✅

