# Revisión de Dependencias - Sistema Chatbot BMC

**Fecha:** 2025-01-25  
**Proyecto:** chatbot-2311

## 📋 Resumen Ejecutivo

Se han identificado varios problemas en las dependencias del proyecto que requieren atención:

- ✅ **Python (requirements.txt)**: Mayormente correcto, pero con duplicados
- ⚠️ **Node.js (package.json)**: Conflictos de versiones entre apps
- ⚠️ **Dependencias faltantes**: Algunas librerías usadas no están declaradas

---

## 🔍 Análisis Detallado

### 1. Python Dependencies (requirements.txt)

#### ✅ Dependencias Correctas
- FastAPI, uvicorn, pydantic (API framework)
- OpenAI, Groq, Google GenAI (IA models)
- PyMongo (MongoDB)
- GSpread, Google Auth (Google Sheets)
- Requests, BeautifulSoup4 (Web scraping)

#### ⚠️ Problemas Encontrados

**1.1. Dependencia Duplicada**
```python
# Línea 15 y 59
requests>=2.25.1  # Aparece dos veces
```

**1.2. Dependencias Faltantes**
Según el análisis del código y archivos del proyecto, estas dependencias se usan pero no están en `requirements.txt`:
- `qdrant-client` - Para vector database (mencionado en VECTOR_DB_PERFORMANCE_ANALYSIS.md)
- `redis` - Para caching (mencionado en análisis)
- `psutil` - Para monitoreo de sistema (mencionado en análisis)

**1.3. Versiones**
- Todas las versiones usan `>=` lo cual es flexible pero puede causar problemas de compatibilidad
- Considerar usar versiones específicas para producción

---

### 2. Node.js Dependencies

#### ⚠️ Conflictos de Versiones Críticos

**2.1. Next.js**
- **Root (`package.json`)**: `next@^14.0.0`
- **nextjs-app (`nextjs-app/package.json`)**: `next@16.0.3`
- **Problema**: Versiones incompatibles, pueden causar conflictos

**2.2. React**
- **Root**: `react@^18.2.0`, `react-dom@^18.2.0`
- **nextjs-app**: `react@19.2.0`, `react-dom@19.2.0`
- **Problema**: React 19 requiere Next.js 15+, pero root tiene Next.js 14

**2.3. TypeScript**
- **Root**: `typescript@^5.0.0`
- **nextjs-app**: `typescript@^5`
- **Estado**: Compatible, pero debería unificarse

**2.4. Tailwind CSS**
- **Root**: `tailwindcss@^3.3.0`
- **nextjs-app**: `tailwindcss@^4`
- **Problema**: Versiones incompatibles (v4 es mayor breaking change)

---

### 3. Dependencias del Root package.json

#### ✅ Bien Configuradas
- Radix UI components
- AI SDK (`ai@^5.0.78`)
- MongoDB drivers
- Form libraries (react-hook-form, zod)

#### ⚠️ Posibles Problemas
- `colors@^1.4.0` - Librería deprecada, considerar alternativas
- `date-fns@^2.30.0` - Versión antigua, última es v3.x
- `openai@^6.6.0` - Verificar compatibilidad con `ai@^5.0.78`

---

## 🛠️ Recomendaciones

### Prioridad Alta

1. **Eliminar duplicado de `requests` en requirements.txt**
   ```python
   # Eliminar una de las dos líneas 15 o 59
   ```

2. **Unificar versiones de Next.js y React**
   - Decidir si usar Next.js 14 o 16
   - Si Next.js 16: actualizar root package.json
   - Si Next.js 14: actualizar nextjs-app/package.json

3. **Agregar dependencias faltantes a requirements.txt**
   ```python
   qdrant-client>=1.7.0
   redis>=5.0.0
   psutil>=5.9.0
   ```

### Prioridad Media

4. **Actualizar dependencias obsoletas**
   - `date-fns`: Actualizar a v3.x
   - `colors`: Reemplazar o remover si no se usa

5. **Fijar versiones para producción**
   - Considerar usar versiones exactas en producción
   - Mantener `>=` solo en desarrollo

6. **Unificar Tailwind CSS**
   - Decidir entre v3 o v4
   - Tailwind v4 requiere migración significativa

### Prioridad Baja

7. **Revisar dependencias no utilizadas**
   - Ejecutar análisis de dependencias no usadas
   - Limpiar package.json y requirements.txt

8. **Agregar dependencias de desarrollo**
   - Separar devDependencies en requirements.txt
   - Crear `requirements-dev.txt`

---

## 📊 Comparación de Versiones

| Paquete | Root | nextjs-app | Estado |
|---------|------|------------|--------|
| Next.js | 14.0.0 | 16.0.3 | ⚠️ Conflicto |
| React | 18.2.0 | 19.2.0 | ⚠️ Conflicto |
| TypeScript | 5.0.0 | 5 | ✅ Compatible |
| Tailwind | 3.3.0 | 4 | ⚠️ Conflicto |

---

## 🔧 Acciones Inmediatas

### 1. Corregir requirements.txt
```bash
# Eliminar línea duplicada de requests
# Agregar dependencias faltantes
```

### 2. Decidir estrategia de versiones Node.js
- Opción A: Actualizar todo a Next.js 16 + React 19
- Opción B: Mantener Next.js 14 + React 18 en ambos

### 3. Verificar dependencias en uso
```bash
# Python
pip install pipreqs
pipreqs . --force

# Node.js
npm install -g depcheck
depcheck
```

---

## 📝 Checklist de Corrección

- [x] Eliminar duplicado de `requests` en requirements.txt ✅ **COMPLETADO**
- [x] Agregar `qdrant-client`, `redis`, `psutil` a requirements.txt ✅ **COMPLETADO**
- [ ] Unificar versiones de Next.js (14 o 16)
- [ ] Unificar versiones de React (18 o 19)
- [ ] Unificar versiones de Tailwind CSS (3 o 4)
- [ ] Actualizar `date-fns` a v3.x
- [ ] Revisar uso de `colors` package
- [ ] Crear `requirements-dev.txt` para dependencias de desarrollo
- [ ] Ejecutar `npm audit` y `pip-audit` para vulnerabilidades
- [ ] Actualizar package-lock.json después de cambios

---

## 🔒 Seguridad

**Recomendado ejecutar:**
```bash
# Node.js
npm audit
npm audit fix

# Python
pip-audit
pip-audit --fix
```

---

## 📚 Referencias

- [Next.js Migration Guide](https://nextjs.org/docs/app/building-your-application/upgrading)
- [React 19 Upgrade Guide](https://react.dev/blog/2024/04/25/react-19)
- [Tailwind CSS v4 Migration](https://tailwindcss.com/docs/v4-beta)

---

**Generado automáticamente** - Revisar y aplicar cambios según prioridades del proyecto.


