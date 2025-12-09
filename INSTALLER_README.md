# Instalador Unificado del Chatbot BMC

## Descripción

`install_chatbot.py` es un ejecutable Python que consolida todas las funcionalidades de instalación, configuración y verificación del chatbot en un solo script.

## Características

- ✅ Verificación completa de requisitos previos
- ✅ Instalación automática de dependencias
- ✅ Configuración interactiva de variables de entorno
- ✅ Verificación completa del sistema
- ✅ Validación de IA obligatoria
- ✅ Checklist completo pre-ejecución
- ✅ Ejecución opcional del chatbot al finalizar

## Uso

### Opción 1: Ejecución directa (recomendado)

```bash
# Hacer ejecutable (solo la primera vez)
chmod +x install_chatbot.py

# Ejecutar
./install_chatbot.py
```

### Opción 2: Con Python

```bash
python3 install_chatbot.py
```

## Proceso de Instalación

El instalador ejecuta 7 fases secuenciales:

1. **Fase 1: Verificación Pre-Instalación**
   - Verifica Python 3.8+
   - Verifica pip disponible
   - Verifica archivos esenciales

2. **Fase 2: Instalación de Dependencias**
   - Lee `requirements.txt`
   - Instala todas las dependencias necesarias

3. **Fase 3: Configuración**
   - Verifica/crea `.env.local`
   - Valida API keys configuradas
   - Verifica base de conocimiento

4. **Fase 4: Verificación Completa del Sistema**
   - Verifica Model Integrator
   - Prueba proveedores de IA (OpenAI, Gemini, Grok, Groq)
   - Verifica integración del bot

5. **Fase 5: Validación de IA Obligatoria**
   - Ejecuta tests de validación
   - Verifica que no haya automatismos
   - Verifica integración de KnowledgeManager y TrainingSystem

6. **Fase 6: Checklist Final**
   - Verifica todos los items críticos
   - Genera resumen completo
   - Determina si el sistema está listo

7. **Fase 7: Ejecución Opcional**
   - Pregunta al usuario si desea ejecutar el chatbot
   - Si sí, ejecuta `chat_interactivo_ai.py`

## Requisitos Mínimos

- Python 3.8 o superior
- pip instalado
- Al menos una API key de IA configurada (OPENAI_API_KEY mínimo)

## Configuración de API Keys

El instalador puede crear un template de `.env.local` si no existe. Las API keys mínimas requeridas:

```env
OPENAI_API_KEY=tu_api_key_aqui
```

API keys opcionales (recomendadas para mejor funcionalidad):

```env
GEMINI_API_KEY=tu_api_key_aqui
XAI_API_KEY=tu_api_key_aqui
GROQ_API_KEY=tu_api_key_aqui
```

## Estados del Checklist

- ✅ **COMPLETO**: Todos los items críticos cumplidos, puede ejecutarse
- ⚠️ **ADVERTENCIA**: Items críticos cumplidos pero faltan recomendados
- ❌ **INCOMPLETO**: Faltan items críticos, NO puede ejecutarse

## Solución de Problemas

### Error: "Python 3.8+ requerido"
- Instala Python 3.8 o superior
- Verifica que `python3` esté en tu PATH

### Error: "requirements.txt no encontrado"
- Asegúrate de ejecutar el script desde el directorio raíz del proyecto

### Error: "OPENAI_API_KEY no configurada"
- Crea `.env.local` en el directorio raíz
- Agrega tu API key de OpenAI
- Vuelve a ejecutar el instalador

### Error: "Validación de IA falló"
- Verifica que `ia_conversacional_integrada.py` esté actualizado
- Verifica que `knowledge_manager.py` y `training_system.py` existan
- Revisa los mensajes de error específicos

## Archivos Relacionados

- `CHECKLIST_INSTALACION.md` - Documentación completa del checklist
- `ejecutor_completo.py` - Ejecutor original (funcionalidades integradas)
- `comprehensive_system_verification.py` - Verificaciones del sistema
- `test_ia_obligatoria.py` - Tests de validación de IA

## Notas

- El instalador no modifica archivos existentes sin confirmación
- Todas las verificaciones son no destructivas
- El instalador puede ejecutarse múltiples veces de forma segura
- Los errores no críticos se reportan como advertencias

