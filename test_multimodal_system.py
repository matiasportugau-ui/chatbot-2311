#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration Tests for Multimodal Training System
=================================================

Tests para validar la integración completa del sistema.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from multimodal_processor import create_multimodal_processor, MultimodalInput
from dynamic_knowledge_layer import DynamicKnowledgeLayer
from human_in_loop_trainer import HumanInTheLoopTrainer, WhatsAppHITLIntegration
from benchmark_system import BenchmarkSystem


def cleanup_test_files(*files):
    """Helper function to cleanup test files"""
    for file in files:
        if file and file.exists():
            try:
                file.unlink()
            except Exception as e:
                print(f"⚠️  Could not delete {file}: {e}")


def test_multimodal_processor():
    """Test del procesador multimodal"""
    print("\n🧪 Test 1: Multimodal Processor")
    print("=" * 50)
    
    processor = create_multimodal_processor()
    
    # Test 1: Procesar texto simple
    text_input = "¿Cuál es el precio del Isodec 100mm?"
    result = processor.process_input(text_input, input_type='text')
    assert result.input_type == 'text'
    assert result.content == text_input
    assert result.confidence == 1.0
    print(f"✅ Texto procesado correctamente")
    
    # Test 2: Detectar tipo automático
    result_auto = processor.process_input(text_input, input_type='auto')
    assert result_auto.input_type == 'text'
    print(f"✅ Detección automática de tipo funcionando")
    
    print(f"\n📊 Resultados:")
    print(f"  - Tipo: {result.input_type}")
    print(f"  - Confianza: {result.confidence}")
    print(f"  - Contenido: {result.content[:50]}...")
    
    return True


def test_dynamic_knowledge_layer():
    """Test del sistema de conocimiento dinámico"""
    print("\n🧪 Test 2: Dynamic Knowledge Layer")
    print("=" * 50)
    
    dkl = DynamicKnowledgeLayer(base_dir=Path("/tmp/test_dkl"))
    
    # Test 1: Agregar corrección
    entry = dkl.add_correction(
        topic="precio_isodec_100mm",
        value="$150 USD/m²",
        corrected_by="agent_001",
        metadata={"region": "Uruguay"}
    )
    assert entry.topic == "precio_isodec_100mm"
    print(f"✅ Corrección agregada: {entry.topic} = {entry.value}")
    
    # Test 2: Obtener valor
    value, confidence = dkl.get_value("precio_isodec_100mm")
    assert value == "$150 USD/m²"
    assert confidence > 0.9
    print(f"✅ Valor recuperado: {value} (confianza: {confidence})")
    
    # Test 3: Detectar conflicto
    entry2 = dkl.add_correction(
        topic="precio_isodec_100mm",
        value="$160 USD/m²",
        corrected_by="agent_002"
    )
    conflicts = dkl.get_unresolved_conflicts()
    assert len(conflicts) > 0
    print(f"✅ Conflicto detectado: {len(conflicts)} conflictos sin resolver")
    
    # Test 4: Estadísticas
    stats = dkl.get_statistics()
    print(f"\n📊 Estadísticas:")
    print(f"  - Total entradas: {stats['total_entries']}")
    print(f"  - Por fuente: {stats['by_source']}")
    print(f"  - Conflictos: {stats['total_conflicts']}")
    
    # Cleanup using helper
    cleanup_test_files(dkl.dynamic_file, dkl.conflicts_file)
    
    return True


def test_human_in_loop_trainer():
    """Test del sistema HITL"""
    print("\n🧪 Test 3: Human-in-the-Loop Trainer")
    print("=" * 50)
    
    # Setup
    dkl = DynamicKnowledgeLayer(base_dir=Path("/tmp/test_hitl"))
    multimodal = create_multimodal_processor()
    hitl = HumanInTheLoopTrainer(dkl, multimodal)
    
    # Test 1: Detectar feedback
    feedback_type = hitl.detect_feedback("❌", message_type='reaction')
    assert feedback_type == 'emoji_rejection'
    print(f"✅ Emoji de rechazo detectado")
    
    # Test 2: Modo aprendizaje
    learning_msg = hitl.enter_learning_mode(
        agent_id="agent_001",
        original_response="El precio es $100",
        rejection_type='emoji_rejection'
    )
    assert "información correcta" in learning_msg.lower()
    print(f"✅ Modo aprendizaje activado")
    
    # Test 3: Procesar corrección
    feedback = hitl.process_correction(
        agent_id="agent_001",
        correction_input="El precio es $150 USD por metro cuadrado",
        input_type='text',
        original_response="El precio es $100"
    )
    assert feedback.agent_id == "agent_001"
    assert feedback.correction is not None
    print(f"✅ Corrección procesada: {feedback.correction[:50]}...")
    
    # Test 4: Doubt Gate
    should_ask = hitl.should_ask_for_validation(0.7)
    assert should_ask == True
    should_not_ask = hitl.should_ask_for_validation(0.9)
    assert should_not_ask == False
    print(f"✅ Doubt Gate funcionando correctamente")
    
    # Test 5: Estadísticas
    stats = hitl.get_learning_statistics()
    print(f"\n📊 Estadísticas de Aprendizaje:")
    print(f"  - Total correcciones: {stats['total_corrections']}")
    print(f"  - Por tipo: {stats['by_type']}")
    print(f"  - Umbral de duda: {stats['doubt_threshold']}")
    
    # Cleanup using helper
    cleanup_test_files(dkl.dynamic_file, dkl.conflicts_file)
    
    return True


def test_whatsapp_integration():
    """Test de integración con WhatsApp"""
    print("\n🧪 Test 4: WhatsApp HITL Integration")
    print("=" * 50)
    
    # Setup
    dkl = DynamicKnowledgeLayer(base_dir=Path("/tmp/test_wa"))
    multimodal = create_multimodal_processor()
    hitl = HumanInTheLoopTrainer(dkl, multimodal)
    wa_integration = WhatsAppHITLIntegration(hitl)
    
    # Test 1: Guardar respuesta
    wa_integration.store_last_response("agent_wa_001", "El precio es $100")
    print(f"✅ Respuesta guardada para agente")
    
    # Test 2: Detectar rechazo
    response = wa_integration.handle_message(
        agent_id="agent_wa_001",
        message="❌",
        message_type='reaction'
    )
    assert response['type'] == 'learning_mode'
    assert response['session_active'] == True
    print(f"✅ Sesión de aprendizaje iniciada")
    
    # Test 3: Procesar corrección en sesión
    response2 = wa_integration.handle_message(
        agent_id="agent_wa_001",
        message="El precio correcto es $150",
        message_type='text'
    )
    assert response2['type'] == 'learning_complete'
    assert response2['session_active'] == False
    print(f"✅ Corrección procesada y sesión cerrada")
    
    print(f"\n📊 Mensaje de confirmación:")
    print(f"  {response2['message']}")
    
    # Cleanup using helper
    cleanup_test_files(dkl.dynamic_file, dkl.conflicts_file)
    
    return True


def test_benchmark_system():
    """Test del sistema de benchmarking"""
    print("\n🧪 Test 5: Benchmark System")
    print("=" * 50)
    
    benchmark = BenchmarkSystem(base_dir=Path("/tmp/test_benchmark"))
    
    # Test 1: Registrar interacciones
    benchmark.record_interaction({'type': 'query', 'success': True})
    benchmark.record_interaction({'type': 'query', 'success': True})
    benchmark.record_interaction({'type': 'query', 'success': False})
    print(f"✅ Interacciones registradas: 3")
    
    # Test 2: Registrar correcciones
    benchmark.record_correction({'agent_id': 'agent_001', 'topic': 'precio'})
    print(f"✅ Corrección registrada")
    
    # Test 3: Registrar búsquedas
    benchmark.record_knowledge_lookup('price_check', found_in_dynamic=True, confidence=0.95)
    benchmark.record_knowledge_lookup('delivery_time', found_in_dynamic=False, confidence=0.80)
    print(f"✅ Búsquedas registradas: 2")
    
    # Test 4: Registrar multimodal
    benchmark.record_multimodal_input('audio', True, 0.9)
    benchmark.record_multimodal_input('image', True, 0.85)
    print(f"✅ Entradas multimodales registradas: 2")
    
    # Test 5: Calcular métricas
    metrics = benchmark.calculate_metrics()
    assert metrics.total_interactions == 3
    assert metrics.total_corrections == 1
    assert metrics.dynamic_knowledge_usage == 1
    assert metrics.static_knowledge_usage == 1
    print(f"✅ Métricas calculadas correctamente")
    
    # Test 6: Guardar benchmark
    benchmark.save_benchmark(metrics)
    print(f"✅ Benchmark guardado")
    
    # Test 7: Generar reporte
    report = benchmark.generate_report()
    assert 'current_metrics' in report
    assert 'trends' in report
    assert 'summary' in report
    print(f"✅ Reporte generado")
    
    print(f"\n📊 Métricas:")
    print(f"  - Interacciones: {metrics.total_interactions}")
    print(f"  - Tasa Aprendizaje: {metrics.learning_rate:.1%}")
    print(f"  - Uso Dinámico/Estático: {metrics.dynamic_knowledge_usage}/{metrics.static_knowledge_usage}")
    print(f"  - Confianza Promedio: {metrics.average_confidence:.1%}")
    
    print(f"\n💡 Insights:")
    for insight in report['summary']['key_insights']:
        print(f"  {insight}")
    
    # Cleanup using helper
    cleanup_test_files(benchmark.metrics_file, benchmark.history_file)
    
    return True


def test_full_integration():
    """Test de integración completa del sistema"""
    print("\n🧪 Test 6: Full System Integration")
    print("=" * 50)
    
    # Setup completo del sistema
    dkl = DynamicKnowledgeLayer(base_dir=Path("/tmp/test_full"))
    multimodal = create_multimodal_processor()
    hitl = HumanInTheLoopTrainer(dkl, multimodal)
    wa = WhatsAppHITLIntegration(hitl)
    benchmark = BenchmarkSystem(base_dir=Path("/tmp/test_full"))
    
    # Simular flujo completo
    print("\n📱 Simulando interacción con agente de ventas...")
    
    # 1. Agente hace consulta
    query = "¿Cuál es el precio del Isodec 100mm?"
    benchmark.record_interaction({'query': query, 'type': 'text'})
    print(f"  1. Consulta: {query}")
    
    # 2. Sistema responde (usando conocimiento estático)
    response = "El precio del Isodec 100mm es $100 USD/m²"
    wa.store_last_response("agent_test", response)
    benchmark.record_knowledge_lookup('price', found_in_dynamic=False, confidence=0.7)
    print(f"  2. Respuesta: {response}")
    
    # 3. Agente rechaza con emoji
    rejection = wa.handle_message("agent_test", "❌", message_type='reaction')
    assert rejection['session_active'] == True
    print(f"  3. Rechazo detectado: {rejection['message'][:50]}...")
    
    # 4. Agente envía corrección
    correction_msg = "No, el precio es $150 USD por metro cuadrado"
    correction_response = wa.handle_message("agent_test", correction_msg, message_type='text')
    assert correction_response['session_active'] == False
    benchmark.record_correction({'agent_id': 'agent_test', 'value': '$150'})
    print(f"  4. Corrección recibida y procesada")
    
    # 5. Verificar que se guardó en conocimiento dinámico
    value, confidence = dkl.get_value("precio")
    if value:
        print(f"  5. Conocimiento actualizado: {value} (confianza: {confidence})")
    
    # 6. Nueva consulta usa conocimiento dinámico
    benchmark.record_knowledge_lookup('price', found_in_dynamic=True, confidence=0.95)
    print(f"  6. Siguiente consulta usará conocimiento dinámico")
    
    # 7. Calcular métricas finales
    metrics = benchmark.calculate_metrics()
    print(f"\n📊 Resultados Finales:")
    print(f"  - Total interacciones: {metrics.total_interactions}")
    print(f"  - Correcciones: {metrics.total_corrections}")
    print(f"  - Tasa de aprendizaje: {metrics.learning_rate:.1%}")
    print(f"  - Uso conocimiento dinámico: {metrics.dynamic_knowledge_usage}")
    print(f"  - Uso conocimiento estático: {metrics.static_knowledge_usage}")
    
    # 8. Generar reporte
    report = benchmark.generate_report()
    print(f"\n💡 Insights del sistema:")
    for insight in report['summary']['key_insights']:
        print(f"  {insight}")
    
    # Cleanup using helper
    cleanup_test_files(dkl.dynamic_file, dkl.conflicts_file, 
                      benchmark.metrics_file, benchmark.history_file)
    
    print(f"\n✅ Integración completa exitosa!")
    return True


def run_all_tests():
    """Ejecuta todos los tests"""
    print("\n" + "=" * 70)
    print("🚀 EJECUTANDO TESTS DEL SISTEMA MULTIMODAL")
    print("=" * 70)
    
    tests = [
        ("Multimodal Processor", test_multimodal_processor),
        ("Dynamic Knowledge Layer", test_dynamic_knowledge_layer),
        ("Human-in-the-Loop Trainer", test_human_in_loop_trainer),
        ("WhatsApp Integration", test_whatsapp_integration),
        ("Benchmark System", test_benchmark_system),
        ("Full Integration", test_full_integration)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            success = test_func()
            results[test_name] = "✅ PASS" if success else "❌ FAIL"
        except Exception as e:
            results[test_name] = f"❌ ERROR: {str(e)}"
            print(f"\n❌ Error en {test_name}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Resumen
    print("\n" + "=" * 70)
    print("📋 RESUMEN DE TESTS")
    print("=" * 70)
    for test_name, result in results.items():
        print(f"  {result} - {test_name}")
    
    passed = sum(1 for r in results.values() if "PASS" in r)
    total = len(results)
    print(f"\n🎯 Resultado: {passed}/{total} tests pasados")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
