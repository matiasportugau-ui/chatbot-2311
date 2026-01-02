# 🔐 Guía de Configuración de Secretos Locales

## ✅ Sistema de Gestión de Secretos Local

Este sistema te permite guardar todos tus secretos de forma **local, cifrada y segura**.

---

## 🎯 Características

- ✅ **100% Local** - Nada se sube online
- ✅ **Cifrado** - Secretos cifrados con contraseña maestra
- ✅ **Automático** - Se carga automáticamente al iniciar
- ✅ **Seguro** - Nunca se sube a Git
- ✅ **Backup** - Backups automáticos locales

---

## 🚀 Setup Rápido

### Paso 1: Instalar Dependencias

```bash
pip install cryptography
```

### Paso 2: Configurar Secretos

```bash
python setup_secrets.py
```

Este script te guiará para:
- Crear archivo de secretos cifrado
- Ingresar todos tus API keys y secretos
- Configurar contraseña maestra
- Crear backup automático

### Paso 3: Verificar

```bash
python secrets_manager.py list
```

---

## 📁 Ubicación de Archivos

Los secretos se guardan en:
```
~/.bmc-secrets/
├── secrets.encrypted      # Secretos cifrados
├── master.key             # Clave maestra (salt)
└── backup/                # Backups automáticos
    └── secrets_YYYYMMDD_HHMMSS.encrypted
```

**Este directorio está fuera del repositorio Git** ✅

---

## 🔄 Uso Automático

El sistema carga automáticamente los secretos cuando ejecutas:

```bash
python ejecutor_completo.py
```

O cuando importas:
```python
from load_secrets_automatically import load_secrets_automatically
load_secrets_automatically()
```

---

## 📝 Comandos Disponibles

### Crear archivo de secretos
```bash
python secrets_manager.py create
```

### Agregar un secreto
```bash
python secrets_manager.py add --key OPENAI_API_KEY --value sk-...
```

### Obtener un secreto
```bash
python secrets_manager.py get --key OPENAI_API_KEY
```

### Listar secretos
```bash
python secrets_manager.py list
```

### Exportar a .env.local
```bash
python secrets_manager.py export
```

### Crear backup
```bash
python secrets_manager.py backup
```

---

## 🔒 Seguridad

### Nivel de Cifrado
- **Algoritmo:** Fernet (AES 128 en modo CBC)
- **Derivación de clave:** PBKDF2 con 100,000 iteraciones
- **Salt:** Aleatorio, único por instalación

### Permisos
- Archivos: `600` (solo lectura/escritura para el usuario)
- Directorio: `700` (solo acceso para el usuario)

### Mejores Prácticas
1. ✅ **Nunca compartas tu contraseña maestra**
2. ✅ **Haz backups periódicos de ~/.bmc-secrets/**
3. ✅ **Guarda la contraseña maestra en un gestor de contraseñas**
4. ✅ **Rota los secretos periódicamente**
5. ✅ **No subas ~/.bmc-secrets/ a ningún servicio**

---

## 🔄 Flujo de Trabajo

### Primera Vez
1. Ejecutar `python setup_secrets.py`
2. Ingresar todos los secretos
3. Crear contraseña maestra
4. Sistema crea archivo cifrado

### Uso Diario
1. Ejecutar `python ejecutor_completo.py`
2. Sistema carga secretos automáticamente
3. Todo funciona sin intervención

### Actualizar Secretos
```bash
python secrets_manager.py add --key NUEVO_SECRETO --value valor
```

### Backup
```bash
python secrets_manager.py backup
```

---

## 🆚 Comparación con Otros Métodos

| Método | Local | Cifrado | Automático | Seguro |
|--------|-------|---------|------------|--------|
| **Este Sistema** | ✅ | ✅ | ✅ | ✅ |
| .env.local | ✅ | ❌ | ✅ | ⚠️ |
| Variables de entorno | ✅ | ❌ | ⚠️ | ⚠️ |
| Gestores online | ❌ | ✅ | ✅ | ✅ |

---

## ✅ Ventajas

1. **100% Local** - Control total, nada online
2. **Cifrado** - Secretos protegidos
3. **Automático** - Carga sin intervención
4. **Portable** - Puedes mover ~/.bmc-secrets/ entre máquinas
5. **Backup Fácil** - Solo copiar el directorio

---

## 🎯 Recomendación Final

**Para desarrollo local: Este sistema es perfecto**

- ✅ Control total
- ✅ Sin dependencias externas
- ✅ Seguro y cifrado
- ✅ Fácil de usar
- ✅ Nada online

**Para producción:** Usar gestores profesionales (AWS Secrets Manager, etc.)

---

## 📚 Referencias

- Documentación: `SECRETS_MANAGEMENT_BEST_PRACTICES.md`
- Código: `secrets_manager.py`
- Setup: `setup_secrets.py`

