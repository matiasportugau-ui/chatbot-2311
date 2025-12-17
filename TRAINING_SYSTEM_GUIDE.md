# Sistema de Entrenamiento y Evaluación del ChatBot

## 📋 Resumen Ejecutivo

Este documento describe el sistema completo de entrenamiento y evaluación implementado para el ChatBot BMC Uruguay. El sistema permite mejorar dinámicamente el conocimiento del bot mediante correcciones en tiempo real y evaluar su efectividad mediante benchmarks automatizados.

## 🎯 Problema Resuelto

### Problema Original (Español)
Se necesitaba un sistema de evaluación del ChatBot en estado casi-producción que permita:
- Operar en modo entrenamiento o producción
- Realizar correcciones usando emojis/caracteres especiales
- Reformular respuestas mostrando el razonamiento
- Persistir correcciones en la base de conocimiento
- Permitir refinamiento colaborativo por múltiples agentes
- Evaluar la efectividad mediante benchmarks

### Solución Implementada
Sistema completo de 3 módulos integrados:
1. **Training Evaluation System** - Gestión de modos y correcciones
2. **Benchmark System** - Evaluación y métricas de desempeño
3. **Training Integrated Bot** - Integración con el chatbot existente

## 🏗️ Arquitectura del Sistema

### Componentes Principales

```
┌─────────────────────────────────────────────────────────────┐
│                   Training Integrated Bot                    │
│         (training_integrated_bot.py)                        │
│  - Interfaz unificada para el usuario                       │
│  - Gestión de conversaciones                                │
│  - Coordinación entre módulos                               │
└──────────┬────────────────────────────┬─────────────────────┘
           │                            │
           ▼                            ▼
┌──────────────────────┐    ┌──────────────────────────┐
│  Training System     │    │   Benchmark System       │
│  (training_          │    │   (benchmark_system.py)  │
│   evaluation_        │    │                          │
│   system.py)         │    │  - Test suites           │
│                      │    │  - Performance metrics   │
│  - Modo training/    │    │  - Comparison analysis   │
│    production        │    │  - Reports generation    │
│  - Correcciones      │    │                          │
│  - Reformulación     │    └──────────────────────────┘
│  - Aprobación        │
│  - Knowledge updates │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────────────┐
│    Knowledge Base Storage        │
│    (data/training/)              │
│  - corrections.json              │
│  - knowledge_updates.json        │
│  - training_sessions.json        │
│  - pending_updates.jsonl         │
└──────────────────────────────────┘
```

### Flujo de Datos

```
Usuario → Mensaje → Training Integrated Bot
                         ↓
                    ¿Es corrección?
                    ↙         ↘
                 Sí           No
                 ↓            ↓
         Procesar         Respuesta
         corrección       normal
              ↓
         Reformular
         respuesta
              ↓
         Mostrar nueva
         respuesta + 
         razonamiento
              ↓
         ¿Aprobado?
         ↙       ↘
       Sí        No
       ↓         ↓
   Actualizar  Rechazar
   conocimiento
```

## 📁 Estructura de Archivos

```
chatbot-2311/
├── training_evaluation_system.py    # Sistema principal de entrenamiento
├── benchmark_system.py              # Sistema de benchmarking
├── training_integrated_bot.py       # Bot integrado con entrenamiento
├── data/
│   ├── training/                    # Datos de entrenamiento
│   │   ├── corrections.json         # Correcciones registradas
│   │   ├── knowledge_updates.json   # Actualizaciones de conocimiento
│   │   ├── training_sessions.json   # Sesiones archivadas
│   │   └── pending_updates.jsonl    # Updates pendientes de aplicar
│   └── benchmarks/                  # Datos de benchmarks
│       ├── test_suites.json         # Suites de tests
│       ├── test_results.json        # Resultados de tests
│       └── report_*.json            # Reportes generados
└── docs/
    └── TRAINING_SYSTEM_GUIDE.md     # Esta guía
```

## 🚀 Inicio Rápido

### Instalación

No se requieren dependencias adicionales más allá de las ya existentes en el proyecto:

```bash
# Asegúrate de tener el entorno virtual activado
source .venv/bin/activate  # Linux/Mac
# o
.venv\Scripts\activate  # Windows

# Las dependencias ya están en requirements.txt
pip install -r requirements.txt
```

### Uso Básico - CLI

```bash
python training_integrated_bot.py
```

Comandos disponibles:
- `MODO ENTRENAMIENTO` - Activar modo de entrenamiento
- `MODO PRODUCCIÓN` - Activar modo de producción
- `✏️ [corrección]` - Hacer una corrección
- `APROBAR` - Aprobar respuesta reformulada
- `RECHAZAR [razón]` - Rechazar reformulación
- `ESTADÍSTICAS` - Ver estadísticas de la sesión
- `BENCHMARK` - Ejecutar benchmark
- `REPORTE` - Generar reporte de benchmark
- `SALIR ENTRENAMIENTO` - Finalizar sesión
- `SALIR` - Salir del programa

### Ejemplo de Uso

```
👤 Tú: MODO ENTRENAMIENTO
🤖 Bot: ✅ Modo de entrenamiento activado. Usa ✏️ o 'CORREGIR:' para hacer correcciones.

👤 Tú: ¿Cuánto cuesta el Isodec?
🤖 Bot: Los precios varían según el espesor...

👤 Tú: ✏️ La respuesta debe incluir ejemplos de precios específicos por espesor
🤖 Bot: 
🔄 **Respuesta Reformulada:**
Para el Isodec, los precios varían según el espesor:
- 50mm: $150/m²
- 100mm: $180/m²
- 150mm: $220/m²

💭 **Razonamiento:**
Se agregaron precios específicos por espesor para dar información más concreta...

¿Aprobas esta respuesta?

👤 Tú: APROBAR
🤖 Bot: ✅ Respuesta aprobada y conocimiento actualizado
```

## 🔧 Integración con WhatsApp

### Modificar el Webhook

Para integrar con WhatsApp, modifica `src/app/api/whatsapp/webhook/route.ts`:

```typescript
import { TrainingIntegratedBot } from '@/lib/training-integrated-bot'

const trainingBot = new TrainingIntegratedBot()

async function processMessages(value: any) {
  // ... código existente ...
  
  const response = await trainingBot.processMessage(
    message.from,  // session_id
    message.from,  // user_id
    message.text?.body || ''
  )
  
  await sendWhatsAppMessage(message.from, response)
}
```

### Identificar Agentes de Entrenamiento

Puedes identificar ciertos números de teléfono como agentes de entrenamiento:

```typescript
const TRAINING_AGENTS = [
  '+598XXXXXXXXX',  // Tu número
  '+598YYYYYYYYY',  // Agente 1
]

function isTrainingAgent(phoneNumber: string): boolean {
  return TRAINING_AGENTS.includes(phoneNumber)
}

// Al iniciar conversación
if (isTrainingAgent(message.from)) {
  // Activar modo entrenamiento automáticamente
  await trainingBot.setSessionMode(message.from, 'training')
}
```

## 📊 Sistema de Benchmarking

### Tests Predefinidos

El sistema incluye 5 tests básicos:
1. **Cotización básica Isodec** - Validar generación de cotizaciones
2. **Consulta de productos** - Información sobre productos
3. **Objeción de precio** - Manejo de objeciones
4. **Especificaciones técnicas** - Respuestas técnicas precisas
5. **Datos incompletos** - Validación de datos faltantes

### Agregar Nuevos Tests

```python
from benchmark_system import BenchmarkSystem, BenchmarkTest

benchmark = BenchmarkSystem()

new_test = BenchmarkTest(
    id="test_custom_001",
    name="Mi test personalizado",
    description="Descripción del test",
    input_query="Pregunta de prueba",
    expected_output="palabras, clave, esperadas",
    category="mi_categoria",
    difficulty=3,
    tags=["tag1", "tag2"]
)

benchmark.add_test("mi_suite", new_test)
```

### Ejecutar Benchmarks

```python
# Benchmark antes del entrenamiento
result_before = benchmark.run_benchmark(
    suite_name="default",
    bot_response_func=bot.generate_response,
    mode="before_training"
)

# ... realizar entrenamiento ...

# Benchmark después del entrenamiento
result_after = benchmark.run_benchmark(
    suite_name="default",
    bot_response_func=bot.generate_response,
    mode="after_training"
)

# Comparar resultados
comparison = benchmark.compare_performance(
    result_before["results"],
    result_after["results"]
)
```

### Generar Reportes

```python
# Generar reporte de los últimos 7 días
report = benchmark.generate_report(period_days=7)

# Acceder a métricas
print(f"Score promedio: {report.average_score}")
print(f"Tasa de mejora: {report.improvement_rate}")
print(f"Scores por categoría: {report.category_scores}")
print(f"Recomendaciones: {report.recommendations}")
```

## 🔄 Ciclo de Entrenamiento Recomendado

### Fase 1: Evaluación Inicial (Día 1)
1. Ejecutar benchmark inicial con suite "default"
2. Identificar áreas débiles (scores < 70)
3. Documentar casos de falla

### Fase 2: Entrenamiento Activo (Días 2-5)
1. Activar modo entrenamiento
2. Procesar consultas reales
3. Hacer correcciones cuando sea necesario
4. Aprobar/rechazar reformulaciones
5. Meta: 20-30 correcciones por día

### Fase 3: Evaluación Intermedia (Día 6)
1. Ejecutar benchmark nuevamente
2. Comparar con resultados iniciales
3. Identificar mejoras y áreas pendientes

### Fase 4: Refinamiento (Días 7-10)
1. Enfocarse en categorías con bajo score
2. Agregar tests específicos para casos problemáticos
3. Continuar ciclo de corrección-aprobación

### Fase 5: Evaluación Final (Día 11)
1. Benchmark completo
2. Generar reporte
3. Decidir si pasar a producción

### Criterios de Producción
- ✅ Score promedio ≥ 80
- ✅ Tasa de aprobación ≥ 75%
- ✅ Todas las categorías ≥ 70
- ✅ Desviación estándar < 15

## 📈 Métricas y KPIs

### Métricas de Entrenamiento
- **Correcciones por sesión**: Cantidad de correcciones hechas
- **Tasa de aprobación**: % de reformulaciones aprobadas
- **Tiempo promedio de sesión**: Duración de sesiones de entrenamiento
- **Categorías cubiertas**: Diversidad de temas entrenados

### Métricas de Benchmark
- **Score promedio**: Desempeño general (0-100)
- **Tasa de pass**: % de tests aprobados (threshold: 70)
- **Score por categoría**: Desempeño por tipo de consulta
- **Tasa de mejora**: Cambio en score entre períodos

### Visualización de Progreso

```python
# Exportar métricas para análisis externo
benchmark.export_metrics("metrics_export.json")

# Luego puedes usar herramientas como:
# - Excel/Google Sheets para gráficos
# - Python (matplotlib/seaborn) para visualizaciones
# - Dashboards (Grafana) para monitoreo en tiempo real
```

## 🔐 Seguridad y Permisos

### Control de Acceso a Modo Entrenamiento

```python
# En producción, validar permisos
AUTHORIZED_TRAINERS = [
    "user_admin",
    "agent_001",
    "agent_002"
]

def can_enter_training_mode(user_id: str) -> bool:
    return user_id in AUTHORIZED_TRAINERS

# Al procesar comando de modo
if message == "MODO ENTRENAMIENTO":
    if not can_enter_training_mode(user_id):
        return "❌ No tienes permisos para modo entrenamiento"
    # ... continuar con activación ...
```

### Protección de Datos Sensibles

```python
# No incluir datos sensibles en correcciones
def sanitize_correction(text: str) -> str:
    # Remover números de teléfono
    text = re.sub(r'\d{9,}', '[TELÉFONO]', text)
    # Remover emails
    text = re.sub(r'\S+@\S+', '[EMAIL]', text)
    # Remover direcciones (simplificado)
    text = re.sub(r'\d{1,5}\s+\w+\s+(calle|avenida|av\.)', '[DIRECCIÓN]', text)
    return text
```

## 🐛 Troubleshooting

### Problema: El bot no detecta correcciones
**Solución**: Verificar que la sesión esté en modo entrenamiento:
```python
# Activar explícitamente
response = bot.process_message(session_id, user_id, "MODO ENTRENAMIENTO")
```

### Problema: Las reformulaciones no se guardan
**Solución**: Verificar permisos de escritura en `data/training/`:
```bash
mkdir -p data/training
chmod 755 data/training
```

### Problema: Benchmarks muestran scores bajos
**Solución**: 
1. Revisar tests - pueden ser muy estrictos
2. Ajustar thresholds de scoring
3. Agregar más ejemplos de entrenamiento

### Problema: Integración con bot principal falla
**Solución**: El sistema incluye un mock bot que funciona independientemente. Verificar:
```python
# En training_integrated_bot.py
MAIN_BOT_AVAILABLE = True  # Debe ser True si ia_conversacional_integrada está disponible
```

## 🔄 Actualización del Conocimiento Principal

Las correcciones aprobadas se guardan en `data/training/pending_updates.jsonl`. Para aplicarlas al bot principal:

```python
# Script de aplicación de updates
import json
from pathlib import Path

def apply_pending_updates():
    """Aplicar updates pendientes al conocimiento principal"""
    updates_file = Path("data/training/pending_updates.jsonl")
    
    if not updates_file.exists():
        return
    
    with open(updates_file, 'r', encoding='utf-8') as f:
        for line in f:
            update = json.loads(line)
            
            # Extraer información
            query = update['before_state']['query']
            new_response = update['after_state']['response']
            category = update['category']
            
            # Agregar a base de conocimiento principal
            # (Implementación depende de tu sistema de conocimiento)
            add_to_knowledge_base(query, new_response, category)
    
    # Archivar updates aplicados
    archive_file = updates_file.parent / f"applied_{datetime.now():%Y%m%d}.jsonl"
    updates_file.rename(archive_file)
```

## 📝 Best Practices

### Para Agentes de Entrenamiento

1. **Ser específico en las correcciones**
   - ❌ "Esto está mal"
   - ✅ "La respuesta debe mencionar el precio por m² y el espesor"

2. **Aprobar solo si realmente mejora**
   - No aprobar por aprobar
   - Si no está bien, rechazar con razón clara

3. **Cubrir diferentes categorías**
   - No enfocarse solo en un tipo de consulta
   - Variar entre cotizaciones, información, objeciones, etc.

4. **Documentar patrones**
   - Si notas problemas recurrentes, documentarlos
   - Crear tests específicos para esos casos

### Para Implementación

1. **Monitorear métricas regularmente**
   - Revisar reportes semanales
   - Identificar tendencias

2. **Iterar en los tests**
   - Agregar tests para casos edge encontrados
   - Mantener suite actualizada

3. **Backup regular**
   - Respaldar `data/training/` regularmente
   - Versionar cambios importantes

4. **Validar en staging antes de producción**
   - Nunca aplicar cambios directamente en producción
   - Probar primero en ambiente de staging

## 🎓 Casos de Uso Avanzados

### Entrenamiento Multiagente

```python
# Identificar contribuciones por agente
def get_agent_statistics(user_id: str) -> Dict:
    """Obtener estadísticas de un agente específico"""
    sessions_file = Path("data/training/training_sessions.json")
    
    with open(sessions_file, 'r') as f:
        sessions = json.load(f)
    
    agent_sessions = [s for s in sessions if s['user_id'] == user_id]
    
    return {
        "total_sessions": len(agent_sessions),
        "total_corrections": sum(s['corrections_made'] for s in agent_sessions),
        "total_approved": sum(s['responses_approved'] for s in agent_sessions),
        "avg_approval_rate": statistics.mean([
            s['responses_approved'] / (s['responses_approved'] + s['responses_rejected'])
            for s in agent_sessions
            if s['responses_approved'] + s['responses_rejected'] > 0
        ]) * 100 if agent_sessions else 0
    }
```

### A/B Testing

```python
# Comparar dos versiones del bot
def ab_test(query: str, bot_v1, bot_v2) -> Dict:
    """Comparar respuestas de dos versiones"""
    response_v1 = bot_v1.generate_response(query)
    response_v2 = bot_v2.generate_response(query)
    
    # Evaluar ambas
    score_v1 = evaluate_response(query, response_v1)
    score_v2 = evaluate_response(query, response_v2)
    
    return {
        "query": query,
        "v1": {"response": response_v1, "score": score_v1},
        "v2": {"response": response_v2, "score": score_v2},
        "winner": "v1" if score_v1 > score_v2 else "v2"
    }
```

### Exportación para Análisis Externo

```python
# Exportar todo para análisis en Python/R/Excel
def export_full_analysis():
    """Exportar datos completos para análisis"""
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(f"exports/analysis_{timestamp}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Exportar correcciones
    # Exportar resultados de benchmarks
    # Exportar sesiones
    # Exportar métricas
    
    print(f"Datos exportados a: {output_dir}")
```

## 📚 Referencias

- **Código fuente**: `/training_evaluation_system.py`, `/benchmark_system.py`, `/training_integrated_bot.py`
- **Datos**: `/data/training/`, `/data/benchmarks/`
- **Bot principal**: `/ia_conversacional_integrada.py`
- **Base de conocimiento**: `/base_conocimiento_dinamica.py`

## 🤝 Contribuir

Para agregar funcionalidad al sistema de entrenamiento:

1. Extender las clases base en `training_evaluation_system.py`
2. Agregar nuevos tipos de tests en `benchmark_system.py`
3. Actualizar la integración en `training_integrated_bot.py`
4. Documentar cambios en esta guía

## 📞 Soporte

Para preguntas o problemas:
1. Revisar esta documentación
2. Verificar logs en `data/training/`
3. Ejecutar tests de validación
4. Consultar con el equipo de desarrollo

---

**Versión**: 1.0  
**Última actualización**: Diciembre 2024  
**Autor**: Sistema de Entrenamiento y Evaluación BMC
