#!/usr/bin/env python3
"""
Integración Google Sheets BMC Uruguay
Sincronización automática con Google Sheets "Administrador de Cotizaciones II"
"""

import datetime
import json
from typing import Any

import gspread

from base_conocimiento_dinamica import InteraccionCliente

# import pandas as pd  # Comentado por problemas de espacio
from ia_conversacional_integrada import IAConversacionalIntegrada


class IntegracionGoogleSheets:
    """Integración con Google Sheets"""

    def __init__(self, ia_conversacional: IAConversacionalIntegrada):
        self.ia = ia_conversacional
        self.sheet_id = "1bs467N7FbLSHI7LpNor3wqrPZC9snqPphft8cEPHHl0"  # ID del sheet real
        self.credenciales = None
        self.cliente_gspread = None
        self.hoja_principal = None
        self.hoja_enviados = None
        self.hoja_confirmados = None

        # Configurar credenciales
        self.configurar_credenciales()

    def configurar_credenciales(self):
        """Configura las credenciales de Google Sheets"""
        try:
            # Crear credenciales (necesita archivo JSON de service account)
            scope = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ]

            # En producción, usar archivo de credenciales real
            # creds = Credentials.from_service_account_file('credenciales.json', scopes=scope)

            # Para demo, usar credenciales simuladas
            print("⚠️  Usando credenciales simuladas para demo")
            print("   En producción, configurar credenciales reales de Google Service Account")

            self.credenciales = None  # Simulado
            self.cliente_gspread = None  # Simulado

        except Exception as e:
            print(f"❌ Error configurando credenciales: {e}")
            print("   Configurar credenciales reales para usar en producción")

    def conectar_google_sheets(self):
        """Conecta con Google Sheets"""
        if not self.credenciales:
            print("⚠️  Credenciales no configuradas, usando modo simulado")
            return False

        try:
            self.cliente_gspread = gspread.authorize(self.credenciales)
            self.hoja_principal = self.cliente_gspread.open_by_key(self.sheet_id).worksheet(
                "Admin."
            )
            self.hoja_enviados = self.cliente_gspread.open_by_key(self.sheet_id).worksheet(
                "Enviados"
            )
            self.hoja_confirmados = self.cliente_gspread.open_by_key(self.sheet_id).worksheet(
                "Confirmado"
            )

            print("✅ Conectado a Google Sheets exitosamente")
            return True

        except Exception as e:
            print(f"❌ Error conectando a Google Sheets: {e}")
            return False

    def leer_cotizaciones_pendientes(self) -> list[dict]:
        """Lee cotizaciones pendientes de la pestaña Admin."""
        if not self.hoja_principal:
            return self.simular_datos_cotizaciones()

        try:
            # Leer datos de la hoja
            datos = self.hoja_principal.get_all_records()

            # Filtrar solo cotizaciones pendientes
            pendientes = [
                fila
                for fila in datos
                if fila.get("Estado", "").lower() in ["pendiente", "adjunto", "listo"]
            ]

            print(f"📊 Leídas {len(pendientes)} cotizaciones pendientes")
            return pendientes

        except Exception as e:
            print(f"❌ Error leyendo cotizaciones: {e}")
            return []

    def simular_datos_cotizaciones(self) -> list[dict]:
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
                "Consulta": "Isodec 100mm / 8 p de 10 m / paneles blancos / completo + flete",
            },
            {
                "Arg": "MO002",
                "Estado": "Adjunto",
                "Fecha": "24-10",
                "Cliente": "María García",
                "Orig.": "EM",
                "Telefono-Contacto": "099765432",
                "Direccion / Zona": "Maldonado",
                "Consulta": "Poliestireno 75mm / techo de 50 m2 / gris / sin flete",
            },
            {
                "Arg": "TNT003",
                "Estado": "Listo",
                "Fecha": "23-10",
                "Cliente": "Carlos López",
                "Orig.": "LO",
                "Telefono-Contacto": "099888999",
                "Direccion / Zona": "Rivera",
                "Consulta": "Lana de roca 100mm / galpón 9m x 7m x 5m / instalación completa",
            },
        ]

    def procesar_consulta_cotizacion(self, consulta: str) -> dict[str, Any]:
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
                "timestamp": datetime.datetime.now().isoformat(),
            }

        except Exception as e:
            print(f"❌ Error procesando consulta: {e}")
            return {"error": str(e)}

    def extraer_informacion_consulta(self, consulta: str) -> dict[str, Any]:
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
            "accesorios": "accesorios" in consulta_lower,
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
            "urgente": "urgente" in consulta_lower,
        }

    def extraer_dimensiones(self, consulta: str) -> dict[str, Any]:
        """Extrae dimensiones de la consulta"""
        import re

        # Patrones para dimensiones
        patrones = [
            r"(\d+)\s*p\s*de\s*(\d+)\s*m",  # "8 p de 10 m"
            r"techo\s*de\s*(\d+)\s*m2",  # "techo de 50 m2"
            r"galpón\s*(\d+)m\s*x\s*(\d+)m\s*x\s*(\d+)m",  # "galpón 9m x 7m x 5m"
            r"(\d+)\s*m2",  # "50 m2"
        ]

        for patron in patrones:
            match = re.search(patron, consulta.lower())
            if match:
                if patron == patrones[0]:  # "8 p de 10 m"
                    return {
                        "tipo": "paneles",
                        "cantidad": int(match.group(1)),
                        "largo": int(match.group(2)),
                        "unidad": "paneles",
                    }
                elif patron == patrones[1]:  # "techo de 50 m2"
                    return {"tipo": "area", "area": int(match.group(1)), "unidad": "m2"}
                elif patron == patrones[2]:  # "galpón 9m x 7m x 5m"
                    return {
                        "tipo": "volumen",
                        "largo": int(match.group(1)),
                        "ancho": int(match.group(2)),
                        "alto": int(match.group(3)),
                        "unidad": "m",
                    }
                elif patron == patrones[3]:  # "50 m2"
                    return {"tipo": "area", "area": int(match.group(1)), "unidad": "m2"}

        return {"tipo": "no_especificado"}

    def sincronizar_cotizaciones(self):
        """Sincroniza cotizaciones entre el sistema y Google Sheets"""
        print("\n🔄 SINCRONIZANDO COTIZACIONES CON GOOGLE SHEETS")
        print("=" * 60)

        # Leer cotizaciones pendientes
        cotizaciones = self.leer_cotizaciones_pendientes()

        if not cotizaciones:
            print("No hay cotizaciones para sincronizar")
            return

        print(f"📊 Procesando {len(cotizaciones)} cotizaciones...")

        for i, cotizacion in enumerate(cotizaciones, 1):
            print(f"\n📋 Cotización {i}: {cotizacion['Arg']}")
            print(f"   Cliente: {cotizacion['Cliente']}")
            print(f"   Estado: {cotizacion['Estado']}")
            print(f"   Consulta: {cotizacion['Consulta']}")

            # Procesar consulta con IA
            resultado = self.procesar_consulta_cotizacion(cotizacion["Consulta"])

            if "error" not in resultado:
                print(f"   🤖 IA: {resultado['respuesta_ia']}")
                print(f"   📊 Info extraída: {resultado['informacion_extraida']}")

                # Registrar en base de conocimiento
                self.registrar_cotizacion_sheets(cotizacion, resultado)
            else:
                print(f"   ❌ Error: {resultado['error']}")

    def registrar_cotizacion_sheets(self, cotizacion: dict, resultado: dict):
        """Registra una cotización de Google Sheets en la base de conocimiento"""
        try:
            interaccion = InteraccionCliente(
                id=f"sheets_{cotizacion['Arg']}",
                timestamp=datetime.datetime.now(),
                cliente_id=cotizacion["Telefono-Contacto"],
                tipo_interaccion="cotizacion_sheets",
                mensaje_cliente=cotizacion["Consulta"],
                respuesta_agente=resultado["respuesta_ia"],
                contexto={
                    "canal": "google_sheets",
                    "arg": cotizacion["Arg"],
                    "estado": cotizacion["Estado"],
                    "cliente": cotizacion["Cliente"],
                    "origen": cotizacion["Orig."],
                    "zona": cotizacion["Direccion / Zona"],
                    "informacion_extraida": resultado["informacion_extraida"],
                },
                resultado="exitoso",
            )

            self.ia.base_conocimiento.registrar_interaccion(interaccion)
            print("   ✅ Registrada en base de conocimiento")

        except Exception as e:
            print(f"   ❌ Error registrando: {e}")

    def generar_reporte_cotizaciones(self) -> dict[str, Any]:
        """Genera un reporte de cotizaciones"""
        print("\n📊 GENERANDO REPORTE DE COTIZACIONES")
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
            estado = cotizacion.get("Estado", "Desconocido")
            por_estado[estado] = por_estado.get(estado, 0) + 1

            # Por origen
            origen = cotizacion.get("Orig.", "Desconocido")
            por_origen[origen] = por_origen.get(origen, 0) + 1

            # Por zona
            zona = cotizacion.get("Direccion / Zona", "Desconocido")
            por_zona[zona] = por_zona.get(zona, 0) + 1

        reporte = {
            "fecha_generacion": datetime.datetime.now().isoformat(),
            "total_cotizaciones": total_cotizaciones,
            "por_estado": por_estado,
            "por_origen": por_origen,
            "por_zona": por_zona,
            "cotizaciones": cotizaciones,
        }

        # Mostrar resumen
        print(f"📈 Total de cotizaciones: {total_cotizaciones}")
        print(f"📊 Por estado: {por_estado}")
        print(f"📱 Por origen: {por_origen}")
        print(f"📍 Por zona: {por_zona}")

        return reporte

    def exportar_reporte(self, archivo: str = "reporte_cotizaciones.json"):
        """Exporta el reporte a un archivo JSON"""
        try:
            reporte = self.generar_reporte_cotizaciones()

            with open(archivo, "w", encoding="utf-8") as f:
                json.dump(reporte, f, ensure_ascii=False, indent=2, default=str)

            print(f"✅ Reporte exportado a {archivo}")
            return True

        except Exception as e:
            print(f"❌ Error exportando reporte: {e}")
            return False


def main():
    """Función principal para ejecutar la integración Google Sheets"""
    print("📊 INTEGRACIÓN GOOGLE SHEETS BMC URUGUAY")
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

    print("\n✅ Integración Google Sheets completada")
    print("Para usar en producción:")
    print("1. Configurar credenciales de Google Service Account")
    print("2. Compartir el Sheet con el email del Service Account")
    print("3. Ejecutar sincronización automática")


if __name__ == "__main__":
    main()
