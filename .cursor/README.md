# Configuración por Defecto de Cursor

Este directorio contiene configuraciones por defecto que se cargan automáticamente al abrir Cursor.

## Archivos de Configuración

### `.cursorrules`
Reglas y comportamiento por defecto del proyecto. Define:
- Auto-aprobación siempre habilitada
- Modo de ejecución automático
- Configuración del orchestrator

### `defaults.json`
Valores por defecto en formato JSON:
- Configuración del orchestrator
- Rutas del workspace
- Comportamiento de fases
- Configuración de ejecución

## Valores por Defecto Aplicados

### Orchestrator
- `auto_approve`: `true` (SIEMPRE)
- `require_manual_approval`: `false` (SIEMPRE)
- `execution_mode`: `automated` (SIEMPRE)
- `max_retries`: `3`
- `retry_delay`: `60` segundos

### Ejecución
- Modo: `automated`
- Auto-continuación: `true`
- Rango de fases: `0` a `15`

### Fases
- Auto-aprobación: `true` para todas
- Continuar en error: `true`
- Checkpoint después de cada fase: `true`

## Cómo Funciona

1. Al abrir Cursor, se leen estos archivos
2. Los valores se aplican automáticamente
3. No se requieren configuraciones manuales
4. El sistema siempre usa auto-aprobación

## Modificar Valores

Para cambiar valores por defecto, edita:
- `.cursorrules` - Para reglas de comportamiento
- `.cursor/defaults.json` - Para valores en JSON
- `scripts/orchestrator/config/orchestrator_config.json` - Para configuración del orchestrator

