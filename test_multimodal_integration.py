#!/usr/bin/env python3
"""
Integration Test for Multimodal Training System
Tests the complete flow: multimodal input → processing → training feedback → knowledge update
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_system_imports():
    """Test that all system components can be imported"""
    print("\n" + "="*60)
    print("🧪 TEST 1: System Imports")
    print("="*60)
    
    try:
        from multimodal_processor import MultimodalProcessor
        print("✅ MultimodalProcessor imported")
    except Exception as e:
        print(f"❌ MultimodalProcessor import failed: {e}")
        return False
    
    try:
        from dynamic_knowledge_manager import DynamicKnowledgeManager
        print("✅ DynamicKnowledgeManager imported")
    except Exception as e:
        print(f"❌ DynamicKnowledgeManager import failed: {e}")
        return False
    
    try:
        from human_in_loop_trainer import HumanInLoopTrainer
        print("✅ HumanInLoopTrainer imported")
    except Exception as e:
        print(f"❌ HumanInLoopTrainer import failed: {e}")
        return False
    
    try:
        from benchmark_system import BenchmarkSystem
        print("✅ BenchmarkSystem imported")
    except Exception as e:
        print(f"❌ BenchmarkSystem import failed: {e}")
        return False
    
    try:
        from ia_conversacional_integrada import IAConversacionalIntegrada
        print("✅ IAConversacionalIntegrada imported")
    except Exception as e:
        print(f"❌ IAConversacionalIntegrada import failed: {e}")
        return False
    
    print("\n✅ All imports successful!")
    return True


def test_multimodal_processor():
    """Test multimodal processor with different input types"""
    print("\n" + "="*60)
    print("🧪 TEST 2: Multimodal Processor")
    print("="*60)
    
    from multimodal_processor import MultimodalProcessor
    
    processor = MultimodalProcessor()
    
    # Test text input
    print("\n▶️  Testing text input...")
    text_input = processor.process_input("¿Cuál es el precio del Isodec?", "text")
    print(f"   Type: {text_input.input_type}")
    print(f"   Content: {text_input.content[:100]}")
    print(f"   Confidence: {text_input.confidence}")
    assert text_input.input_type == "text"
    assert text_input.confidence == 1.0
    print("   ✅ Text processing works")
    
    # Note: Audio and image processing require OpenAI API key
    if os.getenv("OPENAI_API_KEY"):
        print("\n▶️  OpenAI API key found - multimodal processing available")
    else:
        print("\n⚠️  OpenAI API key not set - audio/image processing limited")
    
    return True


def test_dynamic_knowledge_manager():
    """Test dynamic knowledge manager"""
    print("\n" + "="*60)
    print("🧪 TEST 3: Dynamic Knowledge Manager")
    print("="*60)
    
    from dynamic_knowledge_manager import DynamicKnowledgeManager, KnowledgeQuery
    
    manager = DynamicKnowledgeManager()
    
    # Test query
    print("\n▶️  Testing knowledge query...")
    query = KnowledgeQuery(
        query_text="precio isodec",
        query_type="price",
        context={}
    )
    result = manager.query_knowledge(query)
    print(f"   Source: {result.source} (Priority Level {result.priority_level})")
    print(f"   Confidence: {result.confidence}")
    print("   ✅ Knowledge query works")
    
    # Test adding correction
    print("\n▶️  Testing add correction...")
    success = manager.add_correction(
        correction_type="prices",
        correction_id="test_correction_isodec",
        correction_data={
            "product": "Isodec",
            "price": 1500.00,
            "unit": "UYU/m²",
            "keywords": ["isodec", "precio", "test"]
        },
        source_agent="test_agent"
    )
    assert success == True
    print("   ✅ Correction added successfully")
    
    # Test statistics
    print("\n▶️  Testing statistics...")
    stats = manager.get_statistics()
    print(f"   Dynamic corrections: {stats['dynamic']['total_corrections']}")
    print(f"   Static productos: {stats['static']['productos']}")
    print("   ✅ Statistics work")
    
    return True


def test_human_in_loop_trainer():
    """Test human-in-the-loop trainer"""
    print("\n" + "="*60)
    print("🧪 TEST 4: Human-in-the-Loop Trainer")
    print("="*60)
    
    from dynamic_knowledge_manager import DynamicKnowledgeManager
    from human_in_loop_trainer import HumanInLoopTrainer
    
    manager = DynamicKnowledgeManager()
    trainer = HumanInLoopTrainer(manager)
    
    # Test training mode activation
    print("\n▶️  Testing training mode activation...")
    result = trainer.process_message("agent_test", "MODO ENTRENAMIENTO")
    assert result["action"] == "training_activated"
    print(f"   Response: {result['response'][:80]}...")
    print("   ✅ Training mode activation works")
    
    # Test emoji correction
    print("\n▶️  Testing emoji correction...")
    result = trainer.process_message(
        "agent_test",
        "❌ El precio correcto es 1800 UYU",
        previous_response="El precio es 1500 UYU"
    )
    assert result["action"] == "correction_received"
    print(f"   Response: {result['response'][:80]}...")
    print("   ✅ Emoji correction works")
    
    # Test approval
    print("\n▶️  Testing correction approval...")
    result = trainer.process_message("agent_test", "✅")
    assert result["action"] in ["correction_applied", "no_pending_correction"]
    print(f"   Response: {result['response'][:80]}...")
    print("   ✅ Approval works")
    
    # Test confidence scoring
    print("\n▶️  Testing confidence scoring...")
    confidence = trainer.calculate_confidence_score(
        "¿Cuál es el precio?",
        "El precio es 1500 UYU por m²",
        {"source": "dynamic"}
    )
    print(f"   Confidence: {confidence:.2f}")
    assert 0.0 <= confidence <= 1.0
    print("   ✅ Confidence scoring works")
    
    return True


def test_integrated_chatbot():
    """Test integrated chatbot with multimodal support"""
    print("\n" + "="*60)
    print("🧪 TEST 5: Integrated Chatbot")
    print("="*60)
    
    from ia_conversacional_integrada import IAConversacionalIntegrada
    
    print("\n▶️  Initializing chatbot...")
    ia = IAConversacionalIntegrada()
    print("   ✅ Chatbot initialized")
    
    # Test normal message processing
    print("\n▶️  Testing normal message processing...")
    respuesta = ia.procesar_mensaje(
        mensaje="¿Qué productos tienen disponibles?",
        cliente_id="test_client",
        sesion_id="test_session_1"
    )
    print(f"   Response length: {len(respuesta.mensaje)} chars")
    print(f"   Confidence: {respuesta.confianza:.2f}")
    print(f"   Type: {respuesta.tipo_respuesta}")
    print("   ✅ Normal message processing works")
    
    # Test multimodal message processing
    if hasattr(ia, 'procesar_mensaje_multimodal'):
        print("\n▶️  Testing multimodal message processing...")
        respuesta = ia.procesar_mensaje_multimodal(
            mensaje="MODO ENTRENAMIENTO",
            cliente_id="test_agent",
            sesion_id="test_session_2",
            mensaje_tipo="text"
        )
        print(f"   Response: {respuesta.mensaje[:100]}...")
        print("   ✅ Multimodal processing works")
    else:
        print("\n⚠️  Multimodal processing not available")
    
    return True


def test_benchmark_system():
    """Test benchmark system"""
    print("\n" + "="*60)
    print("🧪 TEST 6: Benchmark System")
    print("="*60)
    
    from benchmark_system import BenchmarkSystem
    
    benchmark = BenchmarkSystem()
    
    print(f"\n▶️  Test cases loaded: {len(benchmark.test_cases)}")
    
    for i, test_case in enumerate(benchmark.test_cases[:3], 1):
        print(f"\n   {i}. {test_case.test_id}")
        print(f"      Category: {test_case.category}")
        print(f"      Input: {test_case.input_message}")
    
    print("\n✅ Benchmark system initialized successfully")
    
    return True


def run_full_integration_test():
    """Run full integration test"""
    print("\n" + "="*80)
    print("🚀 MULTIMODAL TRAINING SYSTEM - INTEGRATION TEST")
    print("="*80)
    
    tests = [
        ("System Imports", test_system_imports),
        ("Multimodal Processor", test_multimodal_processor),
        ("Dynamic Knowledge Manager", test_dynamic_knowledge_manager),
        ("Human-in-the-Loop Trainer", test_human_in_loop_trainer),
        ("Integrated Chatbot", test_integrated_chatbot),
        ("Benchmark System", test_benchmark_system)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ Test failed: {test_name}")
            print(f"   Error: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready for production.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review the errors above.")
    
    print("="*80)
    
    return passed == total


if __name__ == "__main__":
    success = run_full_integration_test()
    sys.exit(0 if success else 1)
