#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para gestionar procesos del proyecto BMC desde Cursor
Permite listar, detener e iniciar servicios del chatbot
"""

import os
import sys
import signal
import subprocess
import psutil
from typing import List, Dict, Optional


class ProcessManager:
    """Gestor de procesos del proyecto"""
    
    PROJECT_SCRIPTS = [
        'chat_interactivo.py',
        'api_server.py',
        'sistema_completo_integrado.py',
        'automated_agent_system.py',
        'ejecutar_sistema.py',
        'simulate_chat.py'
    ]
    
    def __init__(self):
        self.workspace = '/workspace'
        
    def find_project_processes(self) -> List[Dict]:
        """Encuentra todos los procesos del proyecto"""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'status', 'cpu_percent', 'memory_percent']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if not cmdline:
                    continue
                    
                cmdline_str = ' '.join(cmdline)
                
                # Buscar scripts del proyecto
                for script in self.PROJECT_SCRIPTS:
                    if script in cmdline_str:
                        processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'script': script,
                            'cmdline': cmdline_str,
                            'status': proc.info['status'],
                            'cpu': proc.info.get('cpu_percent', 0),
                            'memory': proc.info.get('memory_percent', 0)
                        })
                        break
                        
                # Buscar contenedores Docker relacionados
                if 'docker' in cmdline_str.lower() and 'bmc' in cmdline_str.lower():
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': 'Docker Container',
                        'script': 'docker',
                        'cmdline': cmdline_str[:100],
                        'status': proc.info['status'],
                        'cpu': proc.info.get('cpu_percent', 0),
                        'memory': proc.info.get('memory_percent', 0)
                    })
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        return processes
    
    def find_listening_ports(self) -> List[Dict]:
        """Encuentra puertos en escucha del proyecto"""
        ports = []
        common_ports = [3000, 5000, 5678, 8000, 8080, 27017]
        
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == 'LISTEN' and conn.laddr.port in common_ports:
                try:
                    proc = psutil.Process(conn.pid) if conn.pid else None
                    ports.append({
                        'port': conn.laddr.port,
                        'pid': conn.pid,
                        'process': proc.name() if proc else 'unknown'
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    ports.append({
                        'port': conn.laddr.port,
                        'pid': conn.pid,
                        'process': 'unknown'
                    })
                    
        return ports
    
    def check_docker_containers(self) -> List[Dict]:
        """Verifica contenedores Docker del proyecto"""
        containers = []
        
        try:
            result = subprocess.run(
                ['docker', 'ps', '-a', '--format', '{{.ID}}|{{.Names}}|{{.Status}}|{{.Ports}}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line and ('bmc' in line.lower() or 'mongo' in line.lower() or 'n8n' in line.lower()):
                        parts = line.split('|')
                        if len(parts) >= 3:
                            containers.append({
                                'id': parts[0][:12],
                                'name': parts[1],
                                'status': parts[2],
                                'ports': parts[3] if len(parts) > 3 else ''
                            })
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
            
        return containers
    
    def stop_process(self, pid: int, force: bool = False) -> bool:
        """Detiene un proceso por PID"""
        try:
            proc = psutil.Process(pid)
            if force:
                proc.kill()
            else:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except psutil.TimeoutExpired:
                    proc.kill()
            return True
        except psutil.NoSuchProcess:
            return False
        except psutil.AccessDenied:
            print(f"⚠️  No tienes permisos para detener el proceso {pid}")
            return False
    
    def stop_docker_container(self, container_id: str) -> bool:
        """Detiene un contenedor Docker"""
        try:
            result = subprocess.run(
                ['docker', 'stop', container_id],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def print_status(self):
        """Imprime el estado completo del sistema"""
        print("=" * 80)
        print("🔍 ESTADO DE PROCESOS DEL PROYECTO BMC")
        print("=" * 80)
        print()
        
        # Procesos Python
        processes = self.find_project_processes()
        if processes:
            print("📊 PROCESOS PYTHON ACTIVOS:")
            print("-" * 80)
            for proc in processes:
                print(f"  PID: {proc['pid']}")
                print(f"  Script: {proc['script']}")
                print(f"  Estado: {proc['status']}")
                print(f"  CPU: {proc['cpu']:.1f}% | Memoria: {proc['memory']:.1f}%")
                print(f"  Comando: {proc['cmdline'][:100]}...")
                print("-" * 80)
        else:
            print("✅ No hay procesos Python del proyecto corriendo actualmente")
            print()
        
        # Puertos en escucha
        ports = self.find_listening_ports()
        if ports:
            print("🌐 PUERTOS EN ESCUCHA:")
            print("-" * 80)
            for port_info in ports:
                print(f"  Puerto {port_info['port']}: {port_info['process']} (PID: {port_info['pid']})")
            print()
        
        # Contenedores Docker
        containers = self.check_docker_containers()
        if containers:
            print("🐳 CONTENEDORES DOCKER:")
            print("-" * 80)
            for container in containers:
                status_icon = "🟢" if "Up" in container['status'] else "🔴"
                print(f"  {status_icon} {container['name']} ({container['id']})")
                print(f"     Estado: {container['status']}")
                if container['ports']:
                    print(f"     Puertos: {container['ports']}")
                print()
        else:
            print("📦 No hay contenedores Docker del proyecto corriendo")
            print()
    
    def interactive_stop(self):
        """Modo interactivo para detener procesos"""
        processes = self.find_project_processes()
        containers = self.check_docker_containers()
        
        if not processes and not containers:
            print("✅ No hay procesos o contenedores para detener")
            return
        
        print("\n🛑 DETENER PROCESOS/CONTENEDORES:")
        print("-" * 80)
        
        items = []
        
        # Listar procesos
        for i, proc in enumerate(processes, 1):
            items.append(('process', proc))
            print(f"  {i}. [PROCESO] {proc['script']} (PID: {proc['pid']})")
        
        # Listar contenedores
        for i, container in enumerate(containers, len(processes) + 1):
            items.append(('container', container))
            status = "🟢 Activo" if "Up" in container['status'] else "🔴 Detenido"
            print(f"  {i}. [DOCKER] {container['name']} - {status}")
        
        print(f"  0. Cancelar")
        print()
        
        try:
            choice = input("Selecciona el número del elemento a detener: ").strip()
            choice_num = int(choice)
            
            if choice_num == 0:
                print("Operación cancelada")
                return
            
            if 1 <= choice_num <= len(items):
                item_type, item_data = items[choice_num - 1]
                
                if item_type == 'process':
                    print(f"\n⏹️  Deteniendo proceso {item_data['script']} (PID: {item_data['pid']})...")
                    if self.stop_process(item_data['pid']):
                        print("✅ Proceso detenido exitosamente")
                    else:
                        print("❌ No se pudo detener el proceso")
                        
                elif item_type == 'container':
                    print(f"\n⏹️  Deteniendo contenedor {item_data['name']}...")
                    if self.stop_docker_container(item_data['id']):
                        print("✅ Contenedor detenido exitosamente")
                    else:
                        print("❌ No se pudo detener el contenedor")
            else:
                print("❌ Opción inválida")
                
        except ValueError:
            print("❌ Entrada inválida")
        except KeyboardInterrupt:
            print("\n\nOperación cancelada por el usuario")


def main():
    """Función principal"""
    manager = ProcessManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'status' or command == 'list' or command == 'ls':
            manager.print_status()
            
        elif command == 'stop':
            if len(sys.argv) > 2:
                try:
                    pid = int(sys.argv[2])
                    print(f"Deteniendo proceso con PID {pid}...")
                    if manager.stop_process(pid):
                        print("✅ Proceso detenido")
                    else:
                        print("❌ No se pudo detener el proceso")
                except ValueError:
                    print("❌ PID inválido")
            else:
                manager.interactive_stop()
                
        elif command == 'kill':
            if len(sys.argv) > 2:
                try:
                    pid = int(sys.argv[2])
                    print(f"Forzando detención del proceso con PID {pid}...")
                    if manager.stop_process(pid, force=True):
                        print("✅ Proceso eliminado")
                    else:
                        print("❌ No se pudo eliminar el proceso")
                except ValueError:
                    print("❌ PID inválido")
            else:
                print("❌ Debes especificar un PID")
                
        elif command == 'help' or command == '-h' or command == '--help':
            print_help()
            
        else:
            print(f"❌ Comando desconocido: {command}")
            print_help()
    else:
        # Modo interactivo por defecto
        manager.print_status()
        print("\n💡 Usa 'python gestionar_procesos.py stop' para detener procesos")
        print("💡 Usa 'python gestionar_procesos.py help' para ver todos los comandos")


def print_help():
    """Imprime la ayuda"""
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                    GESTOR DE PROCESOS DEL PROYECTO BMC                      ║
╚════════════════════════════════════════════════════════════════════════════╝

USO:
    python gestionar_procesos.py [comando] [argumentos]

COMANDOS:
    status, list, ls        Muestra el estado de todos los procesos y contenedores
    stop [PID]             Detiene un proceso (interactivo si no se especifica PID)
    kill [PID]             Fuerza la detención de un proceso
    help, -h, --help       Muestra esta ayuda

EJEMPLOS:
    python gestionar_procesos.py status
    python gestionar_procesos.py stop
    python gestionar_procesos.py stop 1234
    python gestionar_procesos.py kill 1234

NOTAS:
    - Sin argumentos, muestra el estado y opciones disponibles
    - Los contenedores Docker también se pueden gestionar
    - Usa 'stop' para una detención elegante y 'kill' para forzar
""")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Saliendo...")
        sys.exit(0)
