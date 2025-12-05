#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuración Automática Completa de Credenciales
==================================================

Este script configura TODO automáticamente:
1. Genera contraseña maestra automáticamente (si no existe)
2. Configura todas las credenciales necesarias
3. Todo listo para usar

Ejecuta esto UNA VEZ y nunca más tendrás que configurar nada.
"""

import sys
from pathlib import Path

def main():
    print("\n" + "="*80)
    print("🔐 CONFIGURACIÓN AUTOMÁTICA DE CREDENCIALES")
    print("="*80)
    print("\nEste script configurará TODO automáticamente:")
    print("  ✅ Generará contraseña maestra automáticamente")
    print("  ✅ Configurará todas las credenciales necesarias")
    print("  ✅ Todo funcionará sin configuración manual")
    print("\n" + "="*80)
    
    # 1. Generar contraseña maestra automáticamente
    print("\n📝 Paso 1: Configurando contraseña maestra...")
    try:
        from auto_master_password import get_or_create_master_password
        password = get_or_create_master_password()
        print("✅ Contraseña maestra configurada automáticamente")
        print("   (No necesitas recordarla - se usa automáticamente)")
    except Exception as e:
        print(f"⚠️  Error generando contraseña maestra: {e}")
        print("   Continuando sin archivo cifrado (usando solo .env.local)")
    
    # 2. Cargar sistema unificado
    print("\n📝 Paso 2: Cargando sistema de credenciales...")
    try:
        from unified_credentials_manager import UnifiedCredentialsManager
        manager = UnifiedCredentialsManager()
        print("✅ Sistema de credenciales cargado")
    except Exception as e:
        print(f"❌ Error cargando sistema: {e}")
        return 1
    
    # 3. Verificar estado
    print("\n📝 Paso 3: Verificando credenciales...")
    status = manager.check_credentials()
    available = [k for k, v in status.items() if v]
    missing = [k for k, v in status.items() if not v]
    
    # Filtrar BMC_MASTER_PASSWORD de las faltantes (se genera automáticamente)
    missing = [k for k in missing if k != 'BMC_MASTER_PASSWORD']
    
    if available:
        print(f"\n✅ Ya tienes {len(available)} credenciales configuradas")
    
    if missing:
        print(f"\n⚠️  Faltan {len(missing)} credenciales:")
        for key in sorted(missing)[:10]:  # Mostrar solo las primeras 10
            print(f"   • {key}")
        if len(missing) > 10:
            print(f"   ... y {len(missing) - 10} más")
        
        print("\n💡 Opciones:")
        print("   1. Configurar ahora (wizard interactivo)")
        print("   2. Configurar después (puedes usar: python unified_credentials_manager.py wizard)")
        print("   3. Continuar sin configurar (usar solo las que ya tienes)")
        
        choice = input("\n¿Qué deseas hacer? [3]: ").strip() or "3"
        
        if choice == "1":
            print("\n📝 Ejecutando wizard de configuración...")
            import subprocess
            subprocess.run([sys.executable, 'unified_credentials_manager.py', 'wizard'])
    
    # 4. Mostrar estado final
    print("\n" + "="*80)
    print("✅ CONFIGURACIÓN COMPLETADA")
    print("="*80)
    
    manager.print_status()
    
    print("\n💡 IMPORTANTE:")
    print("   • La contraseña maestra se generó automáticamente")
    print("   • No necesitas recordarla - se usa automáticamente")
    print("   • Todas las credenciales se cargan automáticamente en todos los scripts")
    print("   • No necesitas configurar nada más manualmente")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

