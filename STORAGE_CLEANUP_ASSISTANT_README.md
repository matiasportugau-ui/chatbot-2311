# Storage Cleanup Assistant

## 📋 Descripción

Asistente de IA que analiza el uso de almacenamiento local en tu workspace y proporciona recomendaciones inteligentes de limpieza basadas en análisis detallado.

## ✨ Características

- ✅ **Análisis Completo**: Escanea todo el workspace recursivamente
- ✅ **Identificación Inteligente**: Detecta archivos grandes, duplicados, temporales, caches
- ✅ **Recomendaciones Priorizadas**: Categoriza por prioridad (alta/media/baja)
- ✅ **Cálculo de Ahorro**: Calcula el espacio potencial que se puede liberar
- ✅ **Ejemplos Específicos**: Muestra archivos concretos a revisar
- ✅ **Reportes Detallados**: Genera reportes JSON completos
- ✅ **Basado en Prompt Engineering**: Usa mejores prácticas de prompt engineering

## 🚀 Uso Rápido

### Análisis Básico

```bash
python3 storage_cleanup_assistant.py
```

### Análisis y Guardar Reporte

```bash
python3 storage_cleanup_assistant.py --save
```

### Análisis de Workspace Específico

```bash
python3 storage_cleanup_assistant.py --workspace /ruta/al/workspace --save
```

## 📊 Resultados del Análisis Actual

### Resumen General
- **Tamaño total**: 22.94 GB
- **Total archivos**: 315,107
- **Total directorios**: 33,016

### Recomendaciones de Limpieza

#### 🔴 Alta Prioridad (4 categorías)

1. **Archivos Grandes** (1,848 MB potenciales)
   - 281 archivos >10MB
   - Incluye objetos Git grandes, backups de WhatsApp, caches de webpack

2. **Node Modules** (966 MB potenciales)
   - 49 directorios node_modules
   - Pueden regenerarse con `npm install`

3. **Cache Directories** (16,789 MB potenciales)
   - 138 directorios de cache
   - Incluye: __pycache__, .next, .mypy_cache, .cursor/.mypy_cache
   - Se regeneran automáticamente

4. **Archivos Temporales** (741 MB potenciales)
   - 32,823 archivos temporales
   - .log, .bak, .tmp files

#### 🟡 Media Prioridad (2 categorías)

1. **Backups** (21,252 MB potenciales)
   - Directorio de backups completo
   - Considerar comprimir o mover backups antiguos

2. **Tipos de Archivo Grandes**
   - .pack files (14,770 MB)
   - .py files (1,367 MB)
   - .so files (1,154 MB)

#### 🟢 Baja Prioridad (1 categoría)

1. **Archivos Antiguos** (109 MB potenciales)
   - Archivos no modificados en 6+ meses

### 💾 Ahorro Total Potencial

**41,707 MB (40.7 GB)** - 177.5% del tamaño actual
*(Nota: El porcentaje >100% indica que hay duplicados/backups que se cuentan múltiples veces)*

## 🎯 Acciones Recomendadas

### Inmediatas (Alta Prioridad)

1. **Limpiar Caches** (16.8 GB)
   ```bash
   # Python caches
   find . -type d -name __pycache__ -exec rm -r {} +
   find . -type d -name .mypy_cache -exec rm -r {} +
   
   # Next.js cache
   rm -rf .next
   
   # Cursor cache
   rm -rf .cursor/.mypy_cache
   ```

2. **Limpiar Archivos Temporales** (741 MB)
   ```bash
   find . -name "*.log" -type f -delete
   find . -name "*.bak" -type f -delete
   find . -name "*.tmp" -type f -delete
   ```

3. **Revisar Node Modules** (966 MB)
   ```bash
   # Si no necesitas node_modules localmente
   rm -rf node_modules
   rm -rf nextjs-app/node_modules
   # Luego reinstalar cuando sea necesario: npm install
   ```

### Revisar y Decidir (Media Prioridad)

1. **Backups Antiguos** (21.2 GB)
   - Revisar backups en `./backups/`
   - Mantener solo los últimos 7-30 días
   - Comprimir backups antiguos antes de eliminar
   - Considerar mover a almacenamiento externo

2. **Archivos Grandes** (1.8 GB)
   - Revisar objetos Git grandes en `.git/objects/`
   - Considerar `git gc` para optimizar repositorio
   - Revisar backups de WhatsApp si no son necesarios

### Opcional (Baja Prioridad)

1. **Archivos Antiguos** (109 MB)
   - Revisar archivos no modificados en 6+ meses
   - Archivar o eliminar si no son necesarios

## 📁 Estructura del Reporte

El reporte JSON incluye:

```json
{
  "analysis": {
    "total_size": 23493260000,
    "file_count": 315107,
    "largest_files": [...],
    "file_types": {...},
    "cache_directories": [...],
    "node_modules": [...],
    "backups": [...]
  },
  "recommendations": [
    {
      "category": "Cache Directories",
      "priority": "high",
      "potential_savings_mb": 16789.41,
      "suggestions": [...],
      "items": [...]
    }
  ],
  "summary": {
    "workspace_size_mb": 23493.26,
    "total_potential_savings_mb": 41707.35,
    "potential_savings_percentage": 177.5
  }
}
```

## 🔧 Personalización

### Cambiar Umbrales

Edita `storage_cleanup_assistant.py`:

```python
# Archivos grandes (>10MB por defecto)
if size > 10 * 1024 * 1024:  # Cambiar a otro valor

# Archivos antiguos (>90 días por defecto)
if mtime < datetime.now() - timedelta(days=90):  # Cambiar días
```

### Agregar Patrones Personalizados

```python
# En StorageAnalyzer.analyze_storage()
if any(item.name.endswith(ext) for ext in ['.tmp', '.bak', '.log', '.cache', '.tu_extension']):
    # Agregar a temporary_files
```

## 📚 Recursos de Prompt Engineering

El asistente está basado en los recursos de prompt engineering encontrados en el workspace:

- `PROMPT_ENGINEERING_KNOWLEDGE_BASE.md` - Base de conocimiento completa
- `prompt_generator.py` - Generador de prompts
- `storage_cleanup_assistant_prompt.txt` - Prompt específico del asistente

## 🛡️ Seguridad

El asistente **NUNCA elimina archivos automáticamente**. Solo:
- ✅ Analiza y reporta
- ✅ Sugiere acciones
- ✅ Calcula ahorros potenciales

**Tú decides qué eliminar** basándote en las recomendaciones.

## 📝 Ejemplo de Uso

```bash
# 1. Ejecutar análisis
python3 storage_cleanup_assistant.py --save

# 2. Revisar reporte JSON
cat storage_cleanup_report_*.json | jq '.summary'

# 3. Revisar recomendaciones de alta prioridad
cat storage_cleanup_report_*.json | jq '.recommendations[] | select(.priority=="high")'

# 4. Tomar acciones basadas en recomendaciones
# (ejecutar comandos de limpieza manualmente)
```

## 🎯 Próximos Pasos

1. **Revisar el reporte JSON** generado
2. **Priorizar acciones** basadas en ahorro potencial
3. **Ejecutar limpieza** de caches y temporales (seguro)
4. **Revisar backups** y decidir qué mantener
5. **Ejecutar análisis periódico** para mantener workspace limpio

## 💡 Tips

- Ejecuta el análisis periódicamente (semanal/mensual)
- Revisa backups antes de eliminar
- Los caches se regeneran automáticamente
- node_modules se puede reinstalar con `npm install`
- Mantén solo backups recientes (últimos 7-30 días)

---

**¡Mantén tu workspace limpio y optimizado!** 🧹✨



