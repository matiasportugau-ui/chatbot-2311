# Quick Reference - Sistema de Entrenamiento

## 🚀 Inicio Rápido

```bash
# Activar entorno
source .venv/bin/activate

# Iniciar bot de entrenamiento
python training_integrated_bot.py

# Ejecutar tests
python test_training_system.py
```

## 📱 Comandos de Chat

| Comando | Descripción |
|---------|-------------|
| `MODO ENTRENAMIENTO` | Activar modo de entrenamiento |
| `MODO PRODUCCIÓN` | Activar modo de producción |
| `✏️ [corrección]` | Hacer una corrección |
| `🔧 [corrección]` | Hacer una corrección (alternativo) |
| `CORREGIR: [texto]` | Hacer una corrección (texto) |
| `💡 [feedback]` | Dar feedback/sugerencia |
| `APROBAR` o `✅` | Aprobar respuesta reformulada |
| `RECHAZAR [razón]` | Rechazar reformulación |
| `ESTADÍSTICAS` o `📊` | Ver estadísticas de sesión |
| `BENCHMARK` | Ejecutar benchmark |
| `REPORTE` | Generar reporte |
| `SALIR ENTRENAMIENTO` | Finalizar sesión |
| `SALIR` | Salir del programa |

## 🎯 Flujo de Trabajo

### 1. Iniciar Sesión
```
Tú: MODO ENTRENAMIENTO
Bot: ✅ Modo de entrenamiento activado...
```

### 2. Probar Bot
```
Tú: ¿Cuánto cuesta el Isodec?
Bot: [Respuesta del bot]
```

### 3. Hacer Corrección
```
Tú: ✏️ Incluir precios específicos por espesor
Bot: 🔄 Respuesta Reformulada:
     [Nueva respuesta]
     💭 Razonamiento: ...
     📝 Cambios: ...
```

### 4. Aprobar/Rechazar
```
Tú: APROBAR
Bot: ✅ Respuesta aprobada y conocimiento actualizado

# O
Tú: RECHAZAR La respuesta sigue sin ser clara
Bot: ❌ Respuesta rechazada...
```

### 5. Ver Progreso
```
Tú: ESTADÍSTICAS
Bot: 📊 Estadísticas:
     - Correcciones: 15
     - Aprobadas: 12
     - Tasa: 80%
```

### 6. Finalizar
```
Tú: SALIR ENTRENAMIENTO
Bot: ✅ Sesión finalizada
     📊 Estadísticas finales...
```

## 📊 Tipos de Correcciones

### Corrección de Contenido
```
✏️ La respuesta debe mencionar que ofrecemos instalación
```

### Corrección de Tono
```
✏️ Usar un tono más formal y profesional
```

### Agregar Información
```
✏️ Incluir ejemplos de casos de uso reales
```

### Corrección de Estructura
```
✏️ Organizar en puntos numerados para mayor claridad
```

## 🧪 Testing

### Validación Completa
```bash
python test_training_system.py
```

### Test Específico
```python
from training_evaluation_system import TrainingEvaluationSystem, BotMode

system = TrainingEvaluationSystem()
result = system.set_session_mode("test", "agent", BotMode.TRAINING)
print(result)
```

## 📈 Benchmarking

### Ejecutar Benchmark
```python
from training_integrated_bot import TrainingIntegratedBot

bot = TrainingIntegratedBot()
result = bot.run_benchmark()
print(result)
```

### Generar Reporte
```python
report = bot.generate_benchmark_report(period_days=7)
print(report)
```

## 📁 Archivos Importantes

```
training_evaluation_system.py  → Sistema principal
benchmark_system.py            → Benchmarks
training_integrated_bot.py     → Bot integrado
data/training/                 → Datos de entrenamiento
data/benchmarks/               → Datos de benchmarks
```

## 🔧 Programático

### Uso en Python
```python
from training_integrated_bot import TrainingIntegratedBot

# Crear bot
bot = TrainingIntegratedBot()

# Procesar mensaje
response = bot.process_message(
    session_id="sesion_001",
    user_id="agente_001",
    message="Hola"
)

print(response)
```

### Activar Modo Programáticamente
```python
from training_evaluation_system import TrainingEvaluationSystem, BotMode

system = TrainingEvaluationSystem()
result = system.set_session_mode(
    session_id="sesion_001",
    user_id="agente_001",
    mode=BotMode.TRAINING
)
```

### Crear Corrección Programáticamente
```python
correction = system.create_correction_request(
    session_id="sesion_001",
    user_id="agente_001",
    original_query="¿Precio de Isodec?",
    original_response="Varía según espesor",
    correction_text="Incluir precios específicos"
)
```

## 📊 Métricas Clave

| Métrica | Objetivo | Crítico |
|---------|----------|---------|
| Score Promedio | ≥ 80 | < 60 |
| Tasa Aprobación | ≥ 75% | < 50% |
| Categorías | Todas ≥ 70 | Alguna < 50 |
| Std Dev | < 15 | > 25 |

## 🐛 Solución Rápida de Problemas

### Bot no detecta corrección
✅ Verificar que estés en modo entrenamiento
```
Tú: MODO ENTRENAMIENTO
```

### Tests fallan
✅ Verificar permisos de datos
```bash
mkdir -p data/training data/benchmarks
chmod -R 755 data/
```

### Import error
✅ Verificar entorno virtual activado
```bash
which python  # Debe apuntar a .venv
source .venv/bin/activate
```

### Bot responde lento
✅ Bot principal puede no estar disponible, usa mock
```python
MAIN_BOT_AVAILABLE = False  # En training_integrated_bot.py
```

## 📚 Documentación Completa

- **TRAINING_SYSTEM_GUIDE.md** - Guía completa
- **IMPLEMENTATION_PLAN_AGENTS.md** - Plan de implementación
- **EXECUTIVE_SUMMARY_TRAINING_SYSTEM.md** - Resumen ejecutivo

## 💡 Tips

1. **Sé específico** en las correcciones
2. **Prueba antes de aprobar** - Lee la reformulación completa
3. **Varía las categorías** - No solo cotizaciones
4. **Usa estadísticas** - Monitorea tu progreso
5. **Haz benchmark** regularmente - Mide el impacto

## 🎯 Objetivos por Sesión

- **Correcciones**: 20-30 por día
- **Aprobación**: > 75%
- **Categorías**: Mínimo 3 diferentes
- **Duración**: 2-4 horas efectivas

## ⚡ Atajos CLI

```bash
# Alias útiles (agregar a .bashrc o .zshrc)
alias train="cd /path/to/chatbot && source .venv/bin/activate && python training_integrated_bot.py"
alias test-train="cd /path/to/chatbot && python test_training_system.py"
alias benchmark="cd /path/to/chatbot && python -c 'from training_integrated_bot import TrainingIntegratedBot; bot = TrainingIntegratedBot(); print(bot.run_benchmark())'"
```

## 🌐 Integración WhatsApp (Opcional)

### Actualizar Webhook
```typescript
// src/app/api/whatsapp/webhook/route.ts
import { TrainingIntegratedBot } from '@/lib/training-bot'

const bot = new TrainingIntegratedBot()
const response = await bot.processMessage(from, from, message)
await sendWhatsAppMessage(from, response)
```

### Identificar Agentes
```json
// config/training_agents.json
{
  "authorized_trainers": [
    {
      "user_id": "agent_001",
      "phone": "+598XXXXXXXXX",
      "permissions": ["training", "benchmark"]
    }
  ]
}
```

---

**Versión**: 1.0  
**Última Actualización**: Diciembre 2024  
**Para más detalles**: Ver `TRAINING_SYSTEM_GUIDE.md`
