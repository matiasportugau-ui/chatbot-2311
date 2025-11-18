/**
 * 🏗️ Motor de Cotización Integrado con Base de Conocimiento Evolutiva
 * 
 * Este módulo integra el sistema de cotización BMC con la base de conocimiento
 * dinámica que aprende y evoluciona basada en interacciones reales.
 */

import { OpenAI } from 'openai'
import { secureConfig } from './secure-config'
import { connectDB } from './mongodb'
import { QuoteService } from './quote-service'
import { parseQuoteConsulta, ParsedQuote } from './quote-parser'
import { PRODUCTOS, SERVICIOS_ADICIONALES, ZONAS_FLETE, calculateFullQuote } from './knowledge-base'

// Interfaces para el sistema integrado
export interface InteraccionCliente {
  id: string
  telefono: string
  nombre: string
  consulta: string
  respuesta: string
  cotizacion_generada: boolean
  conversion: boolean
  timestamp: Date
  satisfaccion?: number
  lecciones_aprendidas: string[]
}

export interface PatronVenta {
  id: string
  patron: string
  frecuencia: number
  tasa_conversion: number
  productos_asociados: string[]
  servicios_populares: string[]
  zona_geografica: string
  perfil_cliente: string
  timestamp: Date
}

export interface ConocimientoProducto {
  producto: string
  consultas_frecuentes: string[]
  objeciones_comunes: string[]
  respuestas_efectivas: string[]
  precio_optimo: number
  servicios_complementarios: string[]
  tasa_conversion: number
  ultima_actualizacion: Date
}

export interface RespuestaInteligente {
  tipo: 'cotizacion' | 'informacion' | 'objeccion' | 'seguimiento'
  mensaje: string
  cotizacion?: any
  confianza: number
  patrones_aplicados: string[]
  conocimiento_utilizado: string[]
  recomendaciones: string[]
}

class MotorCotizacionIntegrado {
  private openai: OpenAI
  private quoteService: QuoteService
  private baseConocimiento: Map<string, any> = new Map()
  private patronesVenta: PatronVenta[] = []
  private conocimientoProductos: ConocimientoProducto[] = []
  private interacciones: InteraccionCliente[] = []

  constructor() {
    if (!secureConfig.isReady()) {
      throw new Error('SecureConfig not initialized. Call initializeSecureConfig() first.')
    }

    const config = secureConfig.getOpenAIConfig()
    this.openai = new OpenAI({ apiKey: config.apiKey })
    this.quoteService = new QuoteService()
    
    // Inicializar base de conocimiento
    this.inicializarBaseConocimiento()
  }

  /**
   * 🧠 Inicializar Base de Conocimiento Dinámica
   */
  private async inicializarBaseConocimiento() {
    try {
      await connectDB()
      
      // Cargar patrones de venta existentes
      await this.cargarPatronesVenta()
      
      // Cargar conocimiento de productos
      await this.cargarConocimientoProductos()
      
      // Cargar interacciones históricas
      await this.cargarInteraccionesHistoricas()
      
      console.log('✅ Base de conocimiento inicializada correctamente')
    } catch (error) {
      console.error('❌ Error inicializando base de conocimiento:', error)
    }
  }

  /**
   * 🔄 Procesar Consulta con IA Integrada
   */
  async procesarConsulta(consulta: string, userPhone: string, userName?: string): Promise<RespuestaInteligente> {
    try {
      // 1. Parsear consulta con IA
      const parsed = await parseQuoteConsulta(consulta)
      
      // 2. Analizar contexto y patrones
      const contexto = await this.analizarContexto(consulta, userPhone)
      
      // 3. Generar respuesta inteligente
      const respuesta = await this.generarRespuestaInteligente(consulta, parsed, contexto)
      
      // 4. Registrar interacción para aprendizaje
      await this.registrarInteraccion({
        id: this.generarId(),
        telefono: userPhone,
        nombre: userName || 'Cliente',
        consulta,
        respuesta: respuesta.mensaje,
        cotizacion_generada: respuesta.tipo === 'cotizacion',
        conversion: false, // Se actualizará después
        timestamp: new Date(),
        lecciones_aprendidas: []
      })
      
      return respuesta
    } catch (error) {
      console.error('Error procesando consulta:', error)
      return {
        tipo: 'informacion',
        mensaje: 'Disculpa, hubo un error procesando tu consulta. Por favor, intenta de nuevo.',
        confianza: 0,
        patrones_aplicados: [],
        conocimiento_utilizado: [],
        recomendaciones: []
      }
    }
  }

  /**
   * 🎯 Analizar Contexto y Patrones
   */
  private async analizarContexto(consulta: string, userPhone: string): Promise<any> {
    // Buscar patrones similares en interacciones anteriores
    const patronesSimilares = this.buscarPatronesSimilares(consulta)
    
    // Analizar perfil del cliente
    const perfilCliente = await this.analizarPerfilCliente(userPhone)
    
    // Identificar tipo de consulta
    const tipoConsulta = this.identificarTipoConsulta(consulta)
    
    return {
      patronesSimilares,
      perfilCliente,
      tipoConsulta,
      confianza: this.calcularConfianza(patronesSimilares, perfilCliente)
    }
  }

  /**
   * 🤖 Generar Respuesta Inteligente
   */
  private async generarRespuestaInteligente(
    consulta: string, 
    parsed: ParsedQuote, 
    contexto: any
  ): Promise<RespuestaInteligente> {
    
    const prompt = `Eres un experto en ventas de productos de construcción (BMC Uruguay) con acceso a una base de conocimiento que aprende y evoluciona.

CONSULTA DEL CLIENTE: "${consulta}"

INFORMACIÓN PARSEADA:
${JSON.stringify(parsed, null, 2)}

CONTEXTO Y PATRONES:
- Patrones similares encontrados: ${contexto.patronesSimilares.length}
- Perfil del cliente: ${JSON.stringify(contexto.perfilCliente)}
- Tipo de consulta: ${contexto.tipoConsulta}
- Confianza: ${contexto.confianza}

BASE DE CONOCIMIENTO DISPONIBLE:
- Productos: Isodec, Isoroof, Isopanel, Isowall, Chapas, Calamería
- Servicios: Instalación, Flete, Accesorios
- Zonas: Montevideo, Canelones, Maldonado, Rivera, etc.

INSTRUCCIONES:
1. Si es una consulta de cotización, genera una cotización detallada
2. Si es una pregunta de información, responde con datos precisos
3. Si es una objeción, maneja inteligentemente la situación
4. Aplica patrones de venta exitosos del historial
5. Personaliza la respuesta según el perfil del cliente
6. Incluye recomendaciones basadas en conocimiento acumulado

Responde en formato JSON:
{
  "tipo": "cotizacion" | "informacion" | "objecion" | "seguimiento",
  "mensaje": "Respuesta personalizada al cliente",
  "cotizacion": { /* datos de cotización si aplica */ },
  "confianza": 0.95,
  "patrones_aplicados": ["patron1", "patron2"],
  "conocimiento_utilizado": ["conocimiento1", "conocimiento2"],
  "recomendaciones": ["recomendacion1", "recomendacion2"]
}`

    const completion = await this.openai.chat.completions.create({
      model: 'gpt-4',
      messages: [{ role: 'user', content: prompt }],
      response_format: { type: 'json_object' },
      temperature: 0.3
    })

    const respuesta = JSON.parse(completion.choices[0].message.content || '{}')
    
    // Si es cotización, calcular precios reales
    if (respuesta.tipo === 'cotizacion' && parsed.producto) {
      const cotizacionReal = calculateFullQuote({
        producto: parsed.producto.tipo,
        dimensiones: {
          ancho: parsed.dimensiones?.ancho || 1,
          largo: parsed.dimensiones?.largo || 1,
          espesor: parseInt(parsed.producto.grosor || '100')
        },
        servicios: [],
        cantidad: parsed.producto.cantidad || 1
      })
      respuesta.cotizacion = cotizacionReal
    }

    return respuesta
  }

  /**
   * 🔍 Buscar Patrones Similares
   */
  private buscarPatronesSimilares(consulta: string): PatronVenta[] {
    return this.patronesVenta.filter(patron => 
      this.calcularSimilitud(consulta, patron.patron) > 0.7
    )
  }

  /**
   * 👤 Analizar Perfil del Cliente
   */
  private async analizarPerfilCliente(userPhone: string): Promise<any> {
    // Buscar interacciones anteriores del cliente
    const interaccionesCliente = this.interacciones.filter(i => i.telefono === userPhone)
    
    if (interaccionesCliente.length === 0) {
      return { tipo: 'nuevo_cliente', confianza: 0.5 }
    }

    // Analizar patrones del cliente
    const productosConsultados = interaccionesCliente
      .filter(i => i.cotizacion_generada)
      .map(i => this.extraerProductosDeConsulta(i.consulta))
      .flat()

    const serviciosPreferidos = interaccionesCliente
      .filter(i => i.cotizacion_generada)
      .map(i => this.extraerServiciosDeConsulta(i.consulta))
      .flat()

    const tasaConversion = interaccionesCliente.filter(i => i.conversion).length / interaccionesCliente.length

    return {
      tipo: 'cliente_recurrente',
      total_interacciones: interaccionesCliente.length,
      productos_preferidos: this.contarFrecuencias(productosConsultados),
      servicios_preferidos: this.contarFrecuencias(serviciosPreferidos),
      tasa_conversion: tasaConversion,
      ultima_interaccion: Math.max(...interaccionesCliente.map(i => i.timestamp.getTime())),
      confianza: Math.min(0.9, 0.5 + (interaccionesCliente.length * 0.1))
    }
  }

  /**
   * 🎯 Identificar Tipo de Consulta
   */
  private identificarTipoConsulta(consulta: string): string {
    const consultaLower = consulta.toLowerCase()
    
    if (consultaLower.includes('precio') || consultaLower.includes('cuesta') || consultaLower.includes('cotizar')) {
      return 'cotizacion'
    }
    
    if (consultaLower.includes('que es') || consultaLower.includes('como funciona') || consultaLower.includes('caracteristicas')) {
      return 'informacion'
    }
    
    if (consultaLower.includes('muy caro') || consultaLower.includes('no me convence') || consultaLower.includes('problema')) {
      return 'objeccion'
    }
    
    return 'seguimiento'
  }

  /**
   * 📊 Calcular Confianza
   */
  private calcularConfianza(patrones: PatronVenta[], perfil: any): number {
    let confianza = 0.5 // Base
    
    // Aumentar confianza con patrones similares
    if (patrones.length > 0) {
      confianza += 0.2
    }
    
    // Aumentar confianza con perfil del cliente
    if (perfil.tipo === 'cliente_recurrente') {
      confianza += 0.3
    }
    
    return Math.min(1.0, confianza)
  }

  /**
   * 📝 Registrar Interacción para Aprendizaje
   */
  private async registrarInteraccion(interaccion: InteraccionCliente) {
    this.interacciones.push(interaccion)
    
    // Guardar en base de datos
    try {
      await this.quoteService.createQuote({
        arg: `INT-${Date.now()}`,
        estado: 'Listo',
        fecha: interaccion.timestamp.toISOString().split('T')[0],
        cliente: interaccion.nombre,
        origen: 'WA',
        telefono: interaccion.telefono,
        direccion: 'Sistema IA',
        consulta: interaccion.consulta
      })
    } catch (error) {
      console.error('Error guardando interacción:', error)
    }
  }

  /**
   * 🧠 Actualizar Base de Conocimiento
   */
  async actualizarBaseConocimiento() {
    try {
      // Analizar nuevas interacciones
      await this.analizarNuevasInteracciones()
      
      // Actualizar patrones de venta
      await this.actualizarPatronesVenta()
      
      // Actualizar conocimiento de productos
      await this.actualizarConocimientoProductos()
      
      console.log('✅ Base de conocimiento actualizada')
    } catch (error) {
      console.error('❌ Error actualizando base de conocimiento:', error)
    }
  }

  /**
   * 📈 Obtener Métricas del Sistema
   */
  async obtenerMetricas(): Promise<any> {
    const totalInteracciones = this.interacciones.length
    const cotizacionesGeneradas = this.interacciones.filter(i => i.cotizacion_generada).length
    const conversiones = this.interacciones.filter(i => i.conversion).length
    const tasaConversion = conversiones / cotizacionesGeneradas || 0
    
    return {
      total_interacciones: totalInteracciones,
      cotizaciones_generadas: cotizacionesGeneradas,
      conversiones: conversiones,
      tasa_conversion: tasaConversion,
      patrones_identificados: this.patronesVenta.length,
      productos_conocidos: this.conocimientoProductos.length,
      confianza_promedio: this.calcularConfianzaPromedio()
    }
  }

  // Métodos auxiliares
  private generarId(): string {
    return `int_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }

  private calcularSimilitud(texto1: string, texto2: string): number {
    // Implementación simple de similitud (en producción usar embedding)
    const palabras1 = texto1.toLowerCase().split(' ')
    const palabras2 = texto2.toLowerCase().split(' ')
    const interseccion = palabras1.filter(p => palabras2.includes(p))
    return interseccion.length / Math.max(palabras1.length, palabras2.length)
  }

  private extraerProductosDeConsulta(consulta: string): string[] {
    const productos = Object.keys(PRODUCTOS)
    return productos.filter(producto => 
      consulta.toLowerCase().includes(producto.toLowerCase())
    )
  }

  private extraerServiciosDeConsulta(consulta: string): string[] {
    const servicios = Object.keys(SERVICIOS_ADICIONALES)
    return servicios.filter(servicio => 
      consulta.toLowerCase().includes(servicio.toLowerCase())
    )
  }

  private contarFrecuencias(items: string[]): Record<string, number> {
    return items.reduce((acc, item) => {
      acc[item] = (acc[item] || 0) + 1
      return acc
    }, {} as Record<string, number>)
  }

  private detectarZonaPorTelefono(telefono: string): string {
    const codigos: { [key: string]: string } = {
      '2': 'montevideo',
      '4': 'canelones',
      '5': 'fray_bentos',
      '6': 'colonia'
    }
    const codigoArea = telefono.slice(0, 1)
    return codigos[codigoArea] || 'montevideo'
  }

  private calcularConfianzaPromedio(): number {
    if (this.interacciones.length === 0) return 0
    return this.interacciones.reduce((sum, i) => sum + (i.satisfaccion || 0.5), 0) / this.interacciones.length
  }

  // Métodos de carga de datos (implementar según necesidades)
  private async cargarPatronesVenta() {
    // Implementar carga de patrones desde MongoDB
  }

  private async cargarConocimientoProductos() {
    // Implementar carga de conocimiento desde MongoDB
  }

  private async cargarInteraccionesHistoricas() {
    // Implementar carga de interacciones desde MongoDB
  }

  private async analizarNuevasInteracciones() {
    // Implementar análisis de nuevas interacciones
  }

  private async actualizarPatronesVenta() {
    // Implementar actualización de patrones
  }

  private async actualizarConocimientoProductos() {
    // Implementar actualización de conocimiento
  }
}

// Exportar instancia singleton
export const motorCotizacionIntegrado = new MotorCotizacionIntegrado()
