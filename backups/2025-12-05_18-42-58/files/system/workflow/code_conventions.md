# Convenciones de Código - Sistema de Trabajo Base

## Estándares Generales

### Python

- **Indentación:** 4 espacios
- **Línea máxima:** 100 caracteres
- **Encoding:** UTF-8
- **Naming:**
  - Funciones y variables: `snake_case`
  - Clases: `PascalCase`
  - Constantes: `UPPER_SNAKE_CASE`
  - Privados: `_leading_underscore`

### Estructura de Archivos

```
module_name.py
├── Imports (standard library, third-party, local)
├── Constantes
├── Clases
├── Funciones
└── if __name__ == "__main__"
```

### Documentación

- Docstrings en formato Google style
- Comentarios en español para lógica de negocio
- Nombres de variables descriptivos

### Manejo de Errores

- Usar excepciones específicas
- Logging de errores con contexto
- No silenciar errores sin razón

### Testing

- Tests unitarios para funciones críticas
- Tests de integración para flujos completos
- Fixtures reutilizables

## Convenciones Específicas del Sistema

### Agentes

- Cada agente en su propio módulo
- Comunicación vía eventos o API
- Estado persistente en JSON/DB

### Scripts

- Ejecutables con `#!/usr/bin/env python3`
- Argumentos vía argparse
- Outputs en formato JSON cuando sea posible

### Configuración

- Variables de entorno para secrets
- Archivos de config en JSON/YAML
- Validación de configuración al inicio

### Logging

- Niveles: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Formato estructurado (JSON)
- Rotación de logs automática

