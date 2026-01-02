# 🚀 Quick Start Guide - Sistema Multimodal de Entrenamiento

## ⚡ Inicio Rápido en 5 Minutos

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar API Key (Opcional pero Recomendado)

```bash
export OPENAI_API_KEY=sk-your-key-here
```

### 3. Ejecutar Tests

```bash
python3 test_multimodal_system.py
```

Deberías ver: `🎯 Resultado: 6/6 tests pasados`

### 4. Ejemplo Básico de Uso

```python
#!/usr/bin/env python3
from multimodal_processor import create_multimodal_processor
from dynamic_knowledge_layer import DynamicKnowledgeLayer
from human_in_loop_trainer import HumanInTheLoopTrainer, WhatsAppHITLIntegration
from benchmark_system import BenchmarkSystem

# Inicializar sistema
print("Inicializando sistema multimodal...")
multimodal = create_multimodal_processor()
dkl = DynamicKnowledgeLayer()
hitl = HumanInTheLoopTrainer(dkl, multimodal)
wa = WhatsAppHITLIntegration(hitl)
benchmark = BenchmarkSystem()

print("✅ Sistema listo!")

# Simular consulta de agente
agent_id = "agent_test"
query = "¿Cuál es el precio del Isodec 100mm?"

# Procesar consulta
benchmark.record_interaction({'type': 'query', 'agent_id': agent_id})
response = "El precio del Isodec 100mm es $150 USD/m²"
wa.store_last_response(agent_id, response)

print(f"Agente: {query}")
print(f"Bot: {response}")

# Simular rechazo con emoji
rejection = wa.handle_message(agent_id, "❌", message_type='reaction')
print(f"Bot: {rejection['message']}")

# Simular corrección
correction = wa.handle_message(agent_id, "El precio correcto es $160 USD", message_type='text')
print(f"Bot: {correction['message']}")

# Ver estadísticas
metrics = benchmark.calculate_metrics()
print(f"\n📊 Estadísticas:")
print(f"  - Interacciones: {metrics.total_interactions}")
print(f"  - Tasa de Aprendizaje: {metrics.learning_rate:.1%}")

stats = dkl.get_statistics()
print(f"  - Conocimiento dinámico: {stats['total_entries']} entradas")
```

Guarda este código como `quick_start_example.py` y ejecútalo:

```bash
python3 quick_start_example.py
```

## 📚 Casos de Uso Comunes

### Caso 1: Procesar Audio de WhatsApp

```python
from multimodal_processor import create_multimodal_processor

processor = create_multimodal_processor()

# Procesar audio (WhatsApp envía como .ogg o .webm)
result = processor.process_input("mensaje_voz.ogg", input_type='audio')

print(f"Transcripción: {result.content}")
print(f"Confianza: {result.confidence}")
```

### Caso 2: Analizar Foto de Producto

```python
# Cliente envía foto de un producto preguntando qué es
result = processor.process_input("producto.jpg", input_type='image')

print(f"Descripción: {result.content}")
# "Esta es una imagen de un panel de construcción aislante..."
```

### Caso 3: Extraer Info de PDF

```python
# Cliente envía manual técnico en PDF
result = processor.process_input("manual_tecnico.pdf", input_type='document')

print(f"Texto extraído ({len(result.content)} caracteres)")
# Puedes usar este texto para buscar información específica
```

### Caso 4: Corregir Precio Incorrecto

```python
from dynamic_knowledge_layer import DynamicKnowledgeLayer

dkl = DynamicKnowledgeLayer()

# Agente corrige precio
dkl.add_correction(
    topic="precio_isodec_100mm",
    value="$160 USD/m²",
    corrected_by="agent_maria",
    metadata={"region": "Montevideo", "fecha": "2025-12-21"}
)

# Próxima consulta usará el precio correcto
value, confidence = dkl.get_value("precio_isodec_100mm")
print(f"Precio actualizado: {value} (confianza: {confidence})")
```

### Caso 5: Verificar Respuesta de Baja Confianza

```python
from human_in_loop_trainer import HumanInTheLoopTrainer

hitl = HumanInTheLoopTrainer(dkl, multimodal)

# Sistema genera respuesta con baja confianza
original_response = "El tiempo de entrega es aproximadamente 5 días"
confidence = 0.65  # Baja confianza

# Formatear con Doubt Gate
response_with_warning = hitl.format_doubt_gate_response(
    original_response, 
    confidence
)

print(response_with_warning)
# ⚠️ Verificando con mi base de entrenamiento...
# 
# El tiempo de entrega es aproximadamente 5 días
# 
# Por favor, confirma si esta información es correcta...
```

### Caso 6: Ver Métricas del Sistema

```python
from benchmark_system import BenchmarkSystem

benchmark = BenchmarkSystem()

# Ver métricas actuales
metrics = benchmark.calculate_metrics()

print(f"📊 Resumen del Sistema:")
print(f"  Interacciones totales: {metrics.total_interactions}")
print(f"  Correcciones: {metrics.total_corrections}")
print(f"  Tasa de aprendizaje: {metrics.learning_rate:.1%}")
print(f"  Confianza promedio: {metrics.average_confidence:.1%}")
print(f"  Uso conocimiento dinámico: {metrics.dynamic_knowledge_usage}")
print(f"  Uso conocimiento estático: {metrics.static_knowledge_usage}")

# Ver insights
report = benchmark.generate_report()
print("\n💡 Insights:")
for insight in report['summary']['key_insights']:
    print(f"  {insight}")
```

## 🔧 Configuración Avanzada

### Ajustar Umbral de Doubt Gate

```python
from human_in_loop_trainer import HumanInTheLoopTrainer

hitl = HumanInTheLoopTrainer(dkl, multimodal)

# Cambiar umbral (default: 0.8)
hitl.doubt_threshold = 0.85  # Más estricto
# o
hitl.doubt_threshold = 0.7   # Menos estricto
```

### Exportar Datos de Entrenamiento

```python
# Exportar conocimiento dinámico
training_data = dkl.export_for_training('training_export.json')

print(f"Exportadas {training_data['metadata']['total_entries']} entradas")
print(f"Patrones detectados: {len(training_data['patterns'])}")

# Exportar ejemplos few-shot
examples = hitl.export_training_examples('few_shot_examples.json')

print(f"Exportados {len(examples)} ejemplos de entrenamiento")
```

### Generar Reporte Completo

```python
# Generar reporte de benchmarking
report = benchmark.generate_report('benchmark_report.json')

print("📋 Reporte generado:")
print(f"  Archivo: benchmark_report.json")
print(f"  Total benchmarks: {report['summary']['total_benchmarks']}")
print(f"  Tracking desde: {report['summary']['tracking_since']}")
```

## 🐛 Troubleshooting

### Problema: Tests Fallan

```bash
# Verificar que todas las dependencias estén instaladas
pip install -r requirements.txt

# Verificar versión de Python (requiere 3.8+)
python3 --version

# Ejecutar tests con más detalle
python3 test_multimodal_system.py
```

### Problema: Multimodal No Funciona con Audio/Imágenes

**Causa**: Falta OPENAI_API_KEY

**Solución**:
```bash
# Configurar API key
export OPENAI_API_KEY=sk-your-key-here

# O en código
import os
os.environ['OPENAI_API_KEY'] = 'sk-your-key-here'
```

**Nota**: Sin API key, el sistema funciona con procesamiento básico (texto y extracción simple de documentos).

### Problema: Error al Guardar Archivos

**Causa**: Permisos o directorio no existe

**Solución**:
```python
from pathlib import Path

# Asegurar que el directorio existe
Path("./data").mkdir(parents=True, exist_ok=True)

# Usar directorio específico
dkl = DynamicKnowledgeLayer(base_dir=Path("./data"))
```

### Problema: Conflictos No Se Resuelven

```python
# Ver conflictos sin resolver
conflicts = dkl.get_unresolved_conflicts()

for conflict in conflicts:
    print(f"Conflicto ID: {conflict.id}")
    print(f"  Tema: {conflict.topic}")
    print(f"  Valor antiguo: {conflict.old_value}")
    print(f"  Valor nuevo: {conflict.new_value}")
    
    # Resolver manualmente
    dkl.resolve_conflict(conflict.id, resolution='accept_new')
```

## 📖 Próximos Pasos

1. **Lee la documentación completa**: `MULTIMODAL_SYSTEM_DOCS.md`
2. **Explora los tests**: `test_multimodal_system.py`
3. **Revisa los archivos de código fuente**:
   - `multimodal_processor.py`
   - `dynamic_knowledge_layer.py`
   - `human_in_loop_trainer.py`
   - `benchmark_system.py`

## 🆘 Obtener Ayuda

Si tienes problemas:

1. Ejecuta los tests: `python3 test_multimodal_system.py`
2. Revisa los logs del sistema
3. Consulta `MULTIMODAL_SYSTEM_DOCS.md`
4. Verifica configuración de API keys

## 🎯 Checklist de Implementación

- [ ] Dependencias instaladas
- [ ] Tests pasando (6/6)
- [ ] OPENAI_API_KEY configurada (opcional)
- [ ] Ejemplo básico funcionando
- [ ] Integrado con WhatsApp (si aplica)
- [ ] Benchmarking configurado
- [ ] Backups programados

---

**¿Todo listo?** ¡Comienza a usar el sistema multimodal! 🚀

Para más información, consulta: `MULTIMODAL_SYSTEM_DOCS.md`
