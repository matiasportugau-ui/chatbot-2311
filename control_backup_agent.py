#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Control para el Agente de Backup
==========================================

Permite iniciar, detener, y verificar el estado del agente de backup.
"""

import os
import sys
import subprocess
import signal
import json
from pathlib import Path


def get_agent_pid():
    """Obtiene el PID del proceso del agente si está corriendo"""
    try:
        result = subprocess.run(
            ['pgrep', '-f', 'auto_backup_agent.py'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            return [int(pid) for pid in pids if pid]
    except:
        pass
    return []


def get_agent_status():
    """Obtiene el estado del agente"""
    pids = get_agent_pid()
    if pids:
        return {'running': True, 'pids': pids}
    return {'running': False, 'pids': []}


def start_agent():
    """Inicia el agente de backup"""
    status = get_agent_status()
    if status['running']:
        print("⚠️  El agente ya está corriendo (PIDs: {})".format(', '.join(map(str, status['pids']))))
        return False
    
    script_path = Path(__file__).parent / "auto_backup_agent.py"
    if not script_path.exists():
        print("❌ Error: auto_backup_agent.py no encontrado")
        return False
    
    try:
        # Iniciar en background
        process = subprocess.Popen(
            [sys.executable, str(script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(script_path.parent)
        )
        print(f"✅ Agente iniciado (PID: {process.pid})")
        print(f"   El agente guardará el workspace cada 15 minutos")
        print(f"   Backups en: {script_path.parent / 'backups'}")
        return True
    except Exception as e:
        print(f"❌ Error iniciando agente: {e}")
        return False


def stop_agent():
    """Detiene el agente de backup"""
    status = get_agent_status()
    if not status['running']:
        print("ℹ️  El agente no está corriendo")
        return False
    
    stopped = 0
    for pid in status['pids']:
        try:
            os.kill(pid, signal.SIGTERM)
            print(f"✅ Agente detenido (PID: {pid})")
            stopped += 1
        except ProcessLookupError:
            print(f"⚠️  Proceso {pid} ya no existe")
        except PermissionError:
            print(f"❌ Sin permisos para detener proceso {pid}")
        except Exception as e:
            print(f"❌ Error deteniendo proceso {pid}: {e}")
    
    return stopped > 0


def show_status():
    """Muestra el estado del agente"""
    status = get_agent_status()
    backup_dir = Path(__file__).parent / "backups"
    
    print("="*60)
    print("ESTADO DEL AGENTE DE BACKUP")
    print("="*60)
    
    if status['running']:
        print(f"✅ Estado: CORRIENDO")
        print(f"   PIDs: {', '.join(map(str, status['pids']))}")
    else:
        print(f"❌ Estado: DETENIDO")
    
    print()
    print("Configuración:")
    print(f"   Workspace: {Path(__file__).parent}")
    print(f"   Backup dir: {backup_dir}")
    print(f"   Intervalo: 15 minutos")
    
    if backup_dir.exists():
        index_file = backup_dir / "index.json"
        if index_file.exists():
            try:
                with open(index_file, 'r') as f:
                    index = json.load(f)
                    backups = index.get('backups', [])
                    last_backup = index.get('last_backup')
                    
                    print()
                    print("Backups:")
                    print(f"   Total de backups: {len(backups)}")
                    if last_backup:
                        print(f"   Último backup: {last_backup}")
                    
                    if backups:
                        latest = backups[-1]
                        print(f"   Último backup - Archivos: {latest.get('file_count', 'N/A')}")
                        size_mb = latest.get('total_size', 0) / 1024 / 1024
                        print(f"   Último backup - Tamaño: {size_mb:.2f} MB")
            except Exception as e:
                print(f"   ⚠️  Error leyendo índice: {e}")
    else:
        print()
        print("   ℹ️  Aún no se han creado backups")
    
    print("="*60)


def show_logs():
    """Muestra los últimos logs del agente"""
    log_file = Path(__file__).parent / "backups" / "backup_agent.log"
    
    if not log_file.exists():
        print("ℹ️  No hay logs aún (el agente creará logs en el primer backup)")
        return
    
    print("="*60)
    print("ÚLTIMOS LOGS DEL AGENTE")
    print("="*60)
    print()
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # Mostrar últimas 30 líneas
            for line in lines[-30:]:
                print(line.rstrip())
    except Exception as e:
        print(f"❌ Error leyendo logs: {e}")


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Control del Agente de Backup Automático"
    )
    parser.add_argument(
        'action',
        choices=['start', 'stop', 'status', 'restart', 'logs'],
        help='Acción a realizar'
    )
    
    args = parser.parse_args()
    
    if args.action == 'start':
        start_agent()
    elif args.action == 'stop':
        stop_agent()
    elif args.action == 'status':
        show_status()
    elif args.action == 'restart':
        stop_agent()
        import time
        time.sleep(1)
        start_agent()
    elif args.action == 'logs':
        show_logs()


if __name__ == "__main__":
    main()

