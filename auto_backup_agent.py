#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agente de Backup Automático de Workspace
========================================

Guarda automáticamente TODO el trabajo del workspace cada 15 minutos.
Se activa automáticamente al abrir el workspace y trabaja de forma
recurrente y autónoma.

Uso:
    python auto_backup_agent.py
    
El agente se ejecuta automáticamente en background.
"""

import os
import sys
import shutil
import json
import time
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Optional
from threading import Thread, Event
import signal


class WorkspaceBackupAgent:
    """Agente autónomo de backup que guarda el workspace cada 15 minutos"""
    
    def __init__(self, workspace_root: Optional[str] = None, backup_dir: Optional[str] = None):
        """
        Inicializa el agente de backup
        
        Args:
            workspace_root: Ruta raíz del workspace (por defecto: directorio actual)
            backup_dir: Directorio donde guardar backups (por defecto: ./backups)
        """
        self.workspace_root = Path(workspace_root or os.getcwd()).resolve()
        self.backup_dir = Path(backup_dir or self.workspace_root / "backups")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar logging
        self._setup_logging()
        
        # Estado del agente
        self.running = False
        self.stop_event = Event()
        self.last_backup_time = None
        self.backup_interval = 15 * 60  # 15 minutos en segundos
        self.backup_count = 0
        
        # Índice de backups
        self.index_file = self.backup_dir / "index.json"
        self.backup_index = self._load_index()
        
        # Archivos a excluir (opcional, para optimización)
        self.exclude_patterns = {
            '.git/objects',
            'node_modules',
            '__pycache__',
            '.pytest_cache',
            '.mypy_cache',
            '*.pyc',
            '.DS_Store',
            'backups'  # No respaldar los backups mismos
        }
        
        self.logger.info(f"Agente de Backup inicializado")
        self.logger.info(f"Workspace: {self.workspace_root}")
        self.logger.info(f"Backup dir: {self.backup_dir}")
    
    def _setup_logging(self):
        """Configura el sistema de logging"""
        log_file = self.backup_dir / "backup_agent.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _load_index(self) -> Dict:
        """Carga el índice de backups"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Error cargando índice: {e}")
        return {"backups": [], "last_backup": None}
    
    def _save_index(self):
        """Guarda el índice de backups"""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.backup_index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error guardando índice: {e}")
    
    def _should_exclude(self, file_path: Path) -> bool:
        """Verifica si un archivo debe ser excluido"""
        path_str = str(file_path.relative_to(self.workspace_root))
        for pattern in self.exclude_patterns:
            if pattern in path_str:
                return True
        return False
    
    def _get_file_hash(self, file_path: Path) -> Optional[str]:
        """Calcula el hash de un archivo"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            self.logger.warning(f"Error calculando hash de {file_path}: {e}")
            return None
    
    def _scan_workspace(self) -> Dict:
        """
        Escanea el workspace y retorna información de archivos
        
        Returns:
            Dict con información de archivos encontrados
        """
        files_info = {
            'files': [],
            'total_size': 0,
            'file_count': 0
        }
        
        try:
            for root, dirs, files in os.walk(self.workspace_root):
                # Filtrar directorios excluidos
                dirs[:] = [d for d in dirs if not self._should_exclude(Path(root) / d)]
                
                for file in files:
                    file_path = Path(root) / file
                    
                    # Verificar si debe ser excluido
                    if self._should_exclude(file_path):
                        continue
                    
                    try:
                        rel_path = file_path.relative_to(self.workspace_root)
                        stat = file_path.stat()
                        
                        file_info = {
                            'path': str(rel_path),
                            'size': stat.st_size,
                            'modified': stat.st_mtime,
                            'hash': self._get_file_hash(file_path)
                        }
                        
                        files_info['files'].append(file_info)
                        files_info['total_size'] += stat.st_size
                        files_info['file_count'] += 1
                        
                    except Exception as e:
                        self.logger.warning(f"Error procesando {file_path}: {e}")
                        continue
        
        except Exception as e:
            self.logger.error(f"Error escaneando workspace: {e}")
        
        return files_info
    
    def _create_backup(self) -> Optional[str]:
        """
        Crea un backup completo del workspace
        
        Returns:
            Ruta del backup creado o None si falla
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_path = self.backup_dir / timestamp
        backup_path.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Iniciando backup: {timestamp}")
        
        try:
            # Escanear workspace
            files_info = self._scan_workspace()
            
            # Crear estructura de directorios
            files_dir = backup_path / "files"
            config_dir = backup_path / "config"
            state_dir = backup_path / "state"
            metadata_dir = backup_path / "metadata"
            
            for dir_path in [files_dir, config_dir, state_dir, metadata_dir]:
                dir_path.mkdir(parents=True, exist_ok=True)
            
            # Copiar archivos
            copied_files = 0
            skipped_files = 0
            errors = []
            
            for file_info in files_info['files']:
                source = self.workspace_root / file_info['path']
                dest = files_dir / file_info['path']
                
                try:
                    # Crear directorios necesarios
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copiar archivo
                    shutil.copy2(source, dest)
                    copied_files += 1
                    
                except PermissionError:
                    skipped_files += 1
                    errors.append(f"Permiso denegado: {file_info['path']}")
                except Exception as e:
                    skipped_files += 1
                    errors.append(f"Error copiando {file_info['path']}: {e}")
            
            # Guardar metadata
            metadata = {
                'timestamp': timestamp,
                'workspace_root': str(self.workspace_root),
                'backup_time': datetime.now().isoformat(),
                'file_count': files_info['file_count'],
                'copied_files': copied_files,
                'skipped_files': skipped_files,
                'total_size': files_info['total_size'],
                'errors': errors,
                'files': files_info['files']
            }
            
            metadata_file = metadata_dir / "manifest.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            # Guardar información de backup
            backup_info = {
                'timestamp': timestamp,
                'backup_path': str(backup_path),
                'file_count': copied_files,
                'total_size': files_info['total_size'],
                'status': 'success' if skipped_files == 0 else 'partial'
            }
            
            backup_info_file = backup_path / "backup_info.txt"
            with open(backup_info_file, 'w', encoding='utf-8') as f:
                f.write(f"Backup Information\n")
                f.write(f"{'='*50}\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"Workspace: {self.workspace_root}\n")
                f.write(f"Files Copied: {copied_files}\n")
                f.write(f"Files Skipped: {skipped_files}\n")
                f.write(f"Total Size: {files_info['total_size'] / 1024 / 1024:.2f} MB\n")
                f.write(f"Status: {backup_info['status']}\n")
                if errors:
                    f.write(f"\nErrors:\n")
                    for error in errors:
                        f.write(f"  - {error}\n")
            
            # Actualizar índice
            self.backup_index['backups'].append(backup_info)
            self.backup_index['last_backup'] = timestamp
            self._save_index()
            
            # Crear symlink a latest (si es posible)
            latest_link = self.backup_dir / "latest"
            try:
                if latest_link.exists():
                    latest_link.unlink()
                latest_link.symlink_to(timestamp)
            except Exception:
                pass  # Symlinks no disponibles en Windows
            
            self.backup_count += 1
            self.last_backup_time = datetime.now()
            
            self.logger.info(
                f"Backup completado: {copied_files} archivos copiados, "
                f"{skipped_files} omitidos, tamaño: {files_info['total_size'] / 1024 / 1024:.2f} MB"
            )
            
            return str(backup_path)
            
        except Exception as e:
            self.logger.error(f"Error creando backup: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return None
    
    def _backup_cycle(self):
        """Ejecuta un ciclo de backup"""
        try:
            backup_path = self._create_backup()
            if backup_path:
                self.logger.info(f"Backup exitoso: {backup_path}")
            else:
                self.logger.warning("Backup falló, pero continuando...")
        except Exception as e:
            self.logger.error(f"Error en ciclo de backup: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
    
    def _backup_loop(self):
        """Loop principal de backup que se ejecuta cada 15 minutos"""
        self.logger.info("Iniciando loop de backup (cada 15 minutos)")
        
        # Realizar backup inicial
        self._backup_cycle()
        
        # Loop principal
        while not self.stop_event.is_set():
            # Esperar 15 minutos
            if self.stop_event.wait(self.backup_interval):
                break  # Se recibió señal de parada
            
            # Ejecutar backup
            self._backup_cycle()
    
    def start(self):
        """Inicia el agente de backup"""
        if self.running:
            self.logger.warning("El agente ya está corriendo")
            return
        
        self.running = True
        self.stop_event.clear()
        
        self.logger.info("="*60)
        self.logger.info("AGENTE DE BACKUP AUTOMÁTICO INICIADO")
        self.logger.info(f"Workspace: {self.workspace_root}")
        self.logger.info(f"Backup cada: {self.backup_interval / 60} minutos")
        self.logger.info("="*60)
        
        # Iniciar thread de backup
        self.backup_thread = Thread(target=self._backup_loop, daemon=True)
        self.backup_thread.start()
        
        # Manejar señales para parada limpia
        def signal_handler(sig, frame):
            self.logger.info("Recibida señal de parada, deteniendo agente...")
            self.stop()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def stop(self):
        """Detiene el agente de backup"""
        if not self.running:
            return
        
        self.logger.info("Deteniendo agente de backup...")
        self.running = False
        self.stop_event.set()
        
        # Realizar backup final antes de salir
        self.logger.info("Realizando backup final...")
        self._backup_cycle()
        
        if hasattr(self, 'backup_thread'):
            self.backup_thread.join(timeout=5)
        
        self.logger.info(f"Agente detenido. Total de backups: {self.backup_count}")
    
    def get_status(self) -> Dict:
        """Retorna el estado actual del agente"""
        next_backup = None
        if self.last_backup_time:
            next_backup_time = self.last_backup_time.timestamp() + self.backup_interval
            next_backup = datetime.fromtimestamp(next_backup_time).isoformat()
        
        return {
            'running': self.running,
            'workspace_root': str(self.workspace_root),
            'backup_dir': str(self.backup_dir),
            'backup_interval_minutes': self.backup_interval / 60,
            'backup_count': self.backup_count,
            'last_backup': self.last_backup_time.isoformat() if self.last_backup_time else None,
            'next_backup': next_backup
        }


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Agente de Backup Automático de Workspace"
    )
    parser.add_argument(
        '--workspace',
        type=str,
        help='Ruta del workspace (por defecto: directorio actual)'
    )
    parser.add_argument(
        '--backup-dir',
        type=str,
        help='Directorio de backups (por defecto: ./backups)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=15,
        help='Intervalo de backup en minutos (por defecto: 15)'
    )
    
    args = parser.parse_args()
    
    # Crear agente
    agent = WorkspaceBackupAgent(
        workspace_root=args.workspace,
        backup_dir=args.backup_dir
    )
    
    if args.interval != 15:
        agent.backup_interval = args.interval * 60
        agent.logger.info(f"Intervalo personalizado: {args.interval} minutos")
    
    # Iniciar agente
    try:
        agent.start()
        
        # Mantener el proceso corriendo
        print("\n" + "="*60)
        print("AGENTE DE BACKUP CORRIENDO")
        print("="*60)
        print(f"Workspace: {agent.workspace_root}")
        print(f"Backup cada: {agent.backup_interval / 60} minutos")
        print(f"Backups guardados en: {agent.backup_dir}")
        print("\nPresiona Ctrl+C para detener el agente")
        print("="*60 + "\n")
        
        # Mantener proceso vivo
        while agent.running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nDeteniendo agente...")
        agent.stop()
        print("Agente detenido. ¡Hasta luego!")
    except Exception as e:
        agent.logger.error(f"Error fatal: {e}")
        import traceback
        agent.logger.error(traceback.format_exc())
        agent.stop()
        sys.exit(1)


if __name__ == "__main__":
    main()

