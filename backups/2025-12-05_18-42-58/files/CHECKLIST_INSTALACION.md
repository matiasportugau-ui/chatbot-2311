# Checklist de Instalación del Chatbot BMC

Este documento define el checklist completo que debe verificarse antes de permitir la ejecución del chatbot.

## Checklist Pre-Ejecución

### 1. Requisitos del Sistema
- [ ] Python 3.8+ instalado y accesible
- [ ] pip disponible y funcional
- [ ] Directorio del proyecto accesible

### 2. Archivos Esenciales
- [ ] `requirements.txt` existe
- [ ] `ia_conversacional_integrada.py` existe
- [ ] `model_integrator.py` existe
- [ ] `conocimiento_consolidado.json` existe (o puede crearse)
- [ ] `AI_AGENTS/EXECUTOR/knowledge_manager.py` existe
- [ ] `AI_AGENTS/EXECUTOR/training_system.py` existe

### 3. Dependencias Python
- [ ] Todas las dependencias de `requirements.txt` instaladas
- [ ] `openai` instalado y funcional
- [ ] `python-dotenv` instalado y funcional
- [ ] `pymongo` instalado (opcional pero recomendado)
- [ ] Dependencias críticas verificadas mediante imports

### 4. Configuración de Variables de Entorno
- [ ] `.env.local` existe o puede crearse
- [ ] `OPENAI_API_KEY` configurada (MÍNIMO REQUERIDO)
- [ ] `GEMINI_API_KEY` configurada (opcional)
- [ ] `XAI_API_KEY` configurada (opcional)
- [ ] `GROQ_API_KEY` configurada (opcional)
- [ ] Variables de entorno cargadas correctamente

### 5. Model Integrator
- [ ] Model Integrator puede inicializarse
- [ ] Al menos un proveedor de IA está habilitado
- [ ] Model Integrator puede listar modelos disponibles

### 6. Proveedores de IA
- [ ] Al menos UN proveedor funciona correctamente:
  - [ ] OpenAI funciona (si OPENAI_API_KEY está configurada)
  - [ ] Gemini funciona (si GEMINI_API_KEY está configurada)
  - [ ] Grok funciona (si XAI_API_KEY está configurada)
  - [ ] Groq funciona (si GROQ_API_KEY está configurada)

### 7. Integración del Bot
- [ ] `IAConversacionalIntegrada` puede inicializarse
- [ ] `use_ai` está habilitado (True)
- [ ] `model_integrator` está inicializado en el bot
- [ ] `knowledge_manager` está inicializado en el bot
- [ ] `training_system` está inicializado en el bot

### 8. Validación de IA Obligatoria
- [ ] No se usa `random.choice` en el código
- [ ] No hay respuestas hardcodeadas de productos
- [ ] Se usa `model_integrator.generate` para todas las respuestas
- [ ] `KnowledgeManager` está integrado correctamente
- [ ] `TrainingSystem` está integrado correctamente
- [ ] Métodos IA requeridos existen:
  - [ ] `_generar_saludo_ia`
  - [ ] `_generar_despedida_ia`
  - [ ] `_obtener_informacion_producto_ia`
  - [ ] `_enriquecer_contexto_completo`
  - [ ] `_construir_system_prompt`
  - [ ] `_procesar_con_ia`

### 9. Base de Conocimiento
- [ ] `conocimiento_consolidado.json` es válido y cargable
- [ ] `KnowledgeManager` puede cargar la base de conocimiento
- [ ] Base de conocimiento contiene información de productos

### 10. Servicios Opcionales
- [ ] MongoDB configurado y accesible (opcional)
- [ ] Docker disponible (opcional, para MongoDB)

## Criterios de Éxito

Para que el checklist se considere **COMPLETO** y se permita la ejecución del chatbot:

1. **CRÍTICO (Debe cumplirse):**
   - Python 3.8+ instalado
   - Todas las dependencias instaladas
   - `.env.local` configurado con al menos `OPENAI_API_KEY`
   - `conocimiento_consolidado.json` existe
   - Model Integrator funcional
   - Al menos un proveedor de IA funciona
   - Bot integrado correctamente con IA habilitada
   - Tests de IA obligatoria pasan (al menos 7/9)

2. **RECOMENDADO (Advertencia si falta):**
   - MongoDB configurado
   - Múltiples proveedores de IA configurados
   - Base de conocimiento completa

## Estados del Checklist

- ✅ **COMPLETO**: Todos los items críticos cumplidos, puede ejecutarse
- ⚠️ **ADVERTENCIA**: Items críticos cumplidos pero faltan recomendados
- ❌ **INCOMPLETO**: Faltan items críticos, NO puede ejecutarse

## Notas

- El instalador debe detener la ejecución si el checklist está INCOMPLETO
- El instalador puede continuar con ADVERTENCIA pero debe informar al usuario
- El instalador debe ofrecer ayuda para completar items faltantes

