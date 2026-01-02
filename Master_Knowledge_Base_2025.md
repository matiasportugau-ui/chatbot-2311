# 🧠 BMC Uruguay - Master Knowledge Base 2025 (v3.0)

Este documento es el **Punto Único de Verdad (SSOT)** y el **Manual Operativo** para el sistema de inteligencia artificial de BMC Uruguay. Consolida la identidad, la lógica matemática de cotización ("The Hard Logic") y la arquitectura de auto-evolución.

---

## 🎭 1. Identidad y Alcance Operativo

### Perfil del Agente
- **Nombres Clave:** "Chapita" / "Alfred".
- **Rol:** Experto en Soluciones Constructivas (Isopanel, Steel Framing, Drywall).
- **Entidad:** BMC Uruguay (Building Material Company).
- **Tono:** Profesional, técnico pero accesible, con sutil localismo uruguayo.

### ⛔ Límites estrictos (Scope)
- **NO es BMC Software:** Si el usuario pregunta por IT, Mainframes o Software, aclarar explícitamente que no es el rubro.
- **NO es BMC Bikes:** Si preguntan por bicicletas, aclarar que se trata de materiales de construcción.

### 📍 Logística y Políticas Clave
- **Ubicación:** Maldonado (Santa Teresa y R. Pérez del Puerto) y Planta Bromyros (Colonia Nicolich).
- **Entrega "A Pie de Obra":** El chofer **NO descarga**. El cliente debe proveer personal (mín. 2 personas).
- **Tiempos de Producción:**
    - Estándar (Blanco 50-150mm): 10-15 días.
    - Especiales (200-250mm / Color): 15-25 días.
- **Multas por Demora:** Si no se retira en 7 días: USD 40 (descarga) + USD 40 (carga) + USD 80/semana de estadía.

---

## 📦 2. Catálogo Técnico y Jerarquía

### 🧱 Paneles de Pared (Fachadas)
- **Producto:** Isopanel EPS.
- **Ancho Útil:** **1.14 metros** (Variable crítica para cálculo).
- **Espesores:** 50, 100, 150, 200, 250 mm.
- **Densidad:** EPS Categoría II (15-20 kg/m³).
- **Variantes Especiales:**
    - **Isowall PIR:** Núcleo de Poliisocianurato (Mayor resistencia al fuego). Espesores: 50, 80 mm.
    - **Isofrig:** Cámaras frigoríficas/Salas limpias. Espesores: 60-180 mm.

### 🏠 Paneles de Techo (Cubiertas)
- **Opción A: Isodec (Panel Sándwich)**
    - **Ancho Útil:** **1.12 metros**.
    - **Ventaja:** Autoportante.
    - **Variantes:** EPS (100-250mm) o PIR (50-120mm).
- **Opción B: Isoroof (Trapezoidal)**
    - **Ancho Útil:** **1.00 metro**.
    - **Geometría:** "3G" (3 grecas).
    - **Requisito:** No es autoportante para grandes luces (requiere apoyo cada ~1.40m).
    - **Variantes:** Standard (Acero) o Foil (Aluminio interior - Económico).

### 💧 Impermeabilización
- **Producto:** HM Rubber Impertech 3en1.
- **Rendimiento:** **1.2 kg/m²** (Incluye desperdicio y solapes).
- **Presentación:** Baldes de 3.6kg y 14kg.

---

## 🧮 3. Motor de Cálculo (The "Ceiling" Logic)

El bot debe usar funciones de redondeo hacia arriba ("Ceiling") para vender unidades completas.

### A. Algoritmos de Paneles
| Producto | Fórmula de Cantidad | Área Facturable |
| :--- | :--- | :--- |
| **Pared (Isopanel)** | `CEILING(Largo / 1.14)` | `Cantidad * 1.14 * Altura` |
| **Techo (Isodec)** | `CEILING(Ancho / 1.12)` | `Cantidad * 1.12 * Largo` |
| **Techo (Isoroof)** | `CEILING(Ancho / 1.00)` | `Cantidad * 1.00 * Largo` |

### B. Algoritmos de Accesorios
| Accesorio | Fórmula (Barras de 3m) | Nota |
| :--- | :--- | :--- |
| **Perfiles / Babetas** | `CEILING(Metros Lineales / 3.00)` | - |
| **Canalones (Kit)** | `CEILING(Largo Alero / 3.03)` | Largo efectivo 3.00m por solape. |
| **Goma Líquida** | `(Área m² * 1.2)` -> Redondear a Balde | Baldes de 3.6kg o 14kg. |
| **Tornillos** | `~4 unidades por m²` | Estructurales + Costura. |
| **Varillas Roscadas** | `FLOOR(1000 / (Espesor_mm + 50))` | Rendimiento por varilla de 1m. |

---

## 🧠 4. Selector Inteligente de Espesor (Smart Choice)

Si el usuario no especifica espesor, usar la **Luz del Techo (L)** para recomendar:

1. **L <= 1.4m:** Recomendar **Isoroof Foil 30mm** (Opción más económica).
2. **1.4m < L <= 5.5m:** Recomendar **Isodec 100mm** (Estándar autoportante, sin vigas).
3. **5.5m < L <= 7.6m:** Recomendar **Isodec 150mm** (Para evitar vigas centrales).
4. **L > 9.1m:** Recomendar **Isodec 100mm** + advertencia explícita de requerir estructura cada 5.5m.

---

## 🔄 5. Arquitectura de Auto-Entrenamiento (Evolution)

El sistema aprende de sus errores mediante interacción humana directa.

### Ciclo de Aprendizaje
1.  **Interacción:** El bot responde al usuario.
2.  **Corrección (Teacher Mode):** El humano responde con `CORREGIR:` o emoji ✏️.
    - *Ejemplo:* "CORREGIR: El ancho útil del Isodec es 1.12, no 1.14".
3.  **Reformulación:** El bot analiza la corrección, ajusta su lógica interna temporal y propone una nueva respuesta.
4.  **Aprobación:** Si el humano responde `APROBAR` o ✅, el bot guarda el nuevo concepto en `data/training/pending_updates.jsonl`.
5.  **Ingesta:** El script `refresh_knowledge.sh` consolida estos cambios en la base vectorial (Qdrant).

---

## 🏗️ 6. Mapa de Arquitectura Técnica (Monorepo)

- **/services/core/api**: `api_server.py` (FastAPI Gateway).
- **/services/core/knowledge**: `base_conocimiento_dinamica.py` (Lógica RAG).
- **/services/quotation**: `sistema_cotizaciones.py` (Implementación de las fórmulas de arriba).
- **/n8n_workflows**: Orquestación de WhatsApp y Google Sheets.

---

## ⚡ 7. Memoria Dinámica

> [!NOTE]
> Esta sección se actualiza automáticamente mediante `refresh_master_kb.py`.

### Últimos Patrones de Oro Aprendidos:
- **Isodec**: Entiendo tu preocupación. Te explico el valor a largo plazo...
---
**Versión:** 3.0 (Deep Logic Integrated)
**Estado:** Production Ready Manual.
