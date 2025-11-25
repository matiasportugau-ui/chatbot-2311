# Sistema de Cotizaciones BMC Uruguay

Sistema completo para la gestión de cotizaciones de productos de aislamiento térmico, desarrollado específicamente para BMC Uruguay. Integra la lógica de cotización basada en plantillas, matriz de precios actualizable, y mapeo de productos con enlaces web.

## Características Principales

- **Gestión completa de cotizaciones** con seguimiento de estados
- **Cálculo automático de precios** basado en especificaciones técnicas
- **Integración con matriz de precios** actualizable desde bmcuruguay.com.uy
- **Plantillas personalizables** para diferentes tipos de cotizaciones
- **Importación desde Google Sheets** del Administrador de Cotizaciones II
- **Mapeo automático de productos** con enlaces web
- **Búsqueda avanzada** por cliente, teléfono, fecha
- **Exportación de datos** en formato JSON
- **Reportes detallados** en HTML y PDF
- **Sistema modular** con componentes independientes
- **Validación inteligente de datos** - El bot solicita automáticamente información faltante

## Validación Inteligente de Datos (Bot)

El sistema incluye validación centralizada que garantiza que toda la información requerida esté completa antes de generar una cotización. El bot conversacional detecta automáticamente datos faltantes y los solicita al cliente de manera natural y amigable.

### Campos Obligatorios

Para generar una cotización, el sistema requiere los siguientes datos mínimos:

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| **nombre** | Nombre del cliente | Juan |
| **apellido** | Apellido del cliente | Pérez |
| **telefono** | Teléfono de contacto | 099123456 |
| **producto** | Tipo de producto | isodec, poliestireno, lana_roca |
| **espesor** | Espesor del producto | 50mm, 75mm, 100mm, 125mm, 150mm |
| **largo** | Largo en metros | 10 |
| **ancho** | Ancho en metros | 5 |

### Comportamiento del Bot

**Solicitud Automática de Datos:**
- El bot detecta automáticamente qué datos faltan
- Solicita la información de forma clara y específica
- Adapta el mensaje según la cantidad de datos faltantes
- No genera cotización hasta tener todos los datos requeridos

**Ejemplos de Mensajes del Bot:**

Cuando falta un solo dato:
```
Bot: "Para poder cotizar necesito que me indiques qué producto te interesa 
(Isodec, Poliestireno o Lana de Roca). ¿Cuál te interesa?"
```

Cuando faltan varios datos:
```
Bot: "Para poder cotizar necesito los siguientes datos: tu apellido, 
el espesor que necesitas (50mm, 75mm, 100mm, 125mm o 150mm) y las dimensiones 
(largo x ancho en metros, por ejemplo: 10m x 5m). ¿Podrías indicarme esa información?"
```

Cuando faltan las dimensiones:
```
Bot: "Para poder cotizar necesito las dimensiones (largo x ancho en metros, 
por ejemplo: 10m x 5m). ¿Cuáles son las dimensiones?"
```

### Flujo de Validación

1. **Cliente inicia conversación** - El bot saluda y ofrece ayuda
2. **Cliente solicita cotización** - El bot explica qué datos necesita
3. **Cliente proporciona información** - El bot extrae los datos del mensaje
4. **Validación automática** - El sistema verifica si faltan datos obligatorios
5. **Solicitud de datos faltantes** - Si falta algo, el bot lo solicita específicamente
6. **Generación de cotización** - Solo cuando todos los datos están completos

### Ventajas del Sistema de Validación

✅ **Cotizaciones completas:** Garantiza que ninguna cotización se genere sin información crítica  
✅ **Experiencia natural:** El bot solicita datos de forma conversacional y amigable  
✅ **Mensajes contextuales:** Los mensajes se adaptan a qué específicamente falta  
✅ **Mantenibilidad:** La lógica de validación está centralizada en `utils_cotizaciones.py`  
✅ **Extensible:** Fácil agregar nuevos campos obligatorios en el futuro

### Uso en el Código

```python
from utils_cotizaciones import obtener_datos_faltantes, formatear_mensaje_faltantes

# Construir contexto con datos actuales
contexto = {
    "nombre": "Juan",
    "apellido": "",  # Faltante
    "telefono": "099123456",
    "producto": "isodec",
    "espesor": "100mm",
    "largo": 10,
    "ancho": 5
}

# Detectar datos faltantes
faltantes = obtener_datos_faltantes(contexto)  
# Resultado: ['apellido']

# Generar mensaje amigable
mensaje = formatear_mensaje_faltantes(faltantes)
# Resultado: "Para poder cotizar necesito tu apellido. ¿Cómo te llamas?"
```

## Estructura del Sistema

```
sistema-cotizaciones-bmc/
├── sistema_cotizaciones.py      # Lógica principal del sistema
├── utils_cotizaciones.py         # Utilidades de validación centralizada
├── importar_datos_planilla.py   # Importador desde Google Sheets
├── generador_plantillas.py      # Generador de plantillas
├── mapeador_productos_web.py    # Mapeador de productos web
├── ia_conversacional_integrada.py # IA conversacional con validación
├── chat_interactivo.py          # Chat interactivo con validación
├── simulacion_agente.py         # Simulación de agente con validación
├── main.py                      # Sistema interactivo completo
├── demo.py                      # Demostración del sistema
├── ejecutar_sistema.py          # Script de ejecución principal
├── instalar.py                  # Instalador del sistema
├── config.py                    # Configuración centralizada
├── matriz_precios.json          # Matriz de precios y productos
├── requirements.txt             # Dependencias opcionales
└── README.md                    # Documentación completa
```

## Trabajo en la Nube (Codespaces / Cursor Cloud)

1. **Sincroniza el repositorio:** verifica que tu rama local esté en GitHub (`git push origin <rama>`). Esto asegura que el workspace cloud arranque con la última versión.
2. **Crea el workspace remoto:**
   - **GitHub Codespaces:** en la página del repo haz clic en `Code → Create codespace on main`.
   - **Cursor Cloud:** abre Cursor, selecciona `New Cloud Workspace` y pega la URL del repositorio.
3. **Dev Container automático:** al iniciar, el archivo `.devcontainer/devcontainer.json` cargará el contenedor `python:3.11` con Node.js 20 y ejecutará `.devcontainer/post-create.sh` para instalar dependencias de Python (`requirements.txt`) y Node (`nextjs-app`).
4. **Variables y secretos:** usa `SETUP_CREDENTIALS_GUIDE.md` y `SETUP_WHATSAPP.md` para cargar las API keys o tokens necesarios dentro del workspace (puedes usar los Secrets de GitHub/Cursor).
5. **Ciclo local ↔ nube:** antes de cambiar de entorno haz `git pull` y al terminar en la nube confirma tus cambios (`git commit && git push`) para evitar divergencias.

### Verificación rápida dentro del workspace

- `python ejecutar_sistema.py` para validar el flujo principal.
- `cd nextjs-app && npm run dev` para probar la UI en `http://localhost:3000`.
- `python gestionar_servicios.py` o los scripts de `python-scripts/` según lo que necesites probar.

Una vez que el workspace funcione, considera activar despliegues automáticos (por ejemplo GitHub Actions + Vercel) reutilizando los mismos comandos usados en el contenedor.

## Instalación

### Instalación Automática (Recomendada)

1. **Requisitos del sistema:**
   - Python 3.7 o superior
   - Conexión a internet (para dependencias opcionales)

2. **Ejecutar instalador:**
   ```bash
   python instalar.py
   ```

3. **Ejecutar el sistema:**
   ```bash
   python ejecutar_sistema.py
   ```

### Instalación Manual

1. **Requisitos del sistema:**
   - Python 3.7 o superior
   - Módulos básicos: `json`, `datetime`, `decimal`, `csv`, `dataclasses`, `typing`

2. **Dependencias opcionales (para funcionalidades avanzadas):**
   ```bash
   pip install -r requirements.txt
   ```

3. **Clonar o descargar el sistema:**
   ```bash
   git clone [url-del-repositorio]
   cd sistema-cotizaciones-bmc
   ```

4. **Ejecutar el sistema:**
   ```bash
   python ejecutar_sistema.py
   ```

## Uso del Sistema

### 1. Crear Nueva Cotización

El sistema permite crear cotizaciones de forma interactiva:

- **Datos del cliente:** nombre, teléfono, dirección, zona
- **Especificaciones del producto:** tipo, espesor, relleno, color
- **Dimensiones:** largo y ancho en metros
- **Terminaciones:** frontal, superior, laterales
- **Servicios:** anclajes, traslado
- **Información adicional:** forma de contacto, observaciones

### 2. Buscar Cotizaciones

Opciones de búsqueda disponibles:
- Por nombre del cliente
- Por número de teléfono
- Por rango de fechas
- Mostrar todas las cotizaciones

### 3. Generar Reportes

El sistema genera reportes detallados que incluyen:
- Información del cliente
- Especificaciones técnicas del producto
- Cálculos de dimensiones y precios
- Desglose de costos
- Información de contacto de BMC Uruguay

### 4. Exportar Datos

- **Cotizaciones:** Exporta todas las cotizaciones a JSON
- **Plantillas:** Exporta las plantillas de cotización
- **Configuración:** Exporta la matriz de precios

## Productos Soportados

### Isodec
- **Descripción:** Panel aislante térmico con núcleo de EPS
- **Espesores:** 50mm, 75mm, 100mm, 125mm, 150mm
- **Rellenos:** EPS, Poliuretano, Lana de roca
- **Colores:** Blanco, Gris, Personalizado
- **Terminaciones:** Gotero, Hormigón, Aluminio

### Poliestireno Expandido
- **Descripción:** Aislante térmico de poliestireno expandido
- **Espesores:** 25mm, 50mm, 75mm, 100mm

### Lana de Roca
- **Descripción:** Aislante térmico y acústico de lana de roca
- **Espesores:** 50mm, 75mm, 100mm

## Fórmulas de Cálculo

### Precio Base
```
Precio base = Área (m²) × Precio por m²
```

### Factores de Ajuste
- **Espesor:** 0.8 (50mm) a 1.2 (150mm)
- **Color:** 1.0 (Blanco) a 1.15 (Personalizado)
- **Terminaciones:** +5% (Gotero) a +15% (Aluminio)
- **Servicios:** Incluidos o con descuento

### Precio Final
```
Precio final = Precio base × Factor espesor × Factor color × Factor terminaciones × Factor servicios
```

## Integración con Google Sheets

El sistema puede importar datos desde la planilla "Administrador de Cotizaciones II":

1. **Exportar datos de Google Sheets** a CSV
2. **Usar el importador** para procesar los datos
3. **Mapear campos** entre la planilla y el sistema
4. **Calcular precios** automáticamente

### Campos Mapeados

| Google Sheets | Sistema |
|---------------|---------|
| Cliente | cliente.nombre |
| Telefono-Contacto | cliente.telefono |
| Direccion / Zona | cliente.direccion |
| Producto | especificaciones.producto |
| Espesor | especificaciones.espesor |
| Relleno | especificaciones.relleno |
| Largo (M) | especificaciones.largo_metros |
| Ancho (M) | especificaciones.ancho_metros |
| Color | especificaciones.color |
| TerminaFront | especificaciones.termina_front |
| TerminaSup | especificaciones.termina_sup |
| Termina Lat. 1 | especificaciones.termina_lat_1 |
| Termina Lat. 2 | especificaciones.termina_lat_2 |
| Anclajes a | especificaciones.anclajes |
| Traslado | especificaciones.traslado |

## Plantillas de Cotización

### 1. Isodec - Cotización Estándar
- Para productos Isodec con especificaciones completas
- Incluye todos los campos técnicos
- Cálculo detallado de precios

### 2. Cotización Rápida
- Para estimaciones rápidas
- Campos mínimos requeridos
- Precio estimado por m²

### 3. Cotización Detallada
- Para cotizaciones completas
- Desglose de costos
- Incluye IVA y servicios

## Configuración

### Matriz de Precios (matriz_precios.json)

```json
{
  "productos": {
    "isodec": {
      "espesores_disponibles": {
        "100mm": {
          "precio_base": 150.00,
          "factor_espesor": 1.0
        }
      },
      "colores_disponibles": {
        "Blanco": {
          "precio_base": 0.00,
          "factor_color": 1.0
        }
      }
    }
  },
  "configuracion": {
    "moneda": "UYU",
    "iva_porcentaje": 22
  }
}
```

## Estados de Cotización

- **Pendiente:** Cotización creada, pendiente de asignación
- **Asignado:** Asignada a un vendedor
- **Enviado:** Enviada al cliente
- **Listo:** Lista para confirmación
- **Confirmado:** Confirmada por el cliente
- **Rechazado:** Rechazada por el cliente

## Asignaciones

- **MA:** Vendedor A
- **MO:** Vendedor B
- **RA:** Vendedor C
- **SPRT:** Soporte técnico
- **Ref:** Referencia

## Enlaces de Productos

El sistema incluye enlaces directos a los productos en bmcuruguay.com.uy:

- [Isodec](https://bmcuruguay.com.uy/productos/isodec)
- [Poliestireno](https://bmcuruguay.com.uy/productos/poliestireno)
- [Lana de Roca](https://bmcuruguay.com.uy/productos/lana-roca)

## Desarrollo y Personalización

### Agregar Nuevos Productos

1. Editar `matriz_precios.json`
2. Agregar el producto con sus especificaciones
3. Actualizar el sistema con `actualizar_precio_producto()`

### Crear Nuevas Plantillas

1. Usar `GeneradorPlantillas`
2. Definir campos requeridos y opcionales
3. Crear fórmulas de cálculo
4. Generar templates HTML/PDF

### Modificar Fórmulas de Cálculo

Editar los métodos en `SistemaCotizacionesBMC`:
- `_calcular_factor_espesor()`
- `_calcular_factor_color()`
- `_calcular_factor_terminaciones()`
- `_calcular_factor_anclajes()`
- `_calcular_factor_traslado()`

## Solución de Problemas

### Error: "Producto no encontrado"
- Verificar que el producto esté en `matriz_precios.json`
- Usar códigos exactos (isodec, poliestireno, lana_roca)

### Error: "Precio no calculado"
- Verificar que el precio base esté configurado
- Revisar las especificaciones del producto

### Error: "Archivo no encontrado"
- Verificar que `matriz_precios.json` esté en el directorio
- Verificar permisos de lectura/escritura

## Contacto y Soporte

Para soporte técnico o consultas sobre el sistema:

- **Email:** info@bmcuruguay.com.uy
- **Web:** https://bmcuruguay.com.uy
- **Teléfono:** +598 XX XXX XXX

## Licencia

Sistema desarrollado específicamente para BMC Uruguay. Todos los derechos reservados.

---

**Versión:** 1.0  
**Última actualización:** Diciembre 2024  
**Desarrollado para:** BMC Uruguay
