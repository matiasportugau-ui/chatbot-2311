# Próximos Pasos - Simulador de Chatbot

## ✅ Lo que ya está implementado

1. **Simulador de Chat** - Sistema completo para testing local
2. **CLI Interactivo** - Interfaz de línea de comandos mejorada
3. **Poblador de Knowledge Base** - Script para poblar MongoDB con escenarios
4. **Test Scenarios** - Escenarios predefinidos para testing
5. **API Server** - Servidor FastAPI con todos los endpoints
6. **Integración OpenAI** - Con fallback a pattern matching
7. **Web UI** - Página simulador en Next.js

## 🚀 Pasos Inmediatos

### Paso 1: Verificar Setup

```bash
cd /Users/matias/Documents/GitHub/Dashboard-bmc/proyecto-cotizacion-whatsapp/05_dashboard_ui
python verify_setup.py
```

Este script verificará:
- Versión de Python
- Paquetes instalados
- Archivos necesarios
- Módulos importables

### Paso 2: Instalar Dependencias (si faltan)

```bash
pip install -r requirements.txt
```

O instalar individualmente:
```bash
pip install fastapi uvicorn pydantic requests pymongo openai python-dotenv
```

### Paso 3: Configurar Variables de Entorno

```bash
# Copiar template
cp env.example .env

# Editar .env y configurar:
# - OPENAI_API_KEY (opcional, para usar OpenAI)
# - MONGODB_URI (opcional, para persistencia)
```

### Paso 4: Iniciar API Server

**Terminal 1:**
```bash
python api_server.py
```

Deberías ver:
```
INFO:     Started server process
INFO:     Waiting for application startup.
✅ OpenAI integration enabled  (si tienes API key)
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Paso 5: Probar el Simulador

**Terminal 2:**
```bash
# Opción 1: CLI Mejorado (recomendado)
python simulate_chat_cli.py

# Opción 2: Simulador Simple
python simulate_chat.py

# Opción 3: Script de inicio rápido
./start_simulator.sh
```

### Paso 6: Tu Primera Conversación

En el simulador, prueba:

```
👤 You: Hola

🤖 Bot: [Respuesta del bot]

👤 You: Quiero cotizar Isodec

🤖 Bot: [Respuesta con información de cotización]

👤 You: 10 metros por 5 metros, 100mm, blanco

🤖 Bot: [Cotización generada]
```

## 📊 Poblar Knowledge Base

Una vez que el sistema funciona, puedes poblar la knowledge base:

```bash
# Poblar con todos los escenarios
python populate_kb.py

# Ver estadísticas
# En el CLI, usa: /stats
```

## 🔄 Flujo de Desarrollo Iterativo

1. **Probar conversación** → Ver respuesta
2. **Revisar calidad** → ¿La respuesta es buena?
3. **Ajustar prompts** → Editar `ia_conversacional_integrada.py`
   - Buscar método `_procesar_con_openai`
   - Modificar el system prompt
4. **Reiniciar API** → Ctrl+C y `python api_server.py` de nuevo
5. **Probar mismo input** → Comparar respuestas
6. **Iterar** → Repetir hasta estar satisfecho

## 🎯 Comandos Útiles del CLI

Cuando uses `simulate_chat_cli.py`:

- `/help` - Ver todos los comandos
- `/new` - Iniciar nueva sesión
- `/phone +59891234567` - Cambiar número de teléfono
- `/history` - Ver historial completo
- `/export` - Exportar conversación a JSON
- `/load conversation.json` - Cargar conversación guardada
- `/stats` - Ver estadísticas de knowledge base
- `/clear` - Limpiar pantalla
- `/exit` - Salir

## 📝 Ejemplos de Testing

### Test 1: Cotización Completa
```
Hola
Quiero cotizar Isodec
10 metros por 5 metros
100mm
Blanco
```

### Test 2: Información de Producto
```
¿Qué es Isodec?
¿Qué espesores tienen?
¿Cuál es el precio?
```

### Test 3: Comparación
```
¿Cuál es la diferencia entre Isodec y Poliestireno?
¿Cuál es mejor para aislamiento térmico?
```

### Test 4: Manejo de Objeciones
```
Quiero cotizar Isodec 10x5 100mm
Es muy caro
¿Hay descuentos?
```

## 🐛 Troubleshooting

### Error: "Cannot connect to API"
**Solución:** Asegúrate de que `api_server.py` esté corriendo en otra terminal

### Error: "Module not found"
**Solución:** 
```bash
pip install -r requirements.txt
```

### Error: "OpenAI API key not found"
**Solución:** 
- El sistema usará pattern matching automáticamente
- O configura `OPENAI_API_KEY` en `.env`

### Error: "MongoDB connection failed"
**Solución:**
- El sistema funcionará sin MongoDB (sin persistencia)
- O inicia MongoDB: `docker-compose up -d mongodb`

## 📚 Archivos Importantes

- `simulate_chat_cli.py` - CLI principal para testing
- `api_server.py` - Servidor API
- `ia_conversacional_integrada.py` - Lógica del chatbot (editar prompts aquí)
- `test_scenarios/` - Escenarios de prueba
- `populate_kb.py` - Poblador de knowledge base

## 🎓 Aprender del Sistema

1. **Revisa las respuestas** - ¿Son naturales? ¿Útiles?
2. **Compara OpenAI vs Pattern Matching** - Prueba con y sin API key
3. **Analiza el conocimiento** - Usa `/stats` para ver qué aprendió
4. **Exporta conversaciones** - Revisa los JSON para análisis
5. **Itera en prompts** - Mejora las respuestas ajustando el system prompt

## ✨ Siguiente Nivel

Una vez que el simulador funciona bien:

1. **Optimizar prompts** - Mejorar respuestas del bot
2. **Agregar más escenarios** - Crear nuevos casos de prueba
3. **Analizar métricas** - Revisar confianza, tipos de respuesta
4. **Poblar knowledge base** - Ejecutar muchos escenarios
5. **Preparar para producción** - Cuando esté listo, configurar WhatsApp real

---

**¿Listo para empezar?** Ejecuta:

```bash
python verify_setup.py
```

Y luego:

```bash
python api_server.py
```

En otra terminal:

```bash
python simulate_chat_cli.py
```

¡A chatear! 💬

