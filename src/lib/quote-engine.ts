import { PRODUCTOS, calculateFullQuote, buscarProducto, obtenerEspesoresDisponibles, obtenerPrecio } from './knowledge-base'
import { parseQuoteConsulta } from './quote-parser'

// Define a simple knowledge base structure
const KNOWLEDGE_BASE = {
  productos: PRODUCTOS,
  buscarProducto,
  obtenerEspesoresDisponibles,
  obtenerPrecio
}

// Helper function to search for products
function buscarProductos(consulta: string) {
  const consultaLower = consulta.toLowerCase()
  const results = []

  for (const [key, producto] of Object.entries(PRODUCTOS)) {
    if (consultaLower.includes(key) || consultaLower.includes(producto.nombre.toLowerCase())) {
      results.push({
        id: key,
        nombre: producto.nombre,
        descripcion: producto.descripcion,
        precios: producto.precios
      })
    }
  }

  return results
}

// Helper function to generate quote
async function generarCotizacion(parsed: any, zona?: string) {
  try {
    // Handle area_m2 directly if specified
    let ancho = 1, largo = 1
    if (parsed.dimensiones?.area_m2) {
      // If only area is specified, use it as width (ancho) and 1m as length
      ancho = parsed.dimensiones.area_m2
      largo = 1
    } else if (parsed.dimensiones?.ancho && parsed.dimensiones?.largo) {
      // If both dimensions are specified
      ancho = parsed.dimensiones.ancho
      largo = parsed.dimensiones.largo
    } else if (parsed.dimensiones?.ancho) {
      // If only width is specified, assume it's area
      ancho = parsed.dimensiones.ancho
      largo = 1
    }

    return await calculateFullQuote({
      producto: parsed.producto?.tipo || 'isodec',
      dimensiones: {
        ancho,
        largo,
        espesor: parsed.producto?.grosor ? parseInt(parsed.producto.grosor) : 100
      },
      servicios: parsed.servicios || [],
      cantidad: parsed.producto?.cantidad || 1
    })
  } catch (error) {
    throw new Error('Error generando cotización: ' + (error instanceof Error ? error.message : String(error)))
  }
}

export interface QuoteResponse {
  tipo: 'cotizacion' | 'informacion' | 'pregunta' | 'error'
  mensaje: string
  cotizacion?: {
    producto: string
    descripcion: string
    precio_base: number
    servicios: any
    total: number
    recomendaciones: string[]
    codigo: string
  }
  productos_sugeridos?: Array<{
    nombre: string
    descripcion: string
    precio_estimado: number
    aplicaciones: string[]
  }>
  preguntas_frecuentes?: Array<{
    pregunta: string
    respuesta: string
  }>
  proximos_pasos?: string[]
}

export class QuoteEngine {
  private knowledgeBase = KNOWLEDGE_BASE

  // Procesar consulta y generar respuesta inteligente
  async procesarConsulta(consulta: string, telefono?: string): Promise<QuoteResponse> {
    try {
      // 1. Parsear consulta con IA
      const parsed = await parseQuoteConsulta(consulta)

      // 2. Determinar tipo de consulta
      const tipoConsulta = this.determinarTipoConsulta(consulta, parsed)

      switch (tipoConsulta) {
        case 'cotizacion':
          return await this.generarRespuestaCotizacion(parsed, telefono)

        case 'informacion':
          return await this.generarRespuestaInformacion(consulta)

        case 'pregunta':
          return await this.generarRespuestaPregunta(consulta)

        default:
          return this.generarRespuestaError(consulta)
      }
    } catch (error: any) {
      console.error('Error procesando consulta:', error)
      return this.generarRespuestaError(consulta, error.message)
    }
  }

  // Determinar tipo de consulta
  private determinarTipoConsulta(consulta: string, parsed: any): 'cotizacion' | 'informacion' | 'pregunta' {
    const consultaLower = consulta.toLowerCase()

    // Palabras clave para cotización
    const palabrasCotizacion = [
      'cotizar', 'precio', 'costo', 'cuanto', 'presupuesto', 'cotización',
      'isodec', 'isoroof', 'isopanel', 'isowall', 'chapa', 'calameria',
      'panel', 'techo', 'pared', 'galpón', 'galpon', 'm2', 'metro'
    ]

    // Palabras clave para información
    const palabrasInformacion = [
      'que es', 'como funciona', 'caracteristicas', 'especificaciones',
      'diferencia', 'ventajas', 'beneficios', 'aplicaciones'
    ]

    // Palabras clave para preguntas
    const palabrasPregunta = [
      'como', 'cuando', 'donde', 'por que', 'que', 'cual', 'cuanto tiempo',
      'garantia', 'instalacion', 'flete', 'entrega'
    ]

    if (palabrasCotizacion.some(palabra => consultaLower.includes(palabra))) {
      return 'cotizacion'
    }

    if (palabrasInformacion.some(palabra => consultaLower.includes(palabra))) {
      return 'informacion'
    }

    if (palabrasPregunta.some(palabra => consultaLower.includes(palabra))) {
      return 'pregunta'
    }

    // Si tiene información de producto parseada, es cotización
    if (parsed.producto?.tipo) {
      return 'cotizacion'
    }

    return 'pregunta'
  }

  // Generar respuesta de cotización
  private async generarRespuestaCotizacion(parsed: any, telefono?: string): Promise<QuoteResponse> {
    // Detectar zona por teléfono (simplificado)
    const zona = this.detectarZonaPorTelefono(telefono)

    // Generar cotización
    const cotizacion = await generarCotizacion(parsed, zona)

    if (!cotizacion.producto) {
      return {
        tipo: 'error',
        mensaje: 'No pude identificar el producto en tu consulta. ¿Podrías ser más específico? Por ejemplo: "Necesito cotizar Isodec 100mm para galpón de 50m2"',
        productos_sugeridos: this.obtenerProductosSugeridos(parsed.consulta_original || '')
      }
    }

    // Generar código único
    const codigo = this.generarCodigoCotizacion(telefono)

    // Construir mensaje de respuesta
    let mensaje = `🏗️ **COTIZACIÓN BMC** - Código: ${codigo}\n\n`
    mensaje += `📋 **${cotizacion.producto}**\n\n`
    mensaje += `💰 **Detalle de Precios:**\n`
    mensaje += `• Área: ${cotizacion.dimensiones}\n`
    mensaje += `• Precio unitario: $${cotizacion.precioUnitario?.toFixed(2) || '0'}/m²\n`
    mensaje += `• Subtotal: $${cotizacion.subtotal?.toFixed(2) || '0'}\n`

    if (parsed.servicios?.instalacion || parsed.servicios?.flete || parsed.servicios?.accesorios) {
      mensaje += `• Servicios adicionales incluidos\n`
    }

    mensaje += `\n🎯 **TOTAL: $${cotizacion.precioFinal?.toFixed(2) || '0'}**\n\n`

    mensaje += `📞 **Próximos pasos:**\n`
    mensaje += `• Confirmar dimensiones exactas\n`
    mensaje += `• Coordinar visita técnica (si es necesario)\n`
    mensaje += `• Definir fecha de entrega\n\n`
    mensaje += `¿Te interesa esta cotización? ¡Contáctanos para más detalles! 🚀`

    return {
      tipo: 'cotizacion',
      mensaje,
      cotizacion: {
        producto: cotizacion.producto,
        descripcion: cotizacion.dimensiones,
        precio_base: cotizacion.subtotal,
        servicios: {},
        total: cotizacion.precioFinal,
        recomendaciones: [],
        codigo
      },
      proximos_pasos: [
        'Confirmar dimensiones exactas',
        'Coordinar visita técnica',
        'Definir fecha de entrega',
        'Firmar contrato'
      ]
    }
  }

  // Generar respuesta informativa
  private async generarRespuestaInformacion(consulta: string): Promise<QuoteResponse> {
    const productos = buscarProductos(consulta)

    if (productos.length === 0) {
      return {
        tipo: 'informacion',
        mensaje: `No encontré información específica sobre "${consulta}". 

Te puedo ayudar con información sobre nuestros productos principales:

🏗️ **Isodec EPS** - Paneles aislantes para paredes y techos
🏠 **Isoroof** - Paneles para techos con acabado metálico  
🏢 **Isopanel** - Paneles de uso general
🧱 **Isowall** - Paneles específicos para paredes exteriores
🔧 **Calamería** - Estructura metálica de soporte
📐 **Chapas** - Chapas galvanizadas

¿Sobre cuál te gustaría saber más?`,
        productos_sugeridos: this.obtenerProductosSugeridos(consulta)
      }
    }

    const producto = productos[0]
    let mensaje = `📋 **${producto.nombre}**\n\n`
    mensaje += `${producto.descripcion}\n\n`

    mensaje += `💰 **Precios disponibles:**\n`
    for (const [espesor, precio] of Object.entries(producto.precios)) {
      mensaje += `• ${espesor}: $${precio}/m²\n`
    }

    mensaje += `\n¿Te interesa cotizar este producto? ¡Dime las dimensiones de tu proyecto! 📐`

    return {
      tipo: 'informacion',
      mensaje,
      productos_sugeridos: productos.slice(1, 4).map(p => ({
        nombre: p.nombre,
        descripcion: p.descripcion,
        precio_estimado: 50,
        aplicaciones: []
      }))
    }
  }

  // Generar respuesta a preguntas frecuentes
  private async generarRespuestaPregunta(consulta: string): Promise<QuoteResponse> {
    const preguntasFrecuentes = this.obtenerPreguntasFrecuentes(consulta)

    if (preguntasFrecuentes.length > 0) {
      return {
        tipo: 'pregunta',
        mensaje: `🤔 **Pregunta Frecuente**\n\n${preguntasFrecuentes[0].respuesta}`,
        preguntas_frecuentes: preguntasFrecuentes
      }
    }

    return {
      tipo: 'pregunta',
      mensaje: `Hola! 👋 

No estoy seguro de entender tu pregunta. Te puedo ayudar con:

📋 **Cotizaciones** - Dime qué producto necesitas y las dimensiones
ℹ️ **Información** - Sobre nuestros productos y servicios  
❓ **Preguntas** - Sobre instalación, flete, garantías, etc.

¿En qué te puedo ayudar específicamente?`,
      preguntas_frecuentes: this.obtenerPreguntasFrecuentes('general')
    }
  }

  // Generar respuesta de error
  private generarRespuestaError(consulta: string, error?: string): QuoteResponse {
    return {
      tipo: 'error',
      mensaje: `Lo siento, hubo un problema procesando tu consulta. 😔

${error ? `Error: ${error}` : 'Por favor, intenta reformular tu pregunta.'}

Puedes contactarnos directamente al 📞 [teléfono] o escribirnos de nuevo con más detalles.`
    }
  }

  // Detectar zona por teléfono (simplificado)
  private detectarZonaPorTelefono(telefono?: string): string {
    if (!telefono) return 'montevideo'

    // Códigos de área de Uruguay (simplificado)
    const codigos: { [key: string]: string } = {
      '2': 'montevideo',    // Montevideo
      '4': 'canelones',     // Canelones, Maldonado, Rivera, Artigas, etc.
      '5': 'fray_bentos',   // Río Negro
      '6': 'colonia'        // Colonia
    }

    const codigoArea = telefono.slice(0, 1)
    return codigos[codigoArea] || 'montevideo'
  }

  // Generar código único de cotización
  private generarCodigoCotizacion(telefono?: string): string {
    const timestamp = Date.now().toString().slice(-6)
    const telefonoSuffix = telefono ? telefono.slice(-3) : '000'
    return `BMC${timestamp}${telefonoSuffix}`
  }

  // Obtener productos sugeridos
  private obtenerProductosSugeridos(consulta: string) {
    const productos = buscarProductos(consulta)
    return productos.slice(0, 3).map(p => ({
      nombre: p.nombre,
      descripcion: p.descripcion,
      precio_estimado: 50,
      aplicaciones: []
    }))
  }

  // Obtener preguntas frecuentes
  private obtenerPreguntasFrecuentes(consulta: string) {
    const faqs = [
      {
        pregunta: '¿Cuánto tiempo tarda la entrega?',
        respuesta: 'La entrega depende de la zona y disponibilidad. En Montevideo: 3-5 días hábiles. Interior: 5-10 días hábiles. Te confirmamos el plazo exacto al confirmar la cotización.'
      },
      {
        pregunta: '¿Incluyen instalación?',
        respuesta: 'Sí, ofrecemos servicio de instalación profesional. El costo se calcula según la complejidad y área del proyecto. Incluye mano de obra especializada y garantía de instalación.'
      },
      {
        pregunta: '¿Qué garantía tienen los productos?',
        respuesta: 'Nuestros productos tienen garantía de 10 años contra defectos de fabricación. La instalación tiene garantía de 2 años. Todos los productos cumplen normas IRAM y certificaciones internacionales.'
      },
      {
        pregunta: '¿Hacen flete a todo el país?',
        respuesta: 'Sí, realizamos flete a todo Uruguay. El costo varía según la zona y peso del material. En Montevideo y Canelones el flete es más económico. Te calculamos el costo exacto según tu ubicación.'
      },
      {
        pregunta: '¿Qué formas de pago aceptan?',
        respuesta: 'Aceptamos efectivo, transferencia bancaria, tarjeta de crédito y débito. Para proyectos grandes ofrecemos financiación a través de bancos conveniados. Consulta por planes de pago especiales.'
      }
    ]

    const consultaLower = consulta.toLowerCase()
    return faqs.filter(faq =>
      faq.pregunta.toLowerCase().includes(consultaLower) ||
      faq.respuesta.toLowerCase().includes(consultaLower)
    )
  }
}

// Instancia global del motor de cotización
export const quoteEngine = new QuoteEngine()
