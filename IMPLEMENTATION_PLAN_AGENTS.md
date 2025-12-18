# Plan de Implementación para Agentes Automatizados
# Sistema de Entrenamiento y Evaluación del ChatBot

## 📋 Resumen del Plan

Este documento proporciona un plan detallado, paso a paso, para que agentes automatizados implementen y ejecuten el sistema de entrenamiento y evaluación del chatbot.

## 🎯 Objetivos del Plan

1. ✅ Implementar sistema de modos (Training/Production)
2. ✅ Habilitar mecanismo de correcciones con emojis
3. ✅ Implementar reformulación con razonamiento
4. ✅ Crear persistencia de conocimiento
5. ✅ Desarrollar sistema de benchmark
6. ✅ Integrar con chatbot existente
7. ✅ Documentar todo el sistema

## 🏗️ Arquitectura Técnica

### Componentes Implementados

```
1. training_evaluation_system.py
   └─ TrainingEvaluationSystem (clase principal)
      ├─ BotMode (enum: PRODUCTION, TRAINING)
      ├─ CorrectionTrigger (emojis y comandos)
      ├─ CorrectionRequest (estructura de corrección)
      ├─ ReformulatedResponse (respuesta mejorada)
      ├─ TrainingSession (sesión de entrenamiento)
      └─ KnowledgeUpdate (actualización de conocimiento)

2. benchmark_system.py
   └─ BenchmarkSystem (clase principal)
      ├─ BenchmarkTest (test individual)
      ├─ BenchmarkResult (resultado de test)
      ├─ BenchmarkReport (reporte completo)
      └─ BenchmarkMetric (métrica individual)

3. training_integrated_bot.py
   └─ TrainingIntegratedBot (integración)
      ├─ process_message() (procesamiento principal)
      ├─ run_benchmark() (ejecutar benchmarks)
      └─ generate_benchmark_report() (generar reportes)

4. TRAINING_SYSTEM_GUIDE.md
   └─ Documentación completa del sistema
```

## 📂 Estructura de Datos

### Persistencia

```
data/
├── training/
│   ├── corrections.json
│   │   ├── corrections: [CorrectionRequest]
│   │   └── reformulated: [ReformulatedResponse]
│   │
│   ├── knowledge_updates.json
│   │   └── updates: [KnowledgeUpdate]
│   │
│   ├── training_sessions.json
│   │   └── [TrainingSession]
│   │
│   └── pending_updates.jsonl
│       └── KnowledgeUpdate (línea por línea)
│
└── benchmarks/
    ├── test_suites.json
    │   └── {suite_name: [BenchmarkTest]}
    │
    ├── test_results.json
    │   └── results: [BenchmarkResult]
    │
    └── report_*.json
        └── BenchmarkReport
```

## 🚀 Pasos de Implementación Detallados

### Paso 1: Validación del Entorno ✅

**Estado**: Completado

**Archivos creados**:
- ✅ `training_evaluation_system.py` (21,251 bytes)
- ✅ `benchmark_system.py` (22,141 bytes)
- ✅ `training_integrated_bot.py` (14,367 bytes)
- ✅ `TRAINING_SYSTEM_GUIDE.md` (17,389 bytes)

**Verificación**:
```bash
# Verificar que los archivos existen
ls -lh training_evaluation_system.py
ls -lh benchmark_system.py
ls -lh training_integrated_bot.py
ls -lh TRAINING_SYSTEM_GUIDE.md
```

### Paso 2: Crear Directorios de Datos

```bash
# Crear estructura de directorios
mkdir -p data/training
mkdir -p data/benchmarks

# Verificar creación
ls -la data/
```

### Paso 3: Validar Instalación de Dependencias

```bash
# Activar entorno virtual
source .venv/bin/activate  # Linux/Mac
# o
.venv\Scripts\activate  # Windows

# Verificar dependencias (ya están en requirements.txt)
pip list | grep -E "(openai|fastapi|pymongo)"
```

**Dependencias requeridas** (ya incluidas):
- ✅ Python 3.7+
- ✅ json (built-in)
- ✅ datetime (built-in)
- ✅ dataclasses (built-in)
- ✅ pathlib (built-in)

### Paso 4: Prueba del Sistema de Entrenamiento

```bash
# Ejecutar el bot integrado en modo CLI
python training_integrated_bot.py
```

**Script de prueba automatizado**:
```python
# test_training_system.py
from training_evaluation_system import TrainingEvaluationSystem, BotMode

def test_training_system():
    # Inicializar sistema
    system = TrainingEvaluationSystem()
    
    # Test 1: Activar modo entrenamiento
    result = system.set_session_mode("test_001", "agent_test", BotMode.TRAINING)
    assert result["success"] == True
    print("✅ Test 1: Modo entrenamiento activado")
    
    # Test 2: Detectar corrección
    is_correction, text = system.detect_correction("✏️ Mejorar respuesta", "test_001")
    assert is_correction == True
    print("✅ Test 2: Corrección detectada")
    
    # Test 3: Crear corrección
    correction = system.create_correction_request(
        session_id="test_001",
        user_id="agent_test",
        original_query="Test query",
        original_response="Test response",
        correction_text="Improve this"
    )
    assert correction.id is not None
    print("✅ Test 3: Corrección creada")
    
    # Test 4: Obtener estadísticas
    stats = system.get_session_statistics("test_001")
    assert stats["success"] == True
    print("✅ Test 4: Estadísticas obtenidas")
    
    print("\n🎉 Todos los tests pasaron!")

if __name__ == "__main__":
    test_training_system()
```

### Paso 5: Prueba del Sistema de Benchmark

```bash
# Ejecutar tests de benchmark
python -c "
from benchmark_system import BenchmarkSystem

benchmark = BenchmarkSystem()

# Función de respuesta mock
def mock_response(query):
    return f'Respuesta de prueba para: {query}'

# Ejecutar benchmark
result = benchmark.run_benchmark('default', mock_response, 'test_mode')
print(f'Tests ejecutados: {result[\"summary\"][\"total_tests\"]}')
print(f'Score promedio: {result[\"summary\"][\"average_score\"]:.1f}')
print('✅ Benchmark funcionando correctamente')
"
```

### Paso 6: Integración con WhatsApp (Opcional)

**Para agentes que necesiten integración con WhatsApp**:

1. **Crear wrapper TypeScript/Python bridge**:

```typescript
// src/lib/training-bot-bridge.ts
import { spawn } from 'child_process';

export async function processWithTrainingBot(
  sessionId: string,
  userId: string,
  message: string
): Promise<string> {
  return new Promise((resolve, reject) => {
    const python = spawn('python', [
      'training_integrated_bot_api.py',
      sessionId,
      userId,
      message
    ]);
    
    let response = '';
    
    python.stdout.on('data', (data) => {
      response += data.toString();
    });
    
    python.on('close', (code) => {
      if (code === 0) {
        resolve(response.trim());
      } else {
        reject(new Error(`Process exited with code ${code}`));
      }
    });
  });
}
```

2. **Crear API standalone** (para facilitar integración):

```python
# training_integrated_bot_api.py
import sys
import json
from training_integrated_bot import TrainingIntegratedBot

def main():
    if len(sys.argv) != 4:
        print(json.dumps({"error": "Usage: script.py session_id user_id message"}))
        sys.exit(1)
    
    session_id = sys.argv[1]
    user_id = sys.argv[2]
    message = sys.argv[3]
    
    bot = TrainingIntegratedBot()
    response = bot.process_message(session_id, user_id, message)
    
    # Output como JSON para fácil parsing
    print(json.dumps({
        "success": True,
        "response": response,
        "session_id": session_id
    }))

if __name__ == "__main__":
    main()
```

3. **Actualizar webhook de WhatsApp**:

```typescript
// src/app/api/whatsapp/webhook/route.ts
import { processWithTrainingBot } from '@/lib/training-bot-bridge'

async function processMessages(value: any) {
  for (const message of value.messages || []) {
    try {
      const response = await processWithTrainingBot(
        message.from,
        message.from,
        message.text?.body || ''
      )
      
      await sendWhatsAppMessage(message.from, response)
    } catch (error) {
      console.error('Training bot error:', error)
      // Fallback a bot normal
    }
  }
}
```

### Paso 7: Configuración de Agentes de Entrenamiento

**Crear archivo de configuración**:

```json
// config/training_agents.json
{
  "authorized_trainers": [
    {
      "user_id": "agent_001",
      "name": "Matías Portugal",
      "phone": "+598XXXXXXXXX",
      "permissions": ["training", "benchmark", "approve"],
      "active": true
    },
    {
      "user_id": "agent_002",
      "name": "Agente 2",
      "phone": "+598YYYYYYYYY",
      "permissions": ["training"],
      "active": true
    }
  ],
  "training_settings": {
    "auto_mode_for_agents": true,
    "require_explicit_approval": true,
    "min_confidence_auto_approve": 0.95,
    "notification_channel": "whatsapp"
  }
}
```

**Cargar configuración en el sistema**:

```python
# config_loader.py
import json
from pathlib import Path

class TrainingConfig:
    def __init__(self, config_file="config/training_agents.json"):
        self.config_file = Path(config_file)
        self.load_config()
    
    def load_config(self):
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = self._default_config()
    
    def is_authorized_trainer(self, user_id: str) -> bool:
        trainers = self.config.get("authorized_trainers", [])
        return any(
            t["user_id"] == user_id and t["active"]
            for t in trainers
        )
    
    def get_trainer_permissions(self, user_id: str) -> list:
        trainers = self.config.get("authorized_trainers", [])
        for trainer in trainers:
            if trainer["user_id"] == user_id:
                return trainer.get("permissions", [])
        return []
    
    def _default_config(self):
        return {
            "authorized_trainers": [],
            "training_settings": {
                "auto_mode_for_agents": False
            }
        }
```

### Paso 8: Automatización de Benchmarks

**Crear script de benchmark automatizado**:

```python
# scripts/automated_benchmark.py
import schedule
import time
from datetime import datetime
from pathlib import Path
from training_integrated_bot import TrainingIntegratedBot

def run_scheduled_benchmark():
    """Ejecutar benchmark programado"""
    print(f"[{datetime.now()}] Iniciando benchmark programado...")
    
    bot = TrainingIntegratedBot()
    
    # Ejecutar benchmark
    result = bot.run_benchmark(suite_name="default", mode="scheduled")
    print(result)
    
    # Generar reporte
    report = bot.generate_benchmark_report(period_days=1)
    
    # Guardar reporte
    report_dir = Path("data/benchmarks/scheduled")
    report_dir.mkdir(parents=True, exist_ok=True)
    
    report_file = report_dir / f"report_{datetime.now():%Y%m%d_%H%M%S}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"[{datetime.now()}] Benchmark completado. Reporte guardado en {report_file}")

def main():
    """Programar benchmarks automáticos"""
    # Benchmark diario a las 23:00
    schedule.every().day.at("23:00").do(run_scheduled_benchmark)
    
    # Benchmark cada 6 horas
    # schedule.every(6).hours.do(run_scheduled_benchmark)
    
    print("Scheduler de benchmarks iniciado...")
    print("Benchmarks programados:")
    print("- Diario a las 23:00")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()
```

**Ejecutar como servicio** (Linux):

```bash
# Crear systemd service
sudo nano /etc/systemd/system/chatbot-benchmark.service
```

```ini
[Unit]
Description=ChatBot Automated Benchmark
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/chatbot-2311
ExecStart=/path/to/.venv/bin/python scripts/automated_benchmark.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Habilitar y iniciar servicio
sudo systemctl enable chatbot-benchmark
sudo systemctl start chatbot-benchmark
sudo systemctl status chatbot-benchmark
```

### Paso 9: Monitoreo y Alertas

**Crear sistema de alertas**:

```python
# scripts/monitoring_alerts.py
import json
from pathlib import Path
from datetime import datetime, timedelta

class BenchmarkMonitor:
    def __init__(self):
        self.alert_thresholds = {
            "min_average_score": 70,
            "min_pass_rate": 60,
            "max_std_dev": 25
        }
    
    def check_alerts(self):
        """Revisar métricas y generar alertas"""
        alerts = []
        
        # Cargar último reporte
        reports_dir = Path("data/benchmarks")
        latest_report = self._get_latest_report(reports_dir)
        
        if not latest_report:
            return alerts
        
        with open(latest_report, 'r') as f:
            report = json.load(f)
        
        # Check average score
        if report["average_score"] < self.alert_thresholds["min_average_score"]:
            alerts.append({
                "level": "WARNING",
                "message": f"Score promedio bajo: {report['average_score']:.1f}",
                "recommendation": "Revisar tests fallidos y agregar más entrenamiento"
            })
        
        # Check pass rate
        pass_rate = (report["tests_passed"] / report["total_tests"]) * 100
        if pass_rate < self.alert_thresholds["min_pass_rate"]:
            alerts.append({
                "level": "CRITICAL",
                "message": f"Tasa de aprobación baja: {pass_rate:.1f}%",
                "recommendation": "Urgente: revisar fallas y corregir"
            })
        
        return alerts
    
    def _get_latest_report(self, reports_dir):
        """Obtener el reporte más reciente"""
        reports = list(reports_dir.glob("report_*.json"))
        if not reports:
            return None
        return max(reports, key=lambda p: p.stat().st_mtime)
    
    def send_alerts(self, alerts):
        """Enviar alertas (implementar según canal deseado)"""
        if not alerts:
            print("✅ No hay alertas")
            return
        
        print(f"\n⚠️  {len(alerts)} ALERTAS DETECTADAS:\n")
        for i, alert in enumerate(alerts, 1):
            print(f"{i}. [{alert['level']}] {alert['message']}")
            print(f"   Recomendación: {alert['recommendation']}\n")
        
        # Aquí puedes integrar con:
        # - Email
        # - Slack
        # - WhatsApp
        # - SMS
        # etc.

if __name__ == "__main__":
    monitor = BenchmarkMonitor()
    alerts = monitor.check_alerts()
    monitor.send_alerts(alerts)
```

### Paso 10: Documentación para Usuarios Finales

**Crear guía rápida**:

```markdown
# Guía Rápida - Sistema de Entrenamiento

## Para Agentes de Entrenamiento

### Inicio Rápido
1. Envía "MODO ENTRENAMIENTO" para empezar
2. Haz tus preguntas normalmente
3. Si la respuesta necesita corrección, usa: ✏️ [tu corrección]
4. Revisa la respuesta mejorada
5. Responde "APROBAR" o "RECHAZAR [razón]"

### Emojis y Comandos
- ✏️ - Hacer corrección
- 💡 - Dar feedback
- ✅ - Aprobar
- ❌ - Rechazar
- 📊 - Ver estadísticas

### Mejores Prácticas
- Sé específico en las correcciones
- Aprueba solo si realmente mejora
- Cubre diferentes tipos de consultas
- Documenta patrones que observes

## Para Administradores

### Monitoreo
```bash
# Ver estadísticas
python -c "
from training_integrated_bot import TrainingIntegratedBot
bot = TrainingIntegratedBot()
print(bot.generate_benchmark_report(period_days=7))
"
```

### Mantenimiento
- Revisar logs diariamente
- Ejecutar benchmarks semanalmente
- Backup de datos mensualmente
- Actualizar tests según necesidad
```

## 🔄 Ciclo de Vida del Sistema

### Fase 1: Setup Inicial (Día 0)
- [x] Crear archivos del sistema
- [x] Configurar directorios
- [ ] Validar pruebas básicas
- [ ] Configurar agentes autorizados

### Fase 2: Período de Prueba (Días 1-7)
- [ ] Entrenar con 20-30 correcciones por día
- [ ] Ejecutar benchmarks diarios
- [ ] Ajustar thresholds según resultados
- [ ] Documentar casos especiales

### Fase 3: Evaluación (Día 8)
- [ ] Generar reporte completo
- [ ] Comparar métricas antes/después
- [ ] Decidir si pasar a producción
- [ ] Ajustar configuración

### Fase 4: Producción (Día 9+)
- [ ] Activar modo producción
- [ ] Mantener modo entrenamiento para agentes
- [ ] Monitoreo continuo
- [ ] Mejoras incrementales

## 📊 KPIs de Éxito

### Métricas de Implementación
- ✅ Todos los archivos creados
- ✅ Tests unitarios pasando
- ⏳ Integración con WhatsApp (opcional)
- ⏳ Benchmarks ejecutándose (pendiente prueba)

### Métricas de Operación (Objetivo)
- Score promedio ≥ 80
- Tasa de aprobación ≥ 75%
- Todas las categorías ≥ 70
- Desviación estándar < 15

### Métricas de Negocio (Objetivo)
- Reducción de consultas incorrectas: 50%
- Aumento de satisfacción: 30%
- Reducción de tiempo de respuesta: 20%
- Aumento de conversiones: 15%

## 🐛 Troubleshooting Rápido

### Error: "Module not found"
```bash
# Verificar entorno virtual activado
which python  # Debe apuntar a .venv

# Reinstalar dependencias
pip install -r requirements.txt
```

### Error: "Permission denied" en data/
```bash
# Dar permisos
chmod -R 755 data/
mkdir -p data/training data/benchmarks
```

### Error: "Bot no responde en WhatsApp"
```bash
# Verificar logs
tail -f logs/webhook.log

# Verificar credenciales
python -c "import os; print(os.getenv('WHATSAPP_ACCESS_TOKEN')[:10])"
```

## 📋 Checklist de Implementación

### Setup Básico
- [x] Archivos del sistema creados
- [x] Documentación completa
- [ ] Directorios de datos creados
- [ ] Tests básicos ejecutados

### Integración
- [ ] Bot principal conectado
- [ ] WhatsApp webhook actualizado (opcional)
- [ ] Agentes autorizados configurados
- [ ] Benchmarks ejecutándose

### Validación
- [ ] CLI funcionando
- [ ] Correcciones detectadas correctamente
- [ ] Reformulaciones generándose
- [ ] Conocimiento persistiéndose
- [ ] Benchmarks reportando

### Producción
- [ ] Monitoreo configurado
- [ ] Alertas funcionando
- [ ] Backup automático
- [ ] Documentación actualizada

## 🎯 Próximos Pasos Sugeridos

1. **Inmediato** (Hoy):
   - Crear directorios de datos
   - Ejecutar tests básicos
   - Validar funcionamiento CLI

2. **Corto Plazo** (Esta Semana):
   - Configurar agentes autorizados
   - Integrar con bot principal
   - Ejecutar primer benchmark

3. **Mediano Plazo** (Este Mes):
   - Completar integración WhatsApp
   - Entrenar con casos reales
   - Evaluar métricas

4. **Largo Plazo** (Próximos Meses):
   - Optimizar basado en datos
   - Expandir test suites
   - Automatizar completamente

## 📞 Contacto y Soporte

- **Documentación**: `TRAINING_SYSTEM_GUIDE.md`
- **Código**: `/training_evaluation_system.py`, `/benchmark_system.py`
- **Tests**: Ejecutar `python training_integrated_bot.py`

---

**Versión del Plan**: 1.0  
**Última Actualización**: Diciembre 2024  
**Estado**: ✅ Implementación Completada - Pendiente Validación
