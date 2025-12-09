#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup Script para Agente de Backup Automático
=============================================

Configura el agente para que se active automáticamente al abrir el workspace.
"""

import os
import sys
import json
from pathlib import Path


def setup_vscode_tasks():
    """Configura tareas de VSCode para ejecutar el agente automáticamente"""
    vscode_dir = Path(".vscode")
    vscode_dir.mkdir(exist_ok=True)
    
    tasks_file = vscode_dir / "tasks.json"
    
    # Leer tareas existentes o crear nuevas
    if tasks_file.exists():
        try:
            with open(tasks_file, 'r', encoding='utf-8') as f:
                tasks = json.load(f)
        except:
            tasks = {"version": "2.0.0", "tasks": []}
    else:
        tasks = {"version": "2.0.0", "tasks": []}
    
    # Agregar tarea de backup
    backup_task = {
        "label": "Start Auto Backup Agent",
        "type": "shell",
        "command": "${workspaceFolder}/auto_backup_agent.py",
        "isBackground": True,
        "problemMatcher": [],
        "runOptions": {
            "runOn": "folderOpen"
        },
        "presentation": {
            "reveal": "silent",
            "panel": "dedicated"
        }
    }
    
    # Verificar si la tarea ya existe
    task_exists = any(task.get("label") == "Start Auto Backup Agent" for task in tasks["tasks"])
    
    if not task_exists:
        tasks["tasks"].append(backup_task)
        
        with open(tasks_file, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, indent=2, ensure_ascii=False)
        
        print("✅ Tarea de VSCode configurada")
        return True
    else:
        print("ℹ️  Tarea de VSCode ya existe")
        return False


def setup_cursor_config():
    """Configura Cursor para ejecutar el agente automáticamente"""
    cursor_dir = Path(".cursor")
    cursor_dir.mkdir(exist_ok=True)
    
    # Similar a VSCode, Cursor usa .vscode/tasks.json
    return setup_vscode_tasks()


def create_startup_script():
    """Crea script de inicio para diferentes sistemas"""
    scripts = {}
    
    # Script para Windows
    windows_script = """@echo off
echo Iniciando Agente de Backup Automático...
python "%~dp0auto_backup_agent.py"
pause
"""
    scripts['start_backup_agent.bat'] = windows_script
    
    # Script para Unix/Linux/Mac
    unix_script = """#!/bin/bash
echo "Iniciando Agente de Backup Automático..."
cd "$(dirname "$0")"
python3 auto_backup_agent.py
"""
    scripts['start_backup_agent.sh'] = unix_script
    
    # Crear scripts
    for filename, content in scripts.items():
        script_path = Path(filename)
        script_path.write_text(content, encoding='utf-8')
        if filename.endswith('.sh'):
            os.chmod(script_path, 0o755)
        print(f"✅ Script creado: {filename}")
    
    return scripts


def setup_launch_config():
    """Configura launch.json para debugging"""
    vscode_dir = Path(".vscode")
    vscode_dir.mkdir(exist_ok=True)
    
    launch_file = vscode_dir / "launch.json"
    
    # Leer configuración existente o crear nueva
    if launch_file.exists():
        try:
            with open(launch_file, 'r', encoding='utf-8') as f:
                launch = json.load(f)
        except:
            launch = {"version": "0.2.0", "configurations": []}
    else:
        launch = {"version": "0.2.0", "configurations": []}
    
    # Agregar configuración de backup agent
    backup_config = {
        "name": "Auto Backup Agent",
        "type": "python",
        "request": "launch",
        "program": "${workspaceFolder}/auto_backup_agent.py",
        "console": "integratedTerminal",
        "justMyCode": True
    }
    
    # Verificar si ya existe
    config_exists = any(
        config.get("name") == "Auto Backup Agent" 
        for config in launch.get("configurations", [])
    )
    
    if not config_exists:
        launch["configurations"].append(backup_config)
        
        with open(launch_file, 'w', encoding='utf-8') as f:
            json.dump(launch, f, indent=2, ensure_ascii=False)
        
        print("✅ Configuración de launch creada")
        return True
    else:
        print("ℹ️  Configuración de launch ya existe")
        return False


def main():
    """Ejecuta el setup completo"""
    print("="*60)
    print("SETUP: Agente de Backup Automático")
    print("="*60)
    print()
    
    # Verificar que el script de backup existe
    if not Path("auto_backup_agent.py").exists():
        print("❌ Error: auto_backup_agent.py no encontrado")
        print("   Asegúrate de estar en el directorio correcto")
        return 1
    
    # Configurar VSCode/Cursor
    print("Configurando VSCode/Cursor...")
    setup_vscode_tasks()
    setup_cursor_config()
    print()
    
    # Configurar launch
    print("Configurando launch.json...")
    setup_launch_config()
    print()
    
    # Crear scripts de inicio
    print("Creando scripts de inicio...")
    create_startup_script()
    print()
    
    print("="*60)
    print("✅ SETUP COMPLETADO")
    print("="*60)
    print()
    print("El agente se ejecutará automáticamente cuando:")
    print("  - Abras el workspace en VSCode/Cursor")
    print("  - O ejecutes manualmente: python auto_backup_agent.py")
    print()
    print("Los backups se guardarán en: ./backups/")
    print()
    print("Para ejecutar manualmente:")
    print("  Windows: start_backup_agent.bat")
    print("  Unix/Mac: ./start_backup_agent.sh")
    print("="*60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

