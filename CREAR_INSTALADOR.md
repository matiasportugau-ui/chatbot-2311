# 📦 Guía para Crear el Instalador de BMC Chatbot

Esta guía te explica cómo crear un instalador ejecutable (.exe) para Windows del chatbot BMC.

## 🎯 Opciones Disponibles

### Opción 1: Ejecutable Simple (Sin Instalador)

Crea un archivo `.exe` que se puede ejecutar directamente sin instalación.

### Opción 2: Instalador Completo (Recomendado)

Crea un instalador profesional con Inno Setup que permite:
- Instalación desinstalación fácil
- Accesos directos en el escritorio y menú inicio
- Desinstalador automático

---

## 📋 Requisitos Previos

### 1. Python 3.8 o superior
```powershell
python --version
```

### 2. PyInstaller
Se instalará automáticamente, pero puedes instalarlo manualmente:
```powershell
pip install pyinstaller
```

### 3. Inno Setup (Solo para Opción 2)
- **Descarga:** https://jrsoftware.org/isdl.php
- **Instalación:** Ejecuta el instalador y sigue las instrucciones
- **Gratis y Open Source**

---

## 🚀 Crear el Instalador

### Método Automático (Recomendado)

1. **Abre PowerShell en el directorio del proyecto:**
   ```powershell
   cd "C:\Users\usuario\Clone repo coti inteligente\bmc-cotizacion-inteligente"
   ```

2. **Ejecuta el script de construcción:**
   ```powershell
   .\build_installer.bat
   ```

3. **El script hará todo automáticamente:**
   - Instalará PyInstaller si es necesario
   - Creará el ejecutable
   - Creará el instalador (si Inno Setup está instalado)

4. **Encuentra los archivos generados:**
   - **Ejecutable:** `dist\BMC_Chatbot.exe`
   - **Instalador:** `dist\BMC_Chatbot_Setup.exe`

### Método Manual

#### Paso 1: Crear el Ejecutable

```powershell
# Instalar PyInstaller
pip install pyinstaller

# Crear el ejecutable
pyinstaller chatbot_installer.spec --clean --noconfirm
```

El ejecutable estará en: `dist\BMC_Chatbot.exe`

#### Paso 2: Crear el Instalador (Opcional)

Si tienes Inno Setup instalado:

```powershell
# Opción A: Si Inno Setup está en el PATH
iscc installer.iss

# Opción B: Ruta completa
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

El instalador estará en: `dist\BMC_Chatbot_Setup.exe`

---

## 📁 Estructura de Archivos

```
proyecto/
├── chat_interactivo.py          # Script principal
├── sistema_cotizaciones.py      # Módulo requerido
├── utils_cotizaciones.py        # Módulo requerido
├── chatbot_installer.spec        # Configuración PyInstaller
├── installer.iss                # Script Inno Setup
├── build_installer.bat          # Script automatizado
├── build/                       # Archivos temporales (se crea)
└── dist/                        # Archivos finales (se crea)
    ├── BMC_Chatbot.exe          # Ejecutable standalone
    └── BMC_Chatbot_Setup.exe    # Instalador completo
```

---

## ⚙️ Personalización

### Cambiar el Nombre de la Aplicación

Edita `installer.iss`:
```iss
#define MyAppName "Tu Nombre Aquí"
```

### Agregar un Icono

1. Crea o descarga un archivo `.ico`
2. Colócalo en el directorio del proyecto
3. Edita `chatbot_installer.spec`:
   ```python
   icon='icono.ico',  # Agrega esta línea
   ```
4. Edita `installer.iss`:
   ```iss
   SetupIconFile=icono.ico
   ```

### Incluir Archivos Adicionales

Si necesitas incluir archivos de configuración o datos:

1. Edita `chatbot_installer.spec`:
   ```python
   datas=[
       ('config.json', '.'),
       ('matriz_precios.json', '.'),
   ],
   ```

2. Edita `installer.iss`:
   ```iss
   Source: "config.json"; DestDir: "{app}"; Flags: ignoreversion
   ```

---

## 🧪 Probar el Instalador

### Probar el Ejecutable Directo

1. Ve a `dist\BMC_Chatbot.exe`
2. Haz doble clic para ejecutar
3. Verifica que el chatbot funcione correctamente

### Probar el Instalador

1. Ejecuta `dist\BMC_Chatbot_Setup.exe`
2. Sigue el asistente de instalación
3. Verifica que se instale correctamente
4. Prueba ejecutar el chatbot desde el menú inicio
5. Prueba desinstalar desde Panel de Control

---

## 🐛 Solución de Problemas

### Error: "PyInstaller no encontrado"

```powershell
pip install --upgrade pyinstaller
```

### Error: "Inno Setup no encontrado"

1. Instala Inno Setup desde: https://jrsoftware.org/isdl.php
2. O usa solo el ejecutable `.exe` sin instalador

### El ejecutable es muy grande

PyInstaller incluye Python y todas las dependencias. Esto es normal. El tamaño típico es 50-100 MB.

Para reducir el tamaño:
- Excluye módulos no usados en `chatbot_installer.spec`
- Usa `--onefile` (ya está configurado)

### El ejecutable no funciona en otra PC

Asegúrate de que:
- La PC destino tenga Windows 7 o superior
- No se requiera Python instalado (el ejecutable es standalone)
- Si hay errores, verifica que todas las dependencias estén incluidas

### Error: "ModuleNotFoundError"

Agrega el módulo faltante a `hiddenimports` en `chatbot_installer.spec`:
```python
hiddenimports=[
    'sistema_cotizaciones',
    'utils_cotizaciones',
    'modulo_faltante',  # Agrega aquí
],
```

---

## 📦 Distribución

### Para Distribuir el Ejecutable Simple

1. Copia `dist\BMC_Chatbot.exe`
2. Envíalo por email, USB, o sube a un servidor
3. El usuario solo necesita hacer doble clic

### Para Distribuir el Instalador

1. Copia `dist\BMC_Chatbot_Setup.exe`
2. Distribúyelo como quieras
3. El usuario ejecuta el instalador y sigue las instrucciones

---

## ✅ Checklist de Distribución

- [ ] El ejecutable funciona en tu PC
- [ ] El ejecutable funciona en otra PC (prueba)
- [ ] El instalador funciona correctamente
- [ ] La desinstalación funciona
- [ ] Los accesos directos funcionan
- [ ] El chatbot responde correctamente
- [ ] No hay errores en la consola

---

## 📝 Notas Adicionales

- **Antivirus:** Algunos antivirus pueden marcar ejecutables de PyInstaller como sospechosos. Esto es un falso positivo común. Puedes firmar el ejecutable con un certificado de código para evitarlo.

- **Actualizaciones:** Para actualizar el chatbot, simplemente crea un nuevo instalador con la nueva versión.

- **Licencia:** Asegúrate de incluir cualquier archivo de licencia necesario en el instalador.

---

## 🆘 Soporte

Si tienes problemas:
1. Revisa los mensajes de error en la consola
2. Verifica que todas las dependencias estén instaladas
3. Asegúrate de estar en el directorio correcto
4. Revisa que los archivos fuente existan

---

¡Listo! Ahora tienes un instalador profesional para tu chatbot. 🎉

