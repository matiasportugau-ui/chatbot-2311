import json
import re
from pathlib import Path

def refresh_master_kb():
    """Sincroniza el Master KB con los últimos datos de conocimiento_consolidado.json"""

    directorio_actual = Path(__file__).resolve().parent
    archivo_json = directorio_actual / "conocimiento_consolidado.json"
    archivo_md = directorio_actual / "Master_Knowledge_Base_2025.md"

    if not archivo_json.exists():
        print(f"❌ Error: {archivo_json} no encontrado.")
        return

    if not archivo_md.exists():
        print(f"❌ Error: {archivo_md} no encontrado.")
        return

    # Cargar datos consolidados
    try:
        with open(archivo_json, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error leyendo JSON: {e}")
        return

    # Extraer patrones destacados (Top 5 respuestas efectivas)
    patrones_oro = []

    # Intentar obtener patrones de venta
    patrones = data.get("patrones_venta", [])
    for p in patrones[:5]:
        intencion = p.get("intencion", "general")
        estrategia = p.get("estrategia", "")
        if estrategia:
            patrones_oro.append(f"- **{intencion.capitalize()}**: {estrategia}")

    # Si no hay patrones de venta estructurados, buscar en conocimiento_productos
    if not patrones_oro:
        productos = data.get("conocimiento_productos", {})
        for prod, info in list(productos.items())[:5]:
            respuestas = info.get("respuestas_efectivas", [])
            if respuestas:
                patrones_oro.append(f"- **{prod.capitalize()}**: {respuestas[0]}")

    if not patrones_oro:
        patrones_oro = ["- Sin nuevos patrones de oro detectados aún."]

    # Leer el MD actual
    with open(archivo_md, "r", encoding="utf-8") as f:
        md_content = f.read()

    # Reemplazar la sección de memoria dinámica
    marcador_inicio = "### Últimos Patrones de Oro Aprendidos:"
    bloque_nuevo = f"{marcador_inicio}\n" + "\n".join(patrones_oro)

    # Regex para encontrar desde el marcador hasta el final del documento o una línea de separación
    pattern = rf"{re.escape(marcador_inicio)}[\s\S]*?(?=\n---|\Z)"

    if re.search(pattern, md_content):
        updated_content = re.sub(pattern, bloque_nuevo, md_content)
    else:
        # Si no lo encuentra con regex, simplemente lo añade al final o lo intenta adjuntar
        updated_content = md_content + "\n\n" + bloque_nuevo

    # Guardar cambios
    with open(archivo_md, "w", encoding="utf-8") as f:
        f.write(updated_content)

    print(f"✅ Master_Knowledge_Base_2025.md actualizado con {len(patrones_oro)} patrones.")

if __name__ == "__main__":
    refresh_master_kb()
