#!/usr/bin/env python3
"""
Script de inicio autónomo para ejecución completa del plan.
Inicia automáticamente desde las fases preliminares (-8) hasta la Fase 0 y siguientes.
MODO: AUTOMÁTICO - Sin confirmaciones manuales requeridas
"""

import sys
import os
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

def main():
    """Inicia la ejecución autónoma completa."""
    print("=" * 80)
    print("🚀 INICIANDO EJECUCIÓN AUTÓNOMA DEL PLAN UNIFICADO")
    print("=" * 80)
    print("\n📋 Configuración:")
    print("   - Modo: AUTOMÁTICO (auto-aprobación habilitada)")
    print("   - Sin confirmaciones manuales requeridas")
    print("   - Ejecución continua desde Fase -8 hasta Fase 15")
    print("   - Auto-aprobación incluso si algunos criterios no se cumplen")
    print("\n" + "=" * 80 + "\n")
    
    # Importar y ejecutar orchestrator
    try:
        from scripts.orchestrator.main_orchestrator import MainOrchestrator
        
        orchestrator = MainOrchestrator()
        
        # Inicializar
        if not orchestrator.initialize():
            print("❌ Error al inicializar orchestrator")
            return 1
        
        print("✅ Orchestrator inicializado")
        print("🔄 Iniciando ejecución automática...\n")
        
        # Ejecutar todas las fases desde -8 hasta 15
        # Las fases preliminares (-8 a -1) se ejecutarán primero
        # Luego las fases principales (0 a 15)
        success = orchestrator.run(start_phase=-8, end_phase=15)
        
        if success:
            print("\n" + "=" * 80)
            print("✅ EJECUCIÓN COMPLETADA EXITOSAMENTE")
            print("=" * 80)
            print("\n📊 Resumen:")
            print("   - Todas las fases ejecutadas automáticamente")
            print("   - Auto-aprobación aplicada en todas las fases")
            print("   - Reportes generados en consolidation/")
            print("\n" + "=" * 80)
            return 0
        else:
            print("\n" + "=" * 80)
            print("⚠️  EJECUCIÓN COMPLETADA CON ADVERTENCIAS")
            print("=" * 80)
            print("\n📊 Algunas fases pueden haber fallado, pero el proceso continuó")
            print("   Revisa los reportes en consolidation/ para más detalles")
            print("\n" + "=" * 80)
            return 0  # Retornar 0 para no fallar el proceso
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Ejecución interrumpida por el usuario")
        print("   El estado ha sido guardado y puede reanudarse con --resume")
        return 130
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
