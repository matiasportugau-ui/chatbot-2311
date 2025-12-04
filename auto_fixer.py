#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Auto-Reparación (Auto-Fix)
Detecta problemas comunes y los resuelve automáticamente
"""

import os
import sys
import subprocess
import json
import re
import shutil
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

class AutoFixer:
    """Sistema de auto-reparación de problemas comunes"""
    
    def __init__(self, solutions_db_path: str = 'auto_fix_solutions.json'):
        self.solutions_db = Path(solutions_db_path)
        self.applied_solutions = self._load_solutions()
        self.fixes_applied = []
    
    def _load_solutions(self) -> Dict:
        """Carga soluciones aplicadas previamente"""
        if self.solutions_db.exists():
            try:
                return json.loads(self.solutions_db.read_text(encoding='utf-8'))
            except:
                return {}
        return {}
    
    def _save_solutions(self):
        """Guarda soluciones aplicadas"""
        self.solutions_db.write_text(
            json.dumps(self.applied_solutions, indent=2),
            encoding='utf-8'
        )
    
    def _record_fix(self, problem: str, solution: str, success: bool):
        """Registra una solución aplicada"""
        fix_id = f"{problem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.applied_solutions[fix_id] = {
            'problem': problem,
            'solution': solution,
            'success': success,
            'timestamp': datetime.now().isoformat()
        }
        self.fixes_applied.append(fix_id)
        self._save_solutions()
    
    def detect_and_fix(self, error_message: str, context: Dict = None) -> Tuple[bool, str]:
        """Detecta el problema y aplica solución automática"""
        
        error_lower = error_message.lower()
        
        # 1. Error: Módulo no encontrado
        if 'modulenotfounderror' in error_lower or 'no module named' in error_lower:
            return self._fix_missing_module(error_message)
        
        # 2. Error: Puerto ocupado
        if 'port is already allocated' in error_lower or 'address already in use' in error_lower:
            return self._fix_port_conflict(error_message, context)
        
        # 3. Error: Permisos
        if 'permission denied' in error_lower or 'eacces' in error_lower:
            return self._fix_permissions(error_message, context)
        
        # 4. Error: Archivo no encontrado
        if 'filenotfounderror' in error_lower or 'no such file' in error_lower:
            return self._fix_missing_file(error_message)
        
        # 5. Error: Dependencias faltantes
        if 'requirements.txt' in error_lower or 'package.json' in error_lower:
            return self._fix_missing_dependencies(error_message)
        
        # 6. Error: MongoDB connection
        if 'mongodb' in error_lower and ('connection' in error_lower or 'timeout' in error_lower):
            return self._fix_mongodb_connection(error_message, context)
        
        # 7. Error: Python version
        if 'python' in error_lower and ('version' in error_lower or '3.' in error_message):
            return self._fix_python_version(error_message)
        
        # 8. Error: Node/npm
        if 'npm' in error_lower or 'node' in error_lower:
            return self._fix_node_issues(error_message)
        
        # 9. Error: Docker
        if 'docker' in error_lower:
            return self._fix_docker_issues(error_message, context)
        
        # 10. Error: .env faltante
        if '.env' in error_lower and ('not found' in error_lower or 'missing' in error_lower):
            return self._fix_missing_env(error_message)
        
        return False, "Problema no reconocido - requiere intervención manual"
    
    def _fix_missing_module(self, error: str) -> Tuple[bool, str]:
        """Arregla módulo faltante"""
        # Extraer nombre del módulo
        match = re.search(r"no module named ['\"]([^'\"]+)['\"]", error, re.IGNORECASE)
        if not match:
            return False, "No se pudo identificar el módulo faltante"
        
        module_name = match.group(1)
        solution = f"Instalar módulo: {module_name}"
        
        try:
            print(f"🔧 Auto-fix: Instalando {module_name}...")
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', module_name],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                self._record_fix(f"missing_module_{module_name}", solution, True)
                return True, f"Módulo {module_name} instalado exitosamente"
            else:
                self._record_fix(f"missing_module_{module_name}", solution, False)
                return False, f"Error instalando {module_name}: {result.stderr[:200]}"
        except Exception as e:
            return False, f"Error en auto-fix: {e}"
    
    def _fix_port_conflict(self, error: str, context: Dict) -> Tuple[bool, str]:
        """Arregla conflicto de puerto"""
        # Extraer puerto
        match = re.search(r'port[:\s]+(\d+)', error, re.IGNORECASE)
        if not match:
            return False, "No se pudo identificar el puerto"
        
        port = match.group(1)
        solution = f"Liberar puerto {port} o usar otro puerto"
        
        # Si es MongoDB, intentar detener contenedor existente
        if 'mongodb' in error.lower() or port == '27017':
            try:
                print(f"🔧 Auto-fix: Verificando contenedores MongoDB...")
                result = subprocess.run(
                    ['docker', 'ps', '-a', '--format', '{{.Names}}'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                containers = result.stdout.lower()
                if 'mongodb' in containers or 'mongo' in containers:
                    # Encontrar nombre exacto
                    for line in result.stdout.split('\n'):
                        if 'mongo' in line.lower():
                            container_name = line.strip()
                            print(f"🔧 Auto-fix: Deteniendo contenedor {container_name}...")
                            subprocess.run(['docker', 'stop', container_name], timeout=10)
                            subprocess.run(['docker', 'rm', container_name], timeout=10)
                            self._record_fix(f"port_conflict_{port}", solution, True)
                            return True, f"Contenedor {container_name} detenido y eliminado"
            except Exception as e:
                pass
        
        self._record_fix(f"port_conflict_{port}", solution, False)
        return False, f"Puerto {port} ocupado - requiere intervención manual"
    
    def _fix_permissions(self, error: str, context: Dict) -> Tuple[bool, str]:
        """Arregla problemas de permisos"""
        # Extraer archivo
        match = re.search(r"['\"]([^'\"]+)['\"]", error)
        if not match:
            return False, "No se pudo identificar el archivo"
        
        file_path = Path(match.group(1))
        solution = f"Dar permisos de ejecución a {file_path}"
        
        try:
            if file_path.exists():
                print(f"🔧 Auto-fix: Dando permisos a {file_path}...")
                os.chmod(file_path, 0o755)
                self._record_fix(f"permissions_{file_path.name}", solution, True)
                return True, f"Permisos actualizados para {file_path}"
            else:
                return False, f"Archivo no encontrado: {file_path}"
        except Exception as e:
            self._record_fix(f"permissions_{file_path.name}", solution, False)
            return False, f"Error actualizando permisos: {e}"
    
    def _fix_missing_file(self, error: str) -> Tuple[bool, str]:
        """Arregla archivo faltante"""
        # Extraer nombre de archivo
        match = re.search(r"['\"]([^'\"]+)['\"]", error)
        if not match:
            return False, "No se pudo identificar el archivo"
        
        file_path = Path(match.group(1))
        solution = f"Crear archivo faltante: {file_path}"
        
        # Si es .env, crear desde .env.example
        if '.env' in file_path.name and not file_path.exists():
            env_example = Path('.env.example')
            if env_example.exists():
                try:
                    print(f"🔧 Auto-fix: Creando {file_path} desde .env.example...")
                    shutil.copy(env_example, file_path)
                    self._record_fix(f"missing_file_{file_path.name}", solution, True)
                    return True, f"Archivo {file_path} creado desde .env.example"
                except Exception as e:
                    return False, f"Error creando archivo: {e}"
        
        self._record_fix(f"missing_file_{file_path.name}", solution, False)
        return False, f"Archivo faltante: {file_path} - requiere creación manual"
    
    def _fix_missing_dependencies(self, error: str) -> Tuple[bool, str]:
        """Arregla dependencias faltantes"""
        solution = "Instalar dependencias desde requirements.txt"
        
        try:
            if Path('requirements.txt').exists():
                print("🔧 Auto-fix: Instalando dependencias Python...")
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode == 0:
                    self._record_fix("missing_dependencies", solution, True)
                    return True, "Dependencias instaladas exitosamente"
                else:
                    self._record_fix("missing_dependencies", solution, False)
                    return False, f"Error instalando dependencias: {result.stderr[:200]}"
            else:
                return False, "requirements.txt no encontrado"
        except Exception as e:
            return False, f"Error en auto-fix: {e}"
    
    def _fix_mongodb_connection(self, error: str, context: Dict) -> Tuple[bool, str]:
        """Arregla conexión MongoDB"""
        solution = "Iniciar MongoDB Docker container"
        
        try:
            print("🔧 Auto-fix: Verificando MongoDB...")
            # Buscar contenedor existente
            result = subprocess.run(
                ['docker', 'ps', '-a', '--format', '{{.Names}}'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            containers = result.stdout.lower()
            mongo_containers = ['mongodb', 'bmc-mongodb', 'mongo']
            
            for name in mongo_containers:
                if name in containers:
                    # Iniciar contenedor
                    print(f"🔧 Auto-fix: Iniciando contenedor {name}...")
                    subprocess.run(['docker', 'start', name], timeout=10)
                    time.sleep(3)
                    self._record_fix("mongodb_connection", solution, True)
                    return True, f"MongoDB iniciado: {name}"
            
            # Crear nuevo contenedor
            print("🔧 Auto-fix: Creando contenedor MongoDB...")
            subprocess.run([
                'docker', 'run', '-d',
                '--name', 'mongodb',
                '-p', '27017:27017',
                '-v', 'mongodb_data:/data/db',
                'mongo:latest'
            ], timeout=60)
            time.sleep(3)
            self._record_fix("mongodb_connection", solution, True)
            return True, "MongoDB creado e iniciado"
        except Exception as e:
            self._record_fix("mongodb_connection", solution, False)
            return False, f"Error configurando MongoDB: {e}"
    
    def _fix_python_version(self, error: str) -> Tuple[bool, str]:
        """Arregla versión de Python"""
        solution = "Verificar versión de Python"
        version = sys.version_info
        
        if version.major >= 3 and version.minor >= 8:
            self._record_fix("python_version", solution, True)
            return True, f"Python {version.major}.{version.minor} es compatible"
        else:
            self._record_fix("python_version", solution, False)
            return False, f"Python {version.major}.{version.minor} no es compatible - requiere 3.8+"
    
    def _fix_node_issues(self, error: str) -> Tuple[bool, str]:
        """Arregla problemas de Node.js"""
        solution = "Verificar Node.js y npm"
        
        try:
            # Verificar Node.js
            result = subprocess.run(['node', '--version'], 
                                 capture_output=True, timeout=5)
            if result.returncode == 0:
                self._record_fix("node_issues", solution, True)
                return True, f"Node.js disponible: {result.stdout.decode().strip()}"
            else:
                self._record_fix("node_issues", solution, False)
                return False, "Node.js no está instalado"
        except:
            self._record_fix("node_issues", solution, False)
            return False, "Node.js no disponible (opcional)"
    
    def _fix_docker_issues(self, error: str, context: Dict) -> Tuple[bool, str]:
        """Arregla problemas de Docker"""
        solution = "Verificar Docker"
        
        try:
            result = subprocess.run(['docker', '--version'],
                                 capture_output=True, timeout=5)
            if result.returncode == 0:
                self._record_fix("docker_issues", solution, True)
                return True, "Docker disponible"
            else:
                self._record_fix("docker_issues", solution, False)
                return False, "Docker no está disponible"
        except:
            self._record_fix("docker_issues", solution, False)
            return False, "Docker no está instalado o no está corriendo"
    
    def _fix_missing_env(self, error: str) -> Tuple[bool, str]:
        """Arregla archivo .env faltante"""
        solution = "Crear .env desde .env.example"
        
        env_files = ['.env.local', '.env']
        env_example = Path('.env.example')
        
        for env_file in env_files:
            if Path(env_file).exists():
                return True, f"{env_file} ya existe"
        
        if env_example.exists():
            try:
                print("🔧 Auto-fix: Creando .env.local desde .env.example...")
                shutil.copy(env_example, '.env.local')
                self._record_fix("missing_env", solution, True)
                return True, ".env.local creado desde .env.example"
            except Exception as e:
                self._record_fix("missing_env", solution, False)
                return False, f"Error creando .env: {e}"
        else:
            return False, ".env.example no encontrado"
    
    def get_fixes_summary(self) -> Dict:
        """Obtiene resumen de fixes aplicados"""
        return {
            'total_fixes': len(self.fixes_applied),
            'fixes_applied': self.fixes_applied,
            'solutions_db': len(self.applied_solutions)
        }

