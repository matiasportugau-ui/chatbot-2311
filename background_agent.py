#!/usr/bin/env python3
"""
Agente de Fondo - Sistema BMC Uruguay
Ejecuta tareas automáticas en segundo plano para mantener el chatbot actualizado
"""

import logging
import sys
import time
from datetime import datetime

import schedule

from mapeador_productos_web import MapeadorProductosWeb
from sistema_cotizaciones import SistemaCotizacionesBMC

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("background_agent.log"), logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger("BackgroundAgent")


class BackgroundAgent:
    """Agente que ejecuta tareas automáticas en segundo plano"""

    def __init__(self):
        self.mapeador = None
        self.sistema = None
        self.ultima_actualizacion = None
        self.ejecutando = False

    def inicializar(self):
        """Inicializa los componentes del agente"""
        try:
            logger.info("Inicializando Background Agent...")
            self.mapeador = MapeadorProductosWeb()
            self.sistema = SistemaCotizacionesBMC()
            logger.info("Componentes inicializados correctamente")
            return True
        except Exception as e:
            logger.error(f"Error inicializando agente: {e}")
            return False

    def actualizar_productos(self):
        """Actualiza productos desde la web"""
        try:
            logger.info("Iniciando actualización de productos...")
            productos_mapeados = self.mapeador.mapear_todos_los_productos()

            if productos_mapeados:
                # Actualizar matriz de precios
                self.mapeador.actualizar_matriz_precios_con_enlaces("matriz_precios.json")

                # Sincronizar con sistema de cotizaciones
                self.sistema.actualizar_precios_desde_web(forzar=True)

                self.ultima_actualizacion = datetime.now()
                logger.info(f"Productos actualizados: {len(productos_mapeados)} productos")
                return True
            else:
                logger.warning("No se pudieron mapear productos")
                return False
        except Exception as e:
            logger.error(f"Error actualizando productos: {e}")
            return False

    def sincronizar_precios(self):
        """Sincroniza precios desde la web"""
        try:
            logger.info("Sincronizando precios...")
            resultado = self.sistema.actualizar_precios_desde_web(forzar=True)
            if resultado:
                logger.info("Precios sincronizados correctamente")
            else:
                logger.warning("No se pudieron sincronizar precios")
            return resultado
        except Exception as e:
            logger.error(f"Error sincronizando precios: {e}")
            return False

    def ejecutar_tareas_programadas(self):
        """Ejecuta las tareas programadas"""
        while self.ejecutando:
            schedule.run_pending()
            time.sleep(60)  # Verificar cada minuto

    def iniciar(self):
        """Inicia el agente de fondo"""
        if not self.inicializar():
            logger.error("No se pudo inicializar el agente")
            return False

        self.ejecutando = True

        # Programar tareas
        # Actualizar productos cada 6 horas
        schedule.every(6).hours.do(self.actualizar_productos)

        # Sincronizar precios cada 2 horas
        schedule.every(2).hours.do(self.sincronizar_precios)

        # Ejecutar actualización inicial
        logger.info("Ejecutando actualización inicial...")
        self.actualizar_productos()

        logger.info("Background Agent iniciado correctamente")
        logger.info("Tareas programadas:")
        logger.info("  - Actualización de productos: cada 6 horas")
        logger.info("  - Sincronización de precios: cada 2 horas")

        # Ejecutar tareas programadas
        try:
            self.ejecutar_tareas_programadas()
        except KeyboardInterrupt:
            logger.info("Deteniendo Background Agent...")
            self.detener()

    def detener(self):
        """Detiene el agente"""
        self.ejecutando = False
        schedule.clear()
        logger.info("Background Agent detenido")


def main():
    """Función principal"""
    print("=" * 70)
    print("🤖 BACKGROUND AGENT - BMC URUGUAY")
    print("=" * 70)
    print("El agente se ejecutará en segundo plano y actualizará")
    print("automáticamente los productos y precios desde la web.")
    print("Presiona Ctrl+C para detener.")
    print("=" * 70)

    agente = BackgroundAgent()

    try:
        agente.iniciar()
    except KeyboardInterrupt:
        print("\n\nDeteniendo agente...")
        agente.detener()
        print("Agente detenido correctamente.")


if __name__ == "__main__":
    main()
