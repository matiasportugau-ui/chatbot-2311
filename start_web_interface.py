#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para iniciar la interfaz web local del chatbot BMC
Inicia el servidor API y abre la interfaz web en el navegador
"""

import os
import sys
import time
import webbrowser
import threading
import subprocess
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socket

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_colored(message, color=Colors.RESET):
    """Imprime mensaje con color"""
    print(f"{color}{message}{Colors.RESET}")

def find_free_port(start_port=8080):
    """Encuentra un puerto libre"""
    for port in range(start_port, start_port + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    return None

def check_api_running(port=8000):
    """Verifica si la API está corriendo"""
    try:
        import requests
        response = requests.get(f"http://localhost:{port}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def start_api_server():
    """Inicia el servidor API FastAPI"""
    print_colored("\n🚀 Iniciando servidor API...", Colors.BLUE)
    
    # Verificar si ya está corriendo
    if check_api_running():
        print_colored("✅ API ya está corriendo en http://localhost:8000", Colors.GREEN)
        return True
    
    # Iniciar API en subproceso
    try:
        api_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=Path(__file__).parent
        )
        
        # Esperar a que la API esté lista
        print_colored("⏳ Esperando que la API esté lista...", Colors.YELLOW)
        for i in range(30):  # Esperar hasta 30 segundos
            time.sleep(1)
            if check_api_running():
                print_colored("✅ API iniciada correctamente en http://localhost:8000", Colors.GREEN)
                return True
            if i % 5 == 0:
                print_colored(f"   Intentando conectar... ({i+1}/30)", Colors.YELLOW)
        
        print_colored("⚠️  No se pudo verificar que la API esté corriendo", Colors.YELLOW)
        print_colored("   Verifica manualmente en http://localhost:8000/health", Colors.YELLOW)
        return False
        
    except Exception as e:
        print_colored(f"❌ Error al iniciar API: {e}", Colors.RED)
        print_colored("\n💡 Intenta iniciar la API manualmente:", Colors.YELLOW)
        print_colored("   python -m uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload", Colors.YELLOW)
        return False

def start_web_server(port=8080):
    """Inicia servidor HTTP para la interfaz web"""
    class CustomHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(Path(__file__).parent), **kwargs)
        
        def end_headers(self):
            # Agregar headers CORS
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            super().end_headers()
        
        def log_message(self, format, *args):
            # Silenciar logs del servidor HTTP
            pass
    
    try:
        httpd = HTTPServer(('localhost', port), CustomHandler)
        print_colored(f"✅ Servidor web iniciado en http://localhost:{port}", Colors.GREEN)
        return httpd
    except OSError as e:
        if "Address already in use" in str(e):
            print_colored(f"⚠️  Puerto {port} ya está en uso, buscando puerto alternativo...", Colors.YELLOW)
            new_port = find_free_port(8081)
            if new_port:
                httpd = HTTPServer(('localhost', new_port), CustomHandler)
                print_colored(f"✅ Servidor web iniciado en http://localhost:{new_port}", Colors.GREEN)
                return httpd, new_port
        raise

def open_browser(url, delay=2):
    """Abre el navegador después de un delay"""
    time.sleep(delay)
    try:
        webbrowser.open(url)
        print_colored(f"🌐 Navegador abierto en {url}", Colors.GREEN)
    except Exception as e:
        print_colored(f"⚠️  No se pudo abrir el navegador automáticamente: {e}", Colors.YELLOW)
        print_colored(f"   Abre manualmente: {url}", Colors.YELLOW)

def main():
    """Función principal"""
    print_colored("\n" + "="*60, Colors.BOLD)
    print_colored("🏗️  BMC Chatbot - Interfaz Web Local (BETA)", Colors.BOLD)
    print_colored("="*60 + "\n", Colors.BOLD)
    
    # Verificar que existe el archivo HTML
    html_file = Path(__file__).parent / "chat-interface.html"
    if not html_file.exists():
        print_colored(f"❌ No se encontró el archivo: {html_file}", Colors.RED)
        print_colored("   Asegúrate de que chat-interface.html existe en el directorio", Colors.YELLOW)
        return 1
    
    # Verificar variables de entorno
    print_colored("🔍 Verificando configuración...", Colors.BLUE)
    
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print_colored("⚠️  Variables de entorno faltantes:", Colors.YELLOW)
        for var in missing_vars:
            print_colored(f"   - {var}", Colors.YELLOW)
        print_colored("\n💡 Crea un archivo .env con las variables necesarias", Colors.YELLOW)
        print_colored("   O exporta las variables antes de ejecutar este script", Colors.YELLOW)
        print_colored("\n   Ejemplo:", Colors.YELLOW)
        print_colored("   export OPENAI_API_KEY='tu-api-key'", Colors.YELLOW)
    
    # Iniciar API
    api_ok = start_api_server()
    
    if not api_ok:
        print_colored("\n⚠️  Continuando sin verificar API...", Colors.YELLOW)
        print_colored("   Asegúrate de iniciar la API manualmente si es necesario", Colors.YELLOW)
    
    # Iniciar servidor web
    print_colored("\n🌐 Iniciando servidor web...", Colors.BLUE)
    try:
        result = start_web_server()
        if isinstance(result, tuple):
            httpd, port = result
        else:
            httpd = result
            port = 8080
        
        web_url = f"http://localhost:{port}/chat-interface.html"
        
        # Abrir navegador en thread separado
        browser_thread = threading.Thread(target=open_browser, args=(web_url,))
        browser_thread.daemon = True
        browser_thread.start()
        
        print_colored("\n" + "="*60, Colors.BOLD)
        print_colored("✅ Sistema iniciado correctamente!", Colors.GREEN)
        print_colored("="*60, Colors.BOLD)
        print_colored(f"\n📱 Interfaz web: {web_url}", Colors.BLUE)
        print_colored(f"🔌 API: http://localhost:8000", Colors.BLUE)
        print_colored(f"❤️  Health check: http://localhost:8000/health", Colors.BLUE)
        print_colored("\n💡 Presiona Ctrl+C para detener el servidor", Colors.YELLOW)
        print_colored("="*60 + "\n", Colors.BOLD)
        
        # Mantener servidor corriendo
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print_colored("\n\n🛑 Deteniendo servidor...", Colors.YELLOW)
            httpd.shutdown()
            print_colored("✅ Servidor detenido", Colors.GREEN)
            return 0
            
    except Exception as e:
        print_colored(f"\n❌ Error al iniciar servidor web: {e}", Colors.RED)
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print_colored("\n\n👋 Hasta luego!", Colors.BLUE)
        sys.exit(0)

