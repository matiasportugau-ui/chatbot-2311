# Guía para Ejecutar los Análisis

## Opción 1: Script Automático (Windows)

Ejecuta el script batch que ejecuta todos los análisis en secuencia:

```batch
ejecutar_analisis_completo.bat
```

Este script:
1. Busca Python automáticamente
2. Ejecuta todos los análisis en orden
3. Genera todos los reportes
4. Muestra los resultados

## Opción 2: Ejecutar Manualmente

Si prefieres ejecutar cada análisis por separado:

### 1. Analizar Conocimiento
```bash
python analizar_conocimiento.py
```
Genera:
- `reporte_analisis_conocimiento.json`
- `reporte_analisis_conocimiento.txt`

### 2. Analizar Escenarios
```bash
python analizar_escenarios.py
```
Genera:
- `reporte_analisis_escenarios.json`
- `reporte_analisis_escenarios.txt`

### 3. Auditar Productos
```bash
python auditar_productos.py
```
Genera:
- `reporte_auditoria_productos.json`
- `reporte_auditoria_productos.txt`

### 4. Validar Integración
```bash
python validar_integracion.py
```
Genera:
- `reporte_validacion.json`
- `reporte_validacion.txt`

### 5. Probar Respuestas
```bash
python test_respuestas_chatbot.py
```
Genera:
- `reporte_pruebas_respuestas.json`
- `reporte_pruebas_respuestas.txt`

## Requisitos

- Python 3.8 o superior
- Dependencias instaladas: `pip install -r requirements.txt`

## Solución de Problemas

### Python no encontrado

**Windows:**
1. Instala Python desde [python.org](https://www.python.org/downloads/)
2. Durante la instalación, marca "Add Python to PATH"
3. O instala desde Microsoft Store: busca "Python 3.11"

**Verificar instalación:**
```bash
python --version
```

### Errores de importación

Si hay errores al importar módulos:
```bash
pip install -r requirements.txt
```

### Archivos no encontrados

Asegúrate de ejecutar los scripts desde el directorio raíz del proyecto:
```bash
cd "C:\Users\usuario\Clone repo coti inteligente\bmc-cotizacion-inteligente"
```

## Resultados Esperados

Después de ejecutar todos los análisis, deberías tener:

1. **Reportes de análisis** que muestran:
   - Qué archivos de conocimiento existen
   - Cuántas interacciones/patrones/productos hay
   - Cuál es el archivo más completo

2. **Reporte de validación** que confirma:
   - Que el conocimiento se carga correctamente
   - Que la IA funciona
   - Que los productos están integrados

3. **Reporte de pruebas** que muestra:
   - Calidad de las respuestas
   - Satisfacción promedio
   - Áreas de mejora

## Próximos Pasos

Después de ejecutar los análisis:

1. Revisa los reportes generados
2. Si hay problemas, revisa la sección de solución de problemas
3. Si todo está bien, puedes usar el chatbot:
   ```bash
   python api_server.py
   ```

