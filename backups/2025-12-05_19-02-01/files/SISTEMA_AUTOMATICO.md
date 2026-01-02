# Sistema Automático - Chatbot BMC Uruguay

Este documento explica cómo funciona el sistema automático que mantiene el chatbot actualizado sin intervención manual.

## 🚀 Componentes Automáticos

### 1. GitHub Actions Workflow
**Archivo:** `.github/workflows/auto-update-products.yml`

**Funcionalidad:**
- Se ejecuta automáticamente cada día a las 3 AM UTC (medianoche en Uruguay)
- Actualiza todos los productos desde `bmcuruguay.com.uy`
- Sincroniza precios y descripciones
- Hace commit y push automático de los cambios

**Activación:**
- Automática: Se ejecuta según el cron schedule
- Manual: Puedes ejecutarlo desde GitHub Actions → "Run workflow"

### 2. Background Agent (Local)
**Archivo:** `background_agent.py`

**Funcionalidad:**
- Se ejecuta como proceso en segundo plano
- Actualiza productos cada 6 horas
- Sincroniza precios cada 2 horas
- Genera logs en `background_agent.log`

**Uso:**
```bash
python background_agent.py
```

**Para Windows (ejecutar en segundo plano):**
```bash
start /B python background_agent.py
```

## 📋 Tareas Automáticas

### Actualización de Productos
- **Frecuencia:** Cada 6 horas (o diariamente vía GitHub Actions)
- **Proceso:**
  1. Consulta la API de Shopify (`/products.json`)
  2. Extrae información de cada producto (título, precio, descripción, imágenes)
  3. Actualiza `productos_mapeados.json`
  4. Sincroniza con `matriz_precios.json`

### Sincronización de Precios
- **Frecuencia:** Cada 2 horas
- **Proceso:**
  1. Consulta precios actualizados desde la web
  2. Actualiza el sistema de cotizaciones
  3. Mantiene caché para evitar sobrecarga

## 🔧 Configuración

### Variables de Entorno
El sistema usa las siguientes variables (opcionales):

```bash
# Desactivar sincronización web (usar solo datos locales)
BMC_SKIP_WEB_PRICES=true

# Usar IA completa con conocimiento cargado
CHAT_USE_FULL_IA=true
```

### Logs
- **GitHub Actions:** Ver en la pestaña "Actions" del repositorio
- **Background Agent:** Archivo `background_agent.log` en la raíz del proyecto

## 🎯 Flujo Completo

```
┌─────────────────────────────────────────────────┐
│  GitHub Actions (Diario - 3 AM UTC)             │
│  └─> Actualiza productos desde web              │
│      └─> Commit automático de cambios           │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  Background Agent (Cada 2-6 horas)              │
│  └─> Sincroniza precios                        │
│  └─> Actualiza productos                       │
│      └─> Logs en background_agent.log          │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  Chatbot Interactivo                           │
│  └─> Usa datos actualizados automáticamente     │
│  └─> Comparte links e imágenes de productos    │
└─────────────────────────────────────────────────┘
```

## 📊 Monitoreo

### Verificar Estado
1. **GitHub Actions:** Revisa la última ejecución en la pestaña "Actions"
2. **Background Agent:** Revisa `background_agent.log` para ver actividad reciente
3. **Productos:** Verifica `productos_mapeados.json` para ver última actualización

### Verificar Actualización
```bash
# Ver última actualización en productos_mapeados.json
python -c "import json; data=json.load(open('productos_mapeados.json')); print('Productos:', len(data))"
```

## 🛠️ Solución de Problemas

### GitHub Actions no se ejecuta
- Verifica que el workflow esté en la rama correcta
- Revisa los logs en la pestaña "Actions"
- Verifica permisos del repositorio

### Background Agent no actualiza
- Revisa `background_agent.log` para errores
- Verifica conexión a internet
- Asegúrate de que `mapeador_productos_web.py` funcione correctamente

### Precios desactualizados
- Ejecuta manualmente: `python mapeador_productos_web.py`
- Verifica que la web esté accesible
- Revisa logs para errores de conexión

## 🔐 Seguridad

- Las API keys NO están en el código (usar GitHub Secrets)
- Los logs no contienen información sensible
- Los commits automáticos usan un usuario especial de GitHub Actions

## 📝 Notas Importantes

1. **Primera Ejecución:** El sistema puede tardar varios minutos en mapear todos los productos
2. **Rate Limiting:** El sistema incluye pausas entre peticiones para no sobrecargar el servidor
3. **Fallback:** Si la web no está disponible, el sistema usa datos locales almacenados

## ✅ Checklist de Configuración

- [ ] GitHub Actions workflow activo
- [ ] Background Agent configurado (opcional, para ejecución local)
- [ ] Variables de entorno configuradas (si es necesario)
- [ ] Logs funcionando correctamente
- [ ] Primera actualización ejecutada exitosamente

---

**El sistema está diseñado para funcionar completamente automático. Una vez configurado, no requiere intervención manual.**

