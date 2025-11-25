# Instrucciones para Ejecutar los Próximos Pasos

## ⚠️ Nota Importante

Python no está configurado en el PATH del sistema. Necesitas configurarlo primero o usar la ruta completa.

## Opción 1: Usar el Script Batch (Más Fácil)

1. **Abre PowerShell o CMD** en el directorio del proyecto
2. **Ejecuta:**
   ```batch
   ejecutar_analisis_completo.bat
   ```

Este script:
- Busca Python automáticamente
- Ejecuta todos los análisis en orden
- Genera todos los reportes

## Opción 2: Ejecutar Manualmente

### Paso 1: Verificar Python

Abre PowerShell y ejecuta:
```powershell
python --version
```

Si no funciona, prueba:
```powershell
python3 --version
```

O busca Python instalado:
```powershell
Get-Command python -ErrorAction SilentlyContinue
```

### Paso 2: Si Python no está en PATH

**Opción A: Agregar Python al PATH**
1. Busca dónde está instalado Python (normalmente `C:\Users\TuUsuario\AppData\Local\Programs\Python\Python3XX`)
2. Agrega esa carpeta al PATH del sistema

**Opción B: Usar ruta completa**
```powershell
# Reemplaza con tu ruta real
C:\Users\usuario\AppData\Local\Programs\Python\Python311\python.exe analizar_conocimiento.py
```

**Opción C: Instalar Python**
1. Ve a [python.org/downloads](https://www.python.org/downloads/)
2. Descarga Python 3.11 o superior
3. Durante la instalación, **marca "Add Python to PATH"**
4. Reinicia PowerShell/CMD

### Paso 3: Ejecutar los Análisis

Una vez que Python funciona, ejecuta en orden:

```powershell
# 1. Analizar conocimiento
python analizar_conocimiento.py

# 2. Analizar escenarios
python analizar_escenarios.py

# 3. Auditar productos
python auditar_productos.py

# 4. Validar integración
python validar_integracion.py

# 5. Probar respuestas
python test_respuestas_chatbot.py
```

## Opción 3: Usar Visual Studio Code

Si tienes VS Code instalado:

1. Abre el proyecto en VS Code
2. Abre la terminal integrada (Ctrl + `)
3. Ejecuta los scripts desde ahí
4. VS Code normalmente detecta Python automáticamente

## Qué Esperar

Cada script generará:

1. **analizar_conocimiento.py**:
   - `reporte_analisis_conocimiento.json`
   - `reporte_analisis_conocimiento.txt`
   - Muestra qué archivos de conocimiento existen y cuál es el más completo

2. **analizar_escenarios.py**:
   - `reporte_analisis_escenarios.json`
   - `reporte_analisis_escenarios.txt`
   - Muestra qué escenarios de prueba hay y qué cubren

3. **auditar_productos.py**:
   - `reporte_auditoria_productos.json`
   - `reporte_auditoria_productos.txt`
   - Muestra qué productos están integrados

4. **validar_integracion.py**:
   - `reporte_validacion.json`
   - `reporte_validacion.txt`
   - Verifica que todo funciona correctamente

5. **test_respuestas_chatbot.py**:
   - `reporte_pruebas_respuestas.json`
   - `reporte_pruebas_respuestas.txt`
   - Prueba la calidad de las respuestas

## Solución Rápida: Instalar Python

La forma más rápida de tener Python funcionando:

1. **Abre Microsoft Store**
2. **Busca "Python 3.11"**
3. **Instala**
4. **Reinicia PowerShell**
5. **Ejecuta:** `python --version`

## Verificación Rápida

Para verificar que todo está listo:

```powershell
# Verificar Python
python --version

# Verificar que los scripts existen
Test-Path analizar_conocimiento.py
Test-Path validar_integracion.py
Test-Path test_respuestas_chatbot.py

# Si todos devuelven True, estás listo
```

## Siguiente Paso

Una vez que los análisis se ejecuten exitosamente:

1. Revisa los reportes generados
2. Si hay problemas, revisa los mensajes de error
3. Si todo está bien, puedes usar el chatbot:
   ```powershell
   python api_server.py
   ```

