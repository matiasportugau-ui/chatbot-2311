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

## Estructura del Sistema

```
sistema-cotizaciones-bmc/
├── sistema_cotizaciones.py      # Lógica principal del sistema
├── importar_datos_planilla.py   # Importador desde Google Sheets
├── generador_plantillas.py      # Generador de plantillas
├── mapeador_productos_web.py    # Mapeador de productos web
├── main.py                      # Sistema interactivo completo
├── demo.py                      # Demostración del sistema
├── ejecutar_sistema.py          # Script de ejecución principal
├── instalar.py                  # Instalador del sistema
├── config.py                    # Configuración centralizada
├── matriz_precios.json          # Matriz de precios y productos
├── requirements.txt             # Dependencias opcionales
└── README.md                    # Documentación completa
```

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
