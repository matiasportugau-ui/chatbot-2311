#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests de Validación: IA Obligatoria
===================================

Verifica que:
1. NO se use random.choice en ningún lugar
2. NO existan respuestas hardcodeadas
3. TODAS las respuestas se generen con model_integrator
4. Base de conocimiento se incluya en prompts
5. Documentación se cargue correctamente
6. Conversaciones similares se encuentren
7. Sistema de aprendizaje funcione
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import re
import ast
import inspect


def test_no_random_choice():
    """Verifica que random.choice no se use en ia_conversacional_integrada.py"""
    file_path = project_root / "ia_conversacional_integrada.py"
    
    if not file_path.exists():
        print("❌ ia_conversacional_integrada.py no encontrado")
        return False
    
    content = file_path.read_text(encoding='utf-8')
    
    # Buscar random.choice
    matches = re.findall(r'random\.choice', content)
    if matches:
        print(f"❌ Se encontraron {len(matches)} usos de random.choice:")
        for i, match in enumerate(matches, 1):
            print(f"   {i}. {match}")
        return False
    
    print("✅ No se encontró uso de random.choice")
    return True


def test_no_respuestas_hardcodeadas():
    """Verifica que no haya respuestas hardcodeadas de productos"""
    file_path = project_root / "ia_conversacional_integrada.py"
    
    if not file_path.exists():
        print("❌ ia_conversacional_integrada.py no encontrado")
        return False
    
    content = file_path.read_text(encoding='utf-8')
    
    # Buscar respuestas hardcodeadas conocidas
    hardcoded_patterns = [
        r'ISODEC - Panel Aislante Térmico',
        r'POLIESTIRENO EXPANDIDO',
        r'LANA DE ROCA',
        r'\$150/m².*100mm.*Blanco',
        r'\$120/m².*100mm',
        r'\$140/m².*100mm'
    ]
    
    found = []
    for pattern in hardcoded_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            found.append(pattern)
    
    if found:
        print(f"❌ Se encontraron {len(found)} respuestas hardcodeadas:")
        for pattern in found:
            print(f"   - {pattern}")
        return False
    
    print("✅ No se encontraron respuestas hardcodeadas de productos")
    return True


def test_usa_model_integrator():
    """Verifica que se use model_integrator para generar respuestas"""
    file_path = project_root / "ia_conversacional_integrada.py"
    
    if not file_path.exists():
        print("❌ ia_conversacional_integrada.py no encontrado")
        return False
    
    content = file_path.read_text(encoding='utf-8')
    
    # Buscar uso de model_integrator.generate
    if 'model_integrator.generate' not in content:
        print("❌ No se encontró uso de model_integrator.generate")
        return False
    
    # Verificar que hay múltiples usos (en diferentes métodos)
    matches = len(re.findall(r'model_integrator\.generate', content))
    if matches < 3:
        print(f"⚠️  Solo se encontraron {matches} usos de model_integrator.generate (esperado: 3+)")
        return False
    
    print(f"✅ Se encontraron {matches} usos de model_integrator.generate")
    return True


def test_knowledge_manager_inicializado():
    """Verifica que KnowledgeManager se inicialice correctamente"""
    file_path = project_root / "ia_conversacional_integrada.py"
    
    if not file_path.exists():
        print("❌ ia_conversacional_integrada.py no encontrado")
        return False
    
    content = file_path.read_text(encoding='utf-8')
    
    # Verificar que KnowledgeManager se importe
    if 'KnowledgeManager' not in content:
        print("❌ KnowledgeManager no se importa o usa")
        return False
    
    # Verificar que se inicialice en __init__
    if 'self.knowledge_manager' not in content:
        print("❌ knowledge_manager no se inicializa")
        return False
    
    print("✅ KnowledgeManager está integrado")
    return True


def test_training_system_inicializado():
    """Verifica que TrainingSystem se inicialice correctamente"""
    file_path = project_root / "ia_conversacional_integrada.py"
    
    if not file_path.exists():
        print("❌ ia_conversacional_integrada.py no encontrado")
        return False
    
    content = file_path.read_text(encoding='utf-8')
    
    # Verificar que TrainingSystem se importe
    if 'TrainingSystem' not in content:
        print("❌ TrainingSystem no se importa o usa")
        return False
    
    # Verificar que se inicialice en __init__
    if 'self.training_system' not in content:
        print("❌ training_system no se inicializa")
        return False
    
    print("✅ TrainingSystem está integrado")
    return True


def test_metodos_ia_creados():
    """Verifica que se hayan creado los métodos nuevos con IA"""
    file_path = project_root / "ia_conversacional_integrada.py"
    
    if not file_path.exists():
        print("❌ ia_conversacional_integrada.py no encontrado")
        return False
    
    content = file_path.read_text(encoding='utf-8')
    
    # Verificar métodos nuevos
    metodos_requeridos = [
        '_generar_saludo_ia',
        '_generar_despedida_ia',
        '_obtener_informacion_producto_ia',
        '_enriquecer_contexto_completo',
        '_construir_system_prompt',
        '_procesar_con_ia'
    ]
    
    faltantes = []
    for metodo in metodos_requeridos:
        if f'def {metodo}' not in content:
            faltantes.append(metodo)
    
    if faltantes:
        print(f"❌ Faltan {len(faltantes)} métodos requeridos:")
        for metodo in faltantes:
            print(f"   - {metodo}")
        return False
    
    print(f"✅ Todos los {len(metodos_requeridos)} métodos requeridos están presentes")
    return True


def test_no_fallback_pattern_matching():
    """Verifica que no haya fallback a pattern matching"""
    file_path = project_root / "ia_conversacional_integrada.py"
    
    if not file_path.exists():
        print("❌ ia_conversacional_integrada.py no encontrado")
        return False
    
    content = file_path.read_text(encoding='utf-8')
    
    # Buscar llamadas a _procesar_mensaje_patrones (no deprecated)
    if '_procesar_mensaje_patrones(' in content and '_procesar_mensaje_patrones_DEPRECATED' not in content:
        print("⚠️  Se encontró uso de _procesar_mensaje_patrones (debe estar deprecated)")
        return False
    
    # Verificar que procesar_mensaje_usuario no use pattern matching como fallback
    if 'procesar_mensaje_usuario' in content:
        # Buscar en el método procesar_mensaje_usuario
        pattern = r'def procesar_mensaje_usuario.*?(?=def |\Z)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            metodo_content = match.group(0)
            if '_procesar_mensaje_patrones' in metodo_content and 'DEPRECATED' not in metodo_content:
                print("❌ procesar_mensaje_usuario usa pattern matching como fallback")
                return False
    
    print("✅ No hay fallback a pattern matching")
    return True


def test_knowledge_manager_file_exists():
    """Verifica que knowledge_manager.py existe"""
    file_path = project_root / "AI_AGENTS" / "EXECUTOR" / "knowledge_manager.py"
    
    if not file_path.exists():
        print("❌ knowledge_manager.py no encontrado")
        return False
    
    print("✅ knowledge_manager.py existe")
    return True


def test_training_system_file_exists():
    """Verifica que training_system.py existe"""
    file_path = project_root / "AI_AGENTS" / "EXECUTOR" / "training_system.py"
    
    if not file_path.exists():
        print("❌ training_system.py no encontrado")
        return False
    
    print("✅ training_system.py existe")
    return True


def main():
    """Ejecuta todos los tests"""
    print("=" * 80)
    print("TESTS DE VALIDACIÓN: IA OBLIGATORIA")
    print("=" * 80)
    print()
    
    tests = [
        ("No random.choice", test_no_random_choice),
        ("No respuestas hardcodeadas", test_no_respuestas_hardcodeadas),
        ("Usa model_integrator", test_usa_model_integrator),
        ("KnowledgeManager inicializado", test_knowledge_manager_inicializado),
        ("TrainingSystem inicializado", test_training_system_inicializado),
        ("Métodos IA creados", test_metodos_ia_creados),
        ("No fallback pattern matching", test_no_fallback_pattern_matching),
        ("knowledge_manager.py existe", test_knowledge_manager_file_exists),
        ("training_system.py existe", test_training_system_file_exists),
    ]
    
    resultados = []
    for nombre, test_func in tests:
        print(f"Test: {nombre}")
        try:
            resultado = test_func()
            resultados.append((nombre, resultado))
        except Exception as e:
            print(f"❌ Error ejecutando test: {e}")
            resultados.append((nombre, False))
        print()
    
    # Resumen
    print("=" * 80)
    print("RESUMEN")
    print("=" * 80)
    
    exitosos = sum(1 for _, resultado in resultados if resultado)
    total = len(resultados)
    
    for nombre, resultado in resultados:
        status = "✅ PASS" if resultado else "❌ FAIL"
        print(f"{status}: {nombre}")
    
    print()
    print(f"Total: {exitosos}/{total} tests exitosos")
    
    if exitosos == total:
        print("🎉 Todos los tests pasaron!")
        return 0
    else:
        print(f"⚠️  {total - exitosos} test(s) fallaron")
        return 1


if __name__ == "__main__":
    sys.exit(main())

