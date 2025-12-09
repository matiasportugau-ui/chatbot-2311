#!/usr/bin/env python3
"""
Orchestrator script for massive data ingestion and processing.
Handles multiple data sources, cleaning, and formatting for language adaptation.
"""

import os
import sys
import argparse
import glob
from pathlib import Path
from extraer_datos_entrenamiento import ExtractorDatosEntrenamiento

def procesar_datos_masivos(input_dir: str, output_file: str, file_pattern: str = "*.json"):
    """
    Procesa masivamente archivos de un directorio.
    """
    extractor = ExtractorDatosEntrenamiento()
    all_data = []
    
    input_path = Path(input_dir)
    if not input_path.exists():
        print(f"❌ Directorio no encontrado: {input_dir}")
        return

    files = list(input_path.glob(file_pattern))
    print(f"📂 Encontrados {len(files)} archivos para procesar en {input_dir}")
    
    for file_path in files:
        print(f"Processing: {file_path.name}")
        # Detectar tipo por nombre o contenido (simplificado por ahora)
        if "whatsapp" in file_path.name.lower():
            data = extractor.extraer_whatsapp_archivo(str(file_path), streaming=True)
            all_data.extend(data)
        elif "mercado" in file_path.name.lower() or "ml" in file_path.name.lower() or "conocimiento" in file_path.name.lower():
            # Use the robust parser that handles 'interacciones' and 'mensaje_cliente'
            data = extractor.extraer_mercado_libre_archivo(str(file_path))
            all_data.extend(data)
        else:
             # Default try as whatsapp general json
             data = extractor.extraer_whatsapp_archivo(str(file_path), streaming=True)
             all_data.extend(data)

    if all_data:
        extractor.guardar_para_entrenamiento(all_data, output_file)
        extractor.generar_resumen(all_data)
        print(f"✅ Procesamiento masivo completado. Salida: {output_file}")
    else:
        print("⚠️ No se procesaron datos.")

def main():
    parser = argparse.ArgumentParser(description="Procesamiento Masivo de Datos")
    parser.add_argument("--input-dir", required=True, help="Directorio con archivos JSON")
    parser.add_argument("--output", default="data/training/sales_adaptation_v1.json", help="Archivo de salida")
    args = parser.parse_args()
    
    procesar_datos_masivos(args.input_dir, args.output)

if __name__ == "__main__":
    main()
