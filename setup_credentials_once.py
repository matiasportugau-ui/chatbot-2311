#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuración Única de Credenciales
====================================

Script que configura TODAS las credenciales UNA SOLA VEZ.
Después de ejecutar esto, todos los scripts usarán automáticamente
las credenciales configuradas.

Ejecuta esto UNA VEZ y nunca más tendrás que configurar credenciales.
"""

import sys
from pathlib import Path
from unified_credentials_manager import UnifiedCredentialsManager, ALL_CREDENTIALS

def main():
    print("\n" + "="*80)
    print("🔐 CONFIGURACIÓN ÚNICA DE CREDENCIALES")
    print("="*80)
    print("\nEste script configurará TODAS las credenciales necesarias.")
    print("Después de esto, NO tendrás que configurar credenciales nunca más.")
    print("\n" + "="*80)
    
    manager = UnifiedCredentialsManager()
    
    # Verificar qué credenciales ya están configuradas
    print("\n📊 Verificando credenciales existentes...")
    status = manager.check_credentials()
    available = [k for k, v in status.items() if v]
    missing = [k for k, v in status.items() if not v]
    
    if available:
        print(f"\n✅ Ya tienes {len(available)} credenciales configuradas:")
        for key in sorted(available):
            print(f"   • {key}")
    
    if missing:
        print(f"\n⚠️  Faltan {len(missing)} credenciales:")
        for key in sorted(missing):
            cred_info = ALL_CREDENTIALS.get(key, {})
            desc = cred_info.get('description', '')
            print(f"   • {key}: {desc}")
    
    print("\n" + "="*80)
    print("OPCIONES:")
    print("="*80)
    print("1. Ejecutar wizard interactivo (recomendado)")
    print("2. Ver estado actual de credenciales")
    print("3. Configurar credenciales específicas")
    print("4. Salir")
    print()
    
    choice = input("Selecciona una opción [1]: ").strip() or "1"
    
    if choice == "1":
        # Ejecutar wizard
        import subprocess
        subprocess.run([sys.executable, __file__.replace('setup_credentials_once.py', 'unified_credentials_manager.py'), 'wizard'])
    
    elif choice == "2":
        manager.print_status()
    
    elif choice == "3":
        print("\n📝 Configurar credenciales específicas:")
        print("(Presiona Enter sin valor para terminar)\n")
        
        import getpass
        
        while True:
            key = input("Clave de la credencial (o Enter para terminar): ").strip()
            if not key:
                break
            
            if key not in ALL_CREDENTIALS:
                print(f"⚠️  '{key}' no está en la lista de credenciales conocidas")
                continue
            
            cred_info = ALL_CREDENTIALS[key]
            desc = cred_info.get('description', '')
            print(f"   {desc}")
            
            if key.upper().endswith('_PASSWORD') or key.upper().endswith('_TOKEN') or key.upper().endswith('_KEY'):
                value = getpass.getpass(f"   Valor: ")
            else:
                value = input(f"   Valor: ").strip()
            
            if value:
                manager.set_credential(key, value, save_to='all')
                print(f"   ✅ '{key}' guardada\n")
            else:
                print(f"   ⏭️  Omitida\n")
    
    print("\n" + "="*80)
    print("✅ CONFIGURACIÓN COMPLETADA")
    print("="*80)
    print("\n💡 Ahora todos los scripts cargarán automáticamente estas credenciales.")
    print("   No necesitas configurarlas de nuevo.\n")
    
    # Mostrar estado final
    manager.print_status()


if __name__ == "__main__":
    main()

