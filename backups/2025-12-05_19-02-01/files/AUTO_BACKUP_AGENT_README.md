# Agente de Backup Automático de Workspace

## 📋 Descripción

Agente de IA autónomo que guarda **TODO** el trabajo del workspace cada **15 minutos** de forma automática, sin intervención del usuario. Se activa automáticamente al abrir el workspace y trabaja de forma recurrente y autónoma.

## ✨ Características

- ✅ **Activación Automática**: Se inicia al abrir el workspace
- ✅ **Backup Recurrente**: Guarda todo cada 15 minutos automáticamente
- ✅ **Completamente Autónomo**: No requiere intervención del usuario
- ✅ **Backup Completo**: Guarda todos los archivos, configuraciones y estado
- ✅ **Manejo de Errores**: Continúa funcionando incluso si hay errores
- ✅ **Eficiente**: Usa recursos mínimos
- ✅ **Organizado**: Backups con timestamps y estructura clara

## 🚀 Instalación Rápida

### 1. Configurar el agente

```bash
python setup_auto_backup.py
```

Esto configurará:
- Tareas de VSCode/Cursor para ejecución automática
- Scripts de inicio (Windows y Unix)
- Configuración de launch para debugging

### 2. Ejecutar manualmente (opcional)

```bash
# Windows
start_backup_agent.bat

# Unix/Mac
./start_backup_agent.sh

# O directamente
python auto_backup_agent.py
```

### 3. Activación Automática

El agente se ejecutará automáticamente cuando:
- Abras el workspace en VSCode/Cursor (si configuraste las tareas)
- O ejecutes el script manualmente

## 📁 Estructura de Backups

Los backups se guardan en `./backups/` con esta estructura:

```
backups/
├── 2024-12-05_14-30-00/          # Backup con timestamp
│   ├── files/                     # Todos los archivos del workspace
│   ├── config/                    # Archivos de configuración
│   ├── state/                     # Estado del editor
│   ├── metadata/                  # Metadata del backup
│   │   ├── manifest.json          # Lista completa de archivos
│   │   ├── changes.json           # Cambios detectados
│   │   └── verification.json      # Verificación del backup
│   └── backup_info.txt            # Información del backup
├── index.json                     # Índice de todos los backups
├── latest -> 2024-12-05_14-30-00/ # Enlace al último backup
└── backup_agent.log               # Log del agente
```

## ⚙️ Configuración

### Opciones de Línea de Comandos

```bash
python auto_backup_agent.py --help
```

Opciones disponibles:
- `--workspace PATH`: Especifica la ruta del workspace
- `--backup-dir PATH`: Especifica dónde guardar backups
- `--interval MINUTES`: Cambia el intervalo (por defecto: 15 minutos)

### Ejemplo con opciones personalizadas

```bash
python auto_backup_agent.py \
    --workspace /ruta/al/workspace \
    --backup-dir /ruta/backups \
    --interval 10
```

## 📊 Uso del Agente

### Estado del Agente

El agente muestra información en la consola:
- Workspace siendo respaldado
- Frecuencia de backup
- Archivos respaldados
- Próximo backup programado

### Logs

Los logs se guardan en `backups/backup_agent.log` con información sobre:
- Inicio/detención del agente
- Cada ciclo de backup
- Archivos respaldados
- Errores y advertencias
- Estadísticas de uso

### Verificar Backups

```bash
# Ver índice de backups
cat backups/index.json

# Ver información del último backup
cat backups/latest/backup_info.txt

# Ver manifest del último backup
cat backups/latest/metadata/manifest.json
```

## 🔧 Personalización

### Excluir Archivos/Patrones

Edita `auto_backup_agent.py` y modifica `exclude_patterns`:

```python
self.exclude_patterns = {
    '.git/objects',
    'node_modules',
    '__pycache__',
    # Agrega tus patrones aquí
}
```

### Cambiar Intervalo

```python
# En auto_backup_agent.py
self.backup_interval = 10 * 60  # 10 minutos en lugar de 15
```

O usa la opción de línea de comandos:
```bash
python auto_backup_agent.py --interval 10
```

## 🛠️ Solución de Problemas

### El agente no se inicia automáticamente

1. Verifica que ejecutaste `setup_auto_backup.py`
2. Revisa `.vscode/tasks.json` para ver si la tarea está configurada
3. Ejecuta manualmente: `python auto_backup_agent.py`

### Backups no se están creando

1. Verifica los logs: `cat backups/backup_agent.log`
2. Verifica permisos de escritura en el directorio de backups
3. Verifica que el workspace existe y es accesible

### El agente consume muchos recursos

1. Revisa los patrones de exclusión
2. Aumenta el intervalo de backup
3. Verifica que no hay archivos muy grandes sin excluir

### Archivos no se están respaldando

1. Verifica que no están en `exclude_patterns`
2. Revisa los logs para ver errores específicos
3. Verifica permisos de lectura en los archivos

## 📝 Prompt del Agente

El prompt completo del agente está en:
- `auto_backup_agent_prompt_completo.txt` - Versión completa y detallada
- `auto_backup_agent_prompt.txt` - Versión básica

Estos prompts describen el comportamiento, responsabilidades y lógica del agente.

## 🔄 Restaurar desde Backup

Para restaurar un backup:

```bash
# 1. Identifica el backup a restaurar
ls backups/

# 2. Copia los archivos del backup
cp -r backups/2024-12-05_14-30-00/files/* /ruta/destino/

# O restaura un archivo específico
cp backups/2024-12-05_14-30-00/files/ruta/archivo.py /ruta/original/
```

## 📈 Estadísticas

El agente mantiene estadísticas en `backups/index.json`:
- Lista de todos los backups
- Fecha del último backup
- Información de cada backup (archivos, tamaño, estado)

## 🛡️ Seguridad

- Los backups son **solo lectura** - nunca modifican archivos originales
- Los backups se guardan **localmente** - no se envían a ningún servidor
- Los archivos mantienen sus permisos originales
- Los backups incluyen checksums para verificación

## ⚠️ Notas Importantes

1. **Espacio en Disco**: Los backups ocupan espacio. Considera comprimir backups antiguos periódicamente.

2. **Archivos Grandes**: Archivos muy grandes pueden hacer que el backup tarde más. Considera excluirlos si no son críticos.

3. **Archivos Bloqueados**: Si un archivo está bloqueado, se omitirá en ese ciclo y se intentará en el siguiente.

4. **Detener el Agente**: Presiona `Ctrl+C` para detener el agente de forma segura (hará un backup final).

## 📚 Archivos del Proyecto

- `auto_backup_agent.py` - Implementación del agente
- `auto_backup_agent_prompt_completo.txt` - Prompt completo del agente
- `auto_backup_agent_prompt.txt` - Prompt básico
- `setup_auto_backup.py` - Script de configuración
- `AUTO_BACKUP_AGENT_README.md` - Esta documentación

## 🎯 Casos de Uso

- **Desarrollo de Software**: Backup automático de código en desarrollo
- **Escritura**: Backup de documentos y notas
- **Investigación**: Backup de datos y análisis
- **Cualquier trabajo importante**: Protección contra pérdida de datos

## 💡 Mejores Prácticas

1. **Revisa los logs periódicamente** para asegurar que todo funciona
2. **Limpia backups antiguos** para ahorrar espacio
3. **Verifica backups** ocasionalmente para asegurar que son válidos
4. **Configura exclusiones** apropiadas para tu proyecto
5. **Mantén el agente corriendo** mientras trabajas

---

**¡Tu trabajo está protegido!** 🛡️

El agente trabaja silenciosamente en segundo plano, asegurando que nunca pierdas tu trabajo.

