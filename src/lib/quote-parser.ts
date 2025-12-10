import { OpenAI } from 'openai'
import { secureConfig } from './secure-config'

// Inicializar OpenAI con configuración segura
function getOpenAIClient(): OpenAI {
  if (!secureConfig.isReady()) {
    throw new Error('SecureConfig not initialized. Call initializeSecureConfig() first.')
  }

  const config = secureConfig.getOpenAIConfig()
  return new OpenAI({
    apiKey: config.apiKey
  })
}

export interface ParsedQuote {
  producto: {
    tipo: string
    grosor?: string | null
    color?: string | null
    cantidad?: number | null
    unidad?: 'paneles' | 'm2' | 'ml' | 'unidades' | null
  }
  dimensiones?: {
    largo?: number | null
    ancho?: number | null
    alto?: number | null
    area_m2?: number | null
  }
  servicios: {
    flete: boolean
    instalacion: boolean
    accesorios: boolean
  }
  estado_info: 'completo' | 'pendiente_info' | 'ver_plano'
  notas?: string | null
  confianza: number // 0-1, qué tan seguro está el parser
}

export async function parseQuoteConsulta(consultaText: string): Promise<ParsedQuote> {
  const openai = getOpenAIClient()

  const prompt = `Eres un experto en productos de construcción (paneles aislantes, chapas, etc.) especializado en el mercado uruguayo.

Extrae información estructurada de esta consulta de cotización:

"${consultaText}"

Identifica y extrae:
1. Tipo de producto (Isodec, Isoroof, Isopanel, Isowall, Chapas, Calamería, etc.)
2. Grosor en mm (si se menciona: 50, 100, 150, 200mm)
3. Cantidades y unidades (paneles, m2, ml, unidades)
4. Dimensiones específicas (largo x ancho x alto)
5. Color/acabado (blanco, gris, etc.)
6. Servicios: flete, instalación, accesorios
7. Estado: completo | pendiente_info | ver_plano

Productos comunes en Uruguay:
- Isodec (paneles aislantes EPS)
- Isoroof (paneles para techo)
- Isopanel (paneles generales)
- Isowall (paneles para paredes)
- Chapas (metálicas)
- Calamería (estructura metálica)

Servicios comunes:
- "+ flete" = incluir transporte
- "+ instalación" / "completo" = instalación incluida
- "+ accesorios" = accesorios incluidos

Estados especiales:
- "aguardo info" / "ESPERO INFO" = pendiente_info
- "Ver plano" = ver_plano
- Información completa = completo

Responde SOLO con JSON válido siguiendo este esquema exacto:
{
  "producto": {
    "tipo": "string",
    "grosor": "string o null",
    "color": "string o null", 
    "cantidad": "number o null",
    "unidad": "paneles|m2|ml|unidades o null"
  },
  "dimensiones": {
    "largo": "number o null",
    "ancho": "number o null", 
    "alto": "number o null",
    "area_m2": "number o null"
  },
  "servicios": {
    "flete": "boolean",
    "instalacion": "boolean",
    "accesorios": "boolean"
  },
  "estado_info": "completo|pendiente_info|ver_plano",
  "notas": "string o null",
  "confianza": "number entre 0 y 1"
}`

  try {
    const completion = await openai.chat.completions.create({
      model: 'gpt-4o',
      messages: [{ role: 'user', content: prompt }],
      response_format: { type: 'json_object' },
      temperature: 0.1,
      max_tokens: 1000
    })

    const content = completion.choices[0].message.content
    if (!content) {
      throw new Error('No se recibió respuesta de OpenAI')
    }
    const parsed = JSON.parse(content)

    // Validar estructura básica
    if (!parsed.producto || !parsed.servicios || !parsed.estado_info) {
      throw new Error('Invalid response structure from OpenAI')
    }

    return parsed as ParsedQuote
  } catch (error) {
    console.error('Error parsing quote consulta:', error)

    // Fallback parsing básico sin IA
    return parseQuoteFallback(consultaText)
  }
}

// Parser de fallback sin IA
function parseQuoteFallback(consultaText: string): ParsedQuote {
  const text = consultaText.toLowerCase()

  // Detectar tipo de producto
  let tipo = 'Desconocido'
  if (text.includes('isodec')) tipo = 'Isodec'
  else if (text.includes('isoroof')) tipo = 'Isoroof'
  else if (text.includes('isopanel')) tipo = 'Isopanel'
  else if (text.includes('isowall')) tipo = 'Isowall'
  else if (text.includes('chapa')) tipo = 'Chapas'
  else if (text.includes('calamería') || text.includes('calameria')) tipo = 'Calamería'

  // Detectar grosor
  const grosorMatch = text.match(/(\d+)\s*mm/)
  const grosor = grosorMatch ? grosorMatch[1] + 'mm' : null

  // Detectar servicios
  const flete = text.includes('flete') || text.includes('+ flete')
  const instalacion = text.includes('completo') || text.includes('instalación') || text.includes('instalacion')
  const accesorios = text.includes('accesorios') || text.includes('+ accesorios')

  // Detectar estado
  let estado_info: 'completo' | 'pendiente_info' | 'ver_plano' = 'completo'
  if (text.includes('aguardo') || text.includes('espero') || text.includes('falta info')) {
    estado_info = 'pendiente_info'
  } else if (text.includes('ver plano') || text.includes('plano')) {
    estado_info = 'ver_plano'
  }

  // Detectar dimensiones básicas
  const dimensiones: any = {}
  const largoMatch = text.match(/(\d+(?:\.\d+)?)\s*(?:largo|x\s*(\d+(?:\.\d+)?))/)
  if (largoMatch) {
    dimensiones.largo = parseFloat(largoMatch[1])
    if (largoMatch[2]) dimensiones.ancho = parseFloat(largoMatch[2])
  }

  const areaMatch = text.match(/(\d+(?:\.\d+)?)\s*m2/)
  if (areaMatch) {
    dimensiones.area_m2 = parseFloat(areaMatch[1])
  }

  return {
    producto: {
      tipo,
      grosor,
      color: null,
      cantidad: null,
      unidad: null
    },
    dimensiones: Object.keys(dimensiones).length > 0 ? dimensiones : undefined,
    servicios: {
      flete,
      instalacion,
      accesorios
    },
    estado_info,
    notas: null,
    confianza: 0.3 // Baja confianza para fallback
  }
}

// Función para validar si una consulta es válida para cotización
export function isValidQuoteRequest(consultaText: string): boolean {
  const text = consultaText.toLowerCase()

  // Palabras clave que indican una consulta de cotización
  const keywords = [
    'isodec', 'isoroof', 'isopanel', 'isowall', 'chapa', 'calamería', 'calameria',
    'panel', 'techo', 'pared', 'galpón', 'galpon', 'cubierta', 'm2', 'metro',
    'precio', 'cotización', 'presupuesto', 'costo'
  ]

  return keywords.some(keyword => text.includes(keyword))
}

// Función para extraer información de contacto del texto
export function extractContactInfo(text: string): {
  phone?: string
  email?: string
  name?: string
} {
  const phoneMatch = text.match(/(\d{3,4}\s*\d{3,4}\s*\d{3,4})/)
  const emailMatch = text.match(/([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/)
  const nameMatch = text.match(/(?:soy|me llamo|nombre es)\s+([A-Za-z\s]+)/i)

  return {
    phone: phoneMatch ? phoneMatch[1].replace(/\s/g, '') : undefined,
    email: emailMatch ? emailMatch[1] : undefined,
    name: nameMatch ? nameMatch[1].trim() : undefined
  }
}
