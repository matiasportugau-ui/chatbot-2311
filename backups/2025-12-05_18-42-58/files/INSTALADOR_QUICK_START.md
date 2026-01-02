# 🚀 Inicio Rápido - Crear Instalador

## Opción Rápida: Solo Ejecutable

```powershell
.\crear_ejecutable_simple.bat
```

Esto crea `dist\BMC_Chatbot.exe` que puedes ejecutar directamente.

---

## Opción Completa: Instalador Profesional

### 1. Instalar Inno Setup (una sola vez)
- Descarga: https://jrsoftware.org/isdl.php
- Instala (gratis)

### 2. Crear el instalador
```powershell
.\build_installer.bat
```

Esto crea `dist\BMC_Chatbot_Setup.exe` - un instalador completo.

---

## 📦 Archivos Generados

- **Ejecutable simple:** `dist\BMC_Chatbot.exe` (50-100 MB)
- **Instalador completo:** `dist\BMC_Chatbot_Setup.exe` (si usas Inno Setup)

---

## ✅ Listo para Distribuir

Copia el archivo `.exe` o `.Setup.exe` y envíalo a quien lo necesite.

**No requiere Python instalado** - todo está incluido.

---

Para más detalles, ver: `CREAR_INSTALADOR.md`

