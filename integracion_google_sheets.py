#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integración Google Sheets BMC Uruguay
Sincronización automática con Google Sheets "Administrador de Cotizaciones II"
"""

import json
import datetime
import os
import gspread
from google.oauth2.service_account import Credentials
from typing import Dict, List, Any, Optional
# import pandas as pd  # Comentado por problemas de espacio

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv
    # Intentar cargar desde .env.local primero, luego .env
    env_cargado = False
    if os.path.exists('.env.local'):
        load_dotenv('.env.local', override=True)
        env_cargado = True
        print("[INFO] Variables de entorno cargadas desde .env.local")
    elif os.path.exists('.env'):
        load_dotenv('.env', override=True)
        env_cargado = True
        print("[INFO] Variables de entorno cargadas desde .env")
    else:
        # Intentar cargar sin especificar archivo (busca .env en la raíz)
        result = load_dotenv()
        if result:
            env_cargado = True
            print("[INFO] Variables de entorno cargadas desde archivo .env encontrado")
except ImportError:
    print("[WARNING] python-dotenv no instalado. Instala con: pip install python-dotenv")
    print("[INFO] Las variables de entorno deben estar configuradas en el sistema")

from ia_conversacional_integrada import IAConversacionalIntegrada
from base_conocimiento_dinamica import InteraccionCliente


class IntegracionGoogleSheets:
    """Integración con Google Sheets"""
    
    def __init__(self, ia_conversacional: Optional[IAConversacionalIntegrada] = None):
        self.ia = ia_conversacional
        # Leer Sheet ID de variable de entorno o usar el por defecto
        self.sheet_id = os.getenv('GOOGLE_SHEET_ID', '1-c834pOUNnUWn7Q-Bc4kDHJGCQo0LKI05dXaLgqcXgI')
        self.credenciales = None
        self.cliente_gspread = None
        self.hoja_principal = None
        self.hoja_enviados = None
        self.hoja_confirmados = None
        self.conectado = False
        
        # Configurar credenciales
        self.configurar_credenciales()
    
    def configurar_credenciales(self):
        """Configura las credenciales de Google Sheets desde variables de entorno o archivo"""
        try:
            scope = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Intentar leer desde variables de entorno (producción)
            service_account_email = os.getenv('GOOGLE_SERVICE_ACCOUNT_EMAIL')
            private_key = os.getenv('GOOGLE_PRIVATE_KEY')
            
            if service_account_email and private_key:
                # Usar credenciales desde variables de entorno
                try:
                    # Limpiar la clave privada (remover \n literales)
                    private_key_clean = private_key.replace('\\n', '\n')
                    
                    creds_dict = {
                        "type": "service_account",
                        "project_id": service_account_email.split('@')[1].split('.')[0] if '@' in service_account_email else "bmc-project",
                        "private_key_id": "",
                        "private_key": private_key_clean,
                        "client_email": service_account_email,
                        "client_id": "",
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                        "client_x509_cert_url": ""
                    }
                    
                    self.credenciales = Credentials.from_service_account_info(creds_dict, scopes=scope)
                    print("[OK] Credenciales de Google Sheets configuradas desde variables de entorno")
                    return
                except Exception as e:
                    print(f"[WARNING] Error usando credenciales de variables de entorno: {e}")
            
            # Intentar leer desde archivo JSON (desarrollo local)
            archivos_credenciales = ['credenciales.json', 'google-credentials.json', 'service-account.json']
            for archivo in archivos_credenciales:
                if os.path.exists(archivo):
                    try:
                        self.credenciales = Credentials.from_service_account_file(archivo, scopes=scope)
                        print(f"[OK] Credenciales de Google Sheets cargadas desde {archivo}")
                        return
                    except Exception as e:
                        print(f"[WARNING] Error leyendo {archivo}: {e}")
                        continue
            
            # Si no hay credenciales, usar modo simulado
            print("[WARNING] No se encontraron credenciales de Google Sheets")
            print("[INFO] Usando modo simulado. Para produccion:")
            print("[INFO] 1. Configurar GOOGLE_SERVICE_ACCOUNT_EMAIL y GOOGLE_PRIVATE_KEY en variables de entorno")
            print("[INFO] 2. O colocar archivo credenciales.json en la raiz del proyecto")
            self.credenciales = None
            
        except Exception as e:
            print(f"[ERROR] Error configurando credenciales: {e}")
            print("[INFO] Usando modo simulado")
            self.credenciales = None
    
    def _obtener_hoja(self, spreadsheet, nombre_buscado: str):
        """Busca una hoja ignorando espacios extra al inicio o final"""
        try:
            return spreadsheet.worksheet(nombre_buscado)
        except gspread.exceptions.WorksheetNotFound:
            # Intentar buscar normalizando nombres
            for ws in spreadsheet.worksheets():
                if ws.title.strip() == nombre_buscado.strip():
                    print(f"[INFO] Se encontro '{ws.title}' buscando '{nombre_buscado}'")
                    return ws
            raise

    def conectar_google_sheets(self):
        """Conecta con Google Sheets"""
        if not self.credenciales:
            print("[WARNING] Credenciales no configuradas, usando modo simulado")
            self.conectado = False
            return False
        
        try:
            self.cliente_gspread = gspread.authorize(self.credenciales)
            spreadsheet = self.cliente_gspread.open_by_key(self.sheet_id)
            
            # Usar metodo robusto para encontrar hojas
            self.hoja_principal = self._obtener_hoja(spreadsheet, "Admin.")
            self.hoja_enviados = self._obtener_hoja(spreadsheet, "Enviados")
            self.hoja_confirmados = self._obtener_hoja(spreadsheet, "Confirmado")
            
            self.conectado = True
            print("[OK] Conectado a Google Sheets exitosamente")
            return True
            
        except Exception as e:
            print(f"[ERROR] Error conectando a Google Sheets: {e}")
            self.conectado = False
            return False
    
    def leer_cotizaciones_pendientes(self) -> List[Dict]:
        """Lee cotizaciones pendientes de la pestaña Admin."""
        if not self.hoja_principal:
            return self.simular_datos_cotizaciones()
        
        try:
            # Leer datos de la hoja
            datos = self.hoja_principal.get_all_records()
            
            # Filtrar solo cotizaciones pendientes
            pendientes = [
                fila for fila in datos 
                if fila.get('Estado', '').lower() in ['pendiente', 'adjunto', 'listo']
            ]
            
            print(f"[INFO] Leidas {len(pendientes)} cotizaciones pendientes")
            return pendientes
            
        except Exception as e:
            print(f"[ERROR] Error leyendo cotizaciones: {e}")
            return []
    
    def simular_datos_cotizaciones(self) -> List[Dict]:
        """Simula datos de cotizaciones para demo"""
        return [
            {
                "Arg": "RA001",
                "Estado": "Pendiente",
                "Fecha": "24-10",
                "Cliente": "Juan Pérez",
                "Orig.": "WA",
                "Telefono-Contacto": "099123456",
                "Direccion / Zona": "Montevideo",
                "Consulta": "Isodec 100mm / 8 p de 10 m / paneles blancos / completo + flete"
            },
            {
                "Arg": "MO002",
                "Estado": "Adjunto",
                "Fecha": "24-10",
                "Cliente": "María García",
                "Orig.": "EM",
                "Telefono-Contacto": "099765432",
                "Direccion / Zona": "Maldonado",
                "Consulta": "Poliestireno 75mm / techo de 50 m2 / gris / sin flete"
            },
            {
                "Arg": "TNT003",
                "Estado": "Listo",
                "Fecha": "23-10",
                "Cliente": "Carlos López",
                "Orig.": "LO",
                "Telefono-Contacto": "099888999",
                "Direccion / Zona": "Rivera",
                "Consulta": "Lana de roca 100mm / galpón 9m x 7m x 5m / instalación completa"
            }
        ]
    
    def procesar_consulta_cotizacion(self, consulta: str) -> Dict[str, Any]:
        """Procesa una consulta de cotización usando IA"""
        try:
            # Usar IA para analizar la consulta
            respuesta_ia = self.ia.procesar_mensaje(consulta, "sistema_sheets")
            
            # Extraer información estructurada
            informacion_extraida = self.extraer_informacion_consulta(consulta)
            
            return {
                "consulta_original": consulta,
                "respuesta_ia": respuesta_ia.mensaje,
                "informacion_extraida": informacion_extraida,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"[ERROR] Error procesando consulta: {e}")
            return {"error": str(e)}
    
    def extraer_informacion_consulta(self, consulta: str) -> Dict[str, Any]:
        """Extrae información estructurada de una consulta"""
        consulta_lower = consulta.lower()
        
        # Extraer producto
        productos = ["isodec", "poliestireno", "lana de roca", "isoroof", "isopanel"]
        producto_encontrado = None
        for producto in productos:
            if producto in consulta_lower:
                producto_encontrado = producto
                break
        
        # Extraer espesor
        espesores = ["50mm", "75mm", "100mm", "125mm", "150mm", "200mm"]
        espesor_encontrado = None
        for espesor in espesores:
            if espesor in consulta_lower:
                espesor_encontrado = espesor
                break
        
        # Extraer dimensiones
        dimensiones = self.extraer_dimensiones(consulta)
        
        # Extraer servicios
        servicios = {
            "flete": "+ flete" in consulta_lower or "flete" in consulta_lower,
            "instalacion": "completo" in consulta_lower or "instalación" in consulta_lower,
            "accesorios": "accesorios" in consulta_lower
        }
        
        # Extraer color
        colores = ["blanco", "gris", "grises"]
        color_encontrado = None
        for color in colores:
            if color in consulta_lower:
                color_encontrado = color
                break
        
        return {
            "producto": producto_encontrado,
            "espesor": espesor_encontrado,
            "dimensiones": dimensiones,
            "servicios": servicios,
            "color": color_encontrado,
            "completo": "completo" in consulta_lower,
            "urgente": "urgente" in consulta_lower
        }
    
    def extraer_dimensiones(self, consulta: str) -> Dict[str, Any]:
        """Extrae dimensiones de la consulta"""
        import re
        
        # Patrones para dimensiones
        patrones = [
            r'(\d+)\s*p\s*de\s*(\d+)\s*m',  # "8 p de 10 m"
            r'techo\s*de\s*(\d+)\s*m2',     # "techo de 50 m2"
            r'galpón\s*(\d+)m\s*x\s*(\d+)m\s*x\s*(\d+)m',  # "galpón 9m x 7m x 5m"
            r'(\d+)\s*m2',                   # "50 m2"
        ]
        
        for patron in patrones:
            match = re.search(patron, consulta.lower())
            if match:
                if patron == patrones[0]:  # "8 p de 10 m"
                    return {
                        "tipo": "paneles",
                        "cantidad": int(match.group(1)),
                        "largo": int(match.group(2)),
                        "unidad": "paneles"
                    }
                elif patron == patrones[1]:  # "techo de 50 m2"
                    return {
                        "tipo": "area",
                        "area": int(match.group(1)),
                        "unidad": "m2"
                    }
                elif patron == patrones[2]:  # "galpón 9m x 7m x 5m"
                    return {
                        "tipo": "volumen",
                        "largo": int(match.group(1)),
                        "ancho": int(match.group(2)),
                        "alto": int(match.group(3)),
                        "unidad": "m"
                    }
                elif patron == patrones[3]:  # "50 m2"
                    return {
                        "tipo": "area",
                        "area": int(match.group(1)),
                        "unidad": "m2"
                    }
        
        return {"tipo": "no_especificado"}
    
    def sincronizar_cotizaciones(self):
        """Sincroniza cotizaciones entre el sistema y Google Sheets"""
        print("\n[SYNC] SINCRONIZANDO COTIZACIONES CON GOOGLE SHEETS")
        print("=" * 60)
        
        # Leer cotizaciones pendientes
        cotizaciones = self.leer_cotizaciones_pendientes()
        
        if not cotizaciones:
            print("[INFO] No hay cotizaciones para sincronizar")
            return
        
        print(f"[INFO] Procesando {len(cotizaciones)} cotizaciones...")
        
        for i, cotizacion in enumerate(cotizaciones, 1):
            print(f"\n[INFO] Cotizacion {i}: {cotizacion['Arg']}")
            print(f"   Cliente: {cotizacion['Cliente']}")
            print(f"   Estado: {cotizacion['Estado']}")
            print(f"   Consulta: {cotizacion['Consulta']}")
            
            # Procesar consulta con IA
            resultado = self.procesar_consulta_cotizacion(cotizacion['Consulta'])
            
            if 'error' not in resultado:
                print(f"   [IA] {resultado['respuesta_ia']}")
                print(f"   [INFO] Info extraida: {resultado['informacion_extraida']}")
                
                # Registrar en base de conocimiento
                self.registrar_cotizacion_sheets(cotizacion, resultado)
            else:
                print(f"   [ERROR] Error: {resultado['error']}")
    
    def registrar_cotizacion_sheets(self, cotizacion: Dict, resultado: Dict):
        """Registra una cotización de Google Sheets en la base de conocimiento"""
        try:
            interaccion = InteraccionCliente(
                id=f"sheets_{cotizacion['Arg']}",
                timestamp=datetime.datetime.now(),
                cliente_id=cotizacion['Telefono-Contacto'],
                tipo_interaccion="cotizacion_sheets",
                mensaje_cliente=cotizacion['Consulta'],
                respuesta_agente=resultado['respuesta_ia'],
                contexto={
                    "canal": "google_sheets",
                    "arg": cotizacion['Arg'],
                    "estado": cotizacion['Estado'],
                    "cliente": cotizacion['Cliente'],
                    "origen": cotizacion['Orig.'],
                    "zona": cotizacion['Direccion / Zona'],
                    "informacion_extraida": resultado['informacion_extraida']
                },
                resultado="exitoso"
            )
            
            self.ia.base_conocimiento.registrar_interaccion(interaccion)
            print(f"   [OK] Registrada en base de conocimiento")
            
        except Exception as e:
            print(f"   [ERROR] Error registrando: {e}")
    
    def generar_reporte_cotizaciones(self) -> Dict[str, Any]:
        """Genera un reporte de cotizaciones"""
        print("\n[REPORT] GENERANDO REPORTE DE COTIZACIONES")
        print("=" * 50)
        
        # Leer cotizaciones
        cotizaciones = self.leer_cotizaciones_pendientes()
        
        # Estadísticas
        total_cotizaciones = len(cotizaciones)
        por_estado = {}
        por_origen = {}
        por_zona = {}
        
        for cotizacion in cotizaciones:
            # Por estado
            estado = cotizacion.get('Estado', 'Desconocido')
            por_estado[estado] = por_estado.get(estado, 0) + 1
            
            # Por origen
            origen = cotizacion.get('Orig.', 'Desconocido')
            por_origen[origen] = por_origen.get(origen, 0) + 1
            
            # Por zona
            zona = cotizacion.get('Direccion / Zona', 'Desconocido')
            por_zona[zona] = por_zona.get(zona, 0) + 1
        
        reporte = {
            "fecha_generacion": datetime.datetime.now().isoformat(),
            "total_cotizaciones": total_cotizaciones,
            "por_estado": por_estado,
            "por_origen": por_origen,
            "por_zona": por_zona,
            "cotizaciones": cotizaciones
        }
        
        # Mostrar resumen
        print(f"[INFO] Total de cotizaciones: {total_cotizaciones}")
        print(f"[INFO] Por estado: {por_estado}")
        print(f"[INFO] Por origen: {por_origen}")
        print(f"[INFO] Por zona: {por_zona}")
        
        return reporte
    
    def exportar_reporte(self, archivo: str = "reporte_cotizaciones.json"):
        """Exporta el reporte a un archivo JSON"""
        try:
            reporte = self.generar_reporte_cotizaciones()
            
            with open(archivo, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"[OK] Reporte exportado a {archivo}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Error exportando reporte: {e}")
            return False
    
    def generar_codigo_arg(self, telefono: str, origen: str = "CH") -> str:
        """Genera un código Arg único para la cotización"""
        # Formato: {origen}{día}{hora}{últimos4dígitos}
        ahora = datetime.datetime.now()
        dia = ahora.day
        hora = ahora.hour
        ultimos_4 = telefono[-4:] if len(telefono) >= 4 else telefono.zfill(4)
        return f"{origen}{dia:02d}{hora:02d}{ultimos_4}"
    
    def guardar_cotizacion_en_sheets(self, cotizacion_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Guarda una cotización en la pestaña Admin. de Google Sheets
        
        Args:
            cotizacion_data: Diccionario con los datos de la cotización
                - cliente: nombre del cliente
                - telefono: teléfono de contacto
                - direccion: dirección o zona
                - consulta: descripción de la consulta
                - origen: origen de la cotización (CH=Chat, WA=WhatsApp, etc.)
                - estado: estado inicial (default: "Pendiente")
        
        Returns:
            Dict con resultado de la operación
        """
        if not self.conectado:
            # Intentar conectar si no está conectado
            if not self.conectar_google_sheets():
                return {
                    "exito": False,
                    "error": "No se pudo conectar a Google Sheets. Verifica las credenciales.",
                    "modo": "simulado"
                }
        
        try:
            # Preparar datos para la fila
            codigo_arg = cotizacion_data.get('arg') or self.generar_codigo_arg(
                cotizacion_data.get('telefono', '0000'),
                cotizacion_data.get('origen', 'CH')
            )
            
            estado = cotizacion_data.get('estado', 'Pendiente')
            fecha = cotizacion_data.get('fecha') or datetime.datetime.now().strftime('%d-%m')
            cliente = cotizacion_data.get('cliente', 'Cliente')
            origen = cotizacion_data.get('origen', 'CH')
            telefono = cotizacion_data.get('telefono', '')
            direccion = cotizacion_data.get('direccion', '')
            consulta = cotizacion_data.get('consulta', '')
            
            # Construir la fila según el formato del sheet
            fila = [
                codigo_arg,      # Columna A: Arg
                estado,          # Columna B: Estado
                fecha,           # Columna C: Fecha
                cliente,         # Columna D: Cliente
                origen,          # Columna E: Orig.
                telefono,        # Columna F: Telefono-Contacto
                direccion,       # Columna G: Direccion / Zona
                consulta         # Columna H: Consulta
            ]
            
            # Agregar la fila a la hoja Admin.
            self.hoja_principal.append_row(fila)
            
            resultado = {
                "exito": True,
                "codigo_arg": codigo_arg,
                "mensaje": f"✅ Cotización guardada en Google Sheets con código {codigo_arg}",
                "fila_agregada": fila
            }
            
            print(f"[OK] Cotizacion guardada en Google Sheets: {codigo_arg}")
            return resultado
            
        except Exception as e:
            error_msg = f"Error guardando cotizacion en Google Sheets: {str(e)}"
            print(f"[ERROR] {error_msg}")
            return {
                "exito": False,
                "error": error_msg,
                "modo": "error"
            }
    
    def construir_consulta_cotizacion(self, datos_cliente: Dict, datos_especificaciones: Dict) -> str:
        """Construye una descripción de consulta a partir de los datos de la cotización"""
        producto = datos_especificaciones.get('producto', '').upper()
        espesor = datos_especificaciones.get('espesor', '')
        largo = datos_especificaciones.get('largo', '')
        ancho = datos_especificaciones.get('ancho', '')
        color = datos_especificaciones.get('color', '')
        terminacion = datos_especificaciones.get('terminacion', '')
        
        partes = []
        if producto:
            partes.append(producto)
        if espesor:
            partes.append(espesor)
        if largo and ancho:
            try:
                area = float(largo) * float(ancho)
                partes.append(f"{area} m²")
            except (ValueError, TypeError):
                # Si los valores no son numéricos válidos, omitir el área
                pass
        if color:
            partes.append(f"color {color.lower()}")
        if terminacion:
            partes.append(f"terminación {terminacion.lower()}")
        
        consulta = " / ".join(partes) if partes else "Cotización de producto de aislamiento"
        return consulta


def main():
    """Función principal para ejecutar la integración Google Sheets"""
    print("[GOOGLE SHEETS] INTEGRACION GOOGLE SHEETS BMC URUGUAY")
    print("=" * 50)
    
    # Crear IA conversacional
    ia = IAConversacionalIntegrada()
    
    # Crear integración Google Sheets
    sheets = IntegracionGoogleSheets(ia)
    
    # Conectar (modo simulado)
    sheets.conectar_google_sheets()
    
    # Sincronizar cotizaciones
    sheets.sincronizar_cotizaciones()
    
    # Generar reporte
    sheets.generar_reporte_cotizaciones()
    
    # Exportar reporte
    sheets.exportar_reporte()
    
    print("\n[OK] Integracion Google Sheets completada")
    print("Para usar en producción:")
    print("1. Configurar credenciales de Google Service Account")
    print("2. Compartir el Sheet con el email del Service Account")
    print("3. Ejecutar sincronización automática")


if __name__ == "__main__":
    main()
