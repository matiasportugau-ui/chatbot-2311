// Base de Conocimiento para Sistema de Cotización BMC
// Basada en análisis del Google Sheet y productos identificados

export interface Product {
  id: string
  nombre: string
  categoria: 'paneles' | 'chapas' | 'calameria' | 'accesorios' | 'servicios'
  subcategoria?: string
  descripcion: string
  especificaciones: {
    grosor?: number[] // en mm
    colores?: string[]
    dimensiones?: {
      largo?: number[]
      ancho?: number[]
      alto?: number[]
    }
    unidades?: string[]
  }
  precios: {
    base: number // precio por m2 o unidad
    unidad: 'm2' | 'ml' | 'unidad' | 'panel'
    variaciones?: {
      grosor?: { [key: number]: number } // multiplicador por grosor
      color?: { [key: string]: number } // multiplicador por color
    }
  }
  servicios: {
    instalacion: boolean
    flete: boolean
    accesorios: boolean
  }
  aplicaciones: string[]
  sinonimos: string[]
  palabras_clave: string[]
}

export interface CotizacionRule {
  id: string
  nombre: string
  condicion: (parsed: any) => boolean
  accion: (parsed: any, base: Product) => {
    precio: number
    descripcion: string
    recomendaciones: string[]
  }
  prioridad: number
}

export interface KnowledgeBase {
  productos: Product[]
  reglas: CotizacionRule[]
  zonas: {
    [key: string]: {
      nombre: string
      flete_base: number
      multiplicador: number
      observaciones?: string
    }
  }
  servicios: {
    instalacion: {
      base: number
      por_m2: number
      minimo: number
    }
    flete: {
      base: number
      por_km: number
      minimo: number
    }
    accesorios: {
      [key: string]: {
        precio: number
        descripcion: string
        requerido_con?: string[]
      }
    }
  }
}

// Base de datos de productos BMC
export const PRODUCTOS_BMC: Product[] = [
  {
    id: 'isodec_50',
    nombre: 'Isodec EPS',
    categoria: 'paneles',
    subcategoria: 'aislante',
    descripcion: 'Panel aislante de poliestireno expandido (EPS) para paredes y techos',
    especificaciones: {
      grosor: [50, 100, 150, 200],
      colores: ['blanco', 'gris', 'personalizado'],
      dimensiones: {
        largo: [3000, 6000, 12000],
        ancho: [1000, 1200],
        alto: [50, 100, 150, 200]
      },
      unidades: ['m2', 'panel']
    },
    precios: {
      base: 45, // USD por m2
      unidad: 'm2',
      variaciones: {
        grosor: {
          50: 1.0,
          100: 1.3,
          150: 1.6,
          200: 2.0
        },
        color: {
          'blanco': 1.0,
          'gris': 1.1,
          'personalizado': 1.3
        }
      }
    },
    servicios: {
      instalacion: true,
      flete: true,
      accesorios: true
    },
    aplicaciones: ['paredes', 'techos', 'galpones', 'naves industriales'],
    sinonimos: ['isodec', 'panel eps', 'aislante eps', 'panel aislante'],
    palabras_clave: ['isodec', 'eps', 'aislante', 'panel', 'poliestireno']
  },
  {
    id: 'isoroof_30',
    nombre: 'Isoroof',
    categoria: 'paneles',
    subcategoria: 'techo',
    descripcion: 'Panel aislante para techos con acabado metálico',
    especificaciones: {
      grosor: [30, 50, 80],
      colores: ['blanco', 'gris', 'rojo', 'azul'],
      dimensiones: {
        largo: [3000, 6000, 12000],
        ancho: [1000, 1200]
      },
      unidades: ['m2', 'panel']
    },
    precios: {
      base: 65,
      unidad: 'm2',
      variaciones: {
        grosor: {
          30: 1.0,
          50: 1.2,
          80: 1.5
        }
      }
    },
    servicios: {
      instalacion: true,
      flete: true,
      accesorios: true
    },
    aplicaciones: ['techos', 'cubiertas', 'galpones'],
    sinonimos: ['isoroof', 'panel techo', 'cubierta aislante'],
    palabras_clave: ['isoroof', 'techo', 'cubierta', 'panel techo']
  },
  {
    id: 'isopanel_general',
    nombre: 'Isopanel',
    categoria: 'paneles',
    subcategoria: 'general',
    descripcion: 'Panel aislante de uso general para construcción',
    especificaciones: {
      grosor: [50, 100, 150, 200, 250],
      colores: ['blanco', 'gris'],
      dimensiones: {
        largo: [3000, 6000, 12000],
        ancho: [1000, 1200]
      },
      unidades: ['m2', 'panel']
    },
    precios: {
      base: 55,
      unidad: 'm2',
      variaciones: {
        grosor: {
          50: 1.0,
          100: 1.2,
          150: 1.4,
          200: 1.7,
          250: 2.0
        }
      }
    },
    servicios: {
      instalacion: true,
      flete: true,
      accesorios: true
    },
    aplicaciones: ['paredes', 'techos', 'divisiones'],
    sinonimos: ['isopanel', 'panel general', 'panel construcción'],
    palabras_clave: ['isopanel', 'panel', 'construcción', 'general']
  },
  {
    id: 'isowall_50',
    nombre: 'Isowall',
    categoria: 'paneles',
    subcategoria: 'pared',
    descripcion: 'Panel aislante específico para paredes exteriores',
    especificaciones: {
      grosor: [50, 100, 150],
      colores: ['blanco', 'gris'],
      dimensiones: {
        largo: [3000, 6000],
        ancho: [1000, 1200]
      },
      unidades: ['m2', 'panel']
    },
    precios: {
      base: 50,
      unidad: 'm2',
      variaciones: {
        grosor: {
          50: 1.0,
          100: 1.3,
          150: 1.6
        }
      }
    },
    servicios: {
      instalacion: true,
      flete: true,
      accesorios: true
    },
    aplicaciones: ['paredes exteriores', 'fachadas', 'divisiones'],
    sinonimos: ['isowall', 'panel pared', 'pared aislante'],
    palabras_clave: ['isowall', 'pared', 'fachada', 'exterior']
  },
  {
    id: 'chapa_galvanizada',
    nombre: 'Chapa Galvanizada',
    categoria: 'chapas',
    subcategoria: 'metalica',
    descripcion: 'Chapa de acero galvanizado para techos y paredes',
    especificaciones: {
      grosor: [0.30, 0.41, 0.50],
      colores: ['galvanizado', 'pintado'],
      dimensiones: {
        largo: [3000, 6000, 12000],
        ancho: [1000, 1200]
      },
      unidades: ['m2', 'chapa']
    },
    precios: {
      base: 25,
      unidad: 'm2',
      variaciones: {
        grosor: {
          0.30: 1.0,
          0.41: 1.2,
          0.50: 1.4
        }
      }
    },
    servicios: {
      instalacion: true,
      flete: true,
      accesorios: true
    },
    aplicaciones: ['techos', 'paredes', 'galpones'],
    sinonimos: ['chapa', 'galvanizada', 'acero', 'techo metálico'],
    palabras_clave: ['chapa', 'galvanizada', 'acero', 'metal']
  },
  {
    id: 'calameria_estructura',
    nombre: 'Calamería',
    categoria: 'calameria',
    subcategoria: 'estructura',
    descripcion: 'Estructura metálica para soporte de paneles y chapas',
    especificaciones: {
      grosor: [1.5, 2.0, 2.5],
      colores: ['galvanizado', 'pintado'],
      dimensiones: {
        largo: [3000, 6000, 12000]
      },
      unidades: ['ml', 'kg']
    },
    precios: {
      base: 15,
      unidad: 'ml',
      variaciones: {
        grosor: {
          1.5: 1.0,
          2.0: 1.3,
          2.5: 1.6
        }
      }
    },
    servicios: {
      instalacion: true,
      flete: true,
      accesorios: false
    },
    aplicaciones: ['estructura', 'soporte', 'galpones'],
    sinonimos: ['calameria', 'estructura', 'perfil', 'viga'],
    palabras_clave: ['calameria', 'estructura', 'perfil', 'soporte']
  }
]

// Zonas de flete en Uruguay
export const ZONAS_FLETE = {
  'montevideo': {
    nombre: 'Montevideo',
    flete_base: 50,
    multiplicador: 1.0,
    observaciones: 'Zona metropolitana'
  },
  'canelones': {
    nombre: 'Canelones',
    flete_base: 80,
    multiplicador: 1.2,
    observaciones: 'Incluye Pando, Las Piedras, Ciudad de la Costa'
  },
  'maldonado': {
    nombre: 'Maldonado',
    flete_base: 120,
    multiplicador: 1.5,
    observaciones: 'Incluye Punta del Este, Piriápolis'
  },
  'rivera': {
    nombre: 'Rivera',
    flete_base: 200,
    multiplicador: 2.0,
    observaciones: 'Zona fronteriza'
  },
  'artigas': {
    nombre: 'Artigas',
    flete_base: 250,
    multiplicador: 2.5,
    observaciones: 'Zona norte'
  },
  'fray_bentos': {
    nombre: 'Fray Bentos',
    flete_base: 180,
    multiplicador: 1.8,
    observaciones: 'Río Negro'
  },
  'colonia': {
    nombre: 'Colonia',
    flete_base: 150,
    multiplicador: 1.6,
    observaciones: 'Colonia del Sacramento'
  }
}

// Servicios adicionales
export const SERVICIOS_ADICIONALES = {
  instalacion: {
    base: 100,
    por_m2: 15,
    minimo: 200
  },
  flete: {
    base: 50,
    por_km: 2.5,
    minimo: 80
  },
  accesorios: {
    'babetas': {
      precio: 25,
      descripcion: 'Babetas de terminación',
      requerido_con: ['isodec', 'isoroof', 'isopanel']
    },
    'gotero': {
      precio: 30,
      descripcion: 'Gotero frontal',
      requerido_con: ['isoroof', 'chapa']
    },
    'remates': {
      precio: 20,
      descripcion: 'Remates de esquina',
      requerido_con: ['isodec', 'isopanel', 'isowall']
    },
    'juntas': {
      precio: 15,
      descripcion: 'Juntas de dilatación',
      requerido_con: ['isodec', 'isoroof', 'isopanel']
    }
  }
}

// Reglas de cotización inteligentes
export const REGLAS_COTIZACION: CotizacionRule[] = [
  {
    id: 'galpon_completo',
    nombre: 'Galpón Completo',
    condicion: (parsed) => 
      parsed.dimensiones?.largo && parsed.dimensiones?.ancho && parsed.dimensiones?.alto &&
      parsed.producto?.tipo?.toLowerCase().includes('isodec'),
    accion: (parsed, base) => {
      const area = (parsed.dimensiones.largo * parsed.dimensiones.ancho) / 10000 // m2
      const precio = area * base.precios.base * (base.precios.variaciones?.grosor?.[parsed.producto.grosor] || 1)
      
      return {
        precio: Math.round(precio),
        descripcion: `Galpón completo de ${parsed.dimensiones.largo}m x ${parsed.dimensiones.ancho}m x ${parsed.dimensiones.alto}m`,
        recomendaciones: [
          'Incluir estructura de calameria',
          'Considerar accesorios de terminación',
          'Verificar cimentación existente'
        ]
      }
    },
    prioridad: 1
  },
  {
    id: 'techo_solo',
    nombre: 'Solo Techo',
    condicion: (parsed) => 
      parsed.consulta_original?.toLowerCase().includes('techo') &&
      !parsed.consulta_original?.toLowerCase().includes('pared'),
    accion: (parsed, base) => {
      const area = parsed.dimensiones?.area_m2 || 50 // default 50m2
      const precio = area * base.precios.base
      
      return {
        precio: Math.round(precio),
        descripcion: `Cubierta de techo de ${area}m²`,
        recomendaciones: [
          'Verificar inclinación mínima 5%',
          'Incluir sistema de drenaje',
          'Considerar aislación térmica'
        ]
      }
    },
    prioridad: 2
  },
  {
    id: 'paredes_exteriores',
    nombre: 'Paredes Exteriores',
    condicion: (parsed) => 
      parsed.consulta_original?.toLowerCase().includes('pared') &&
      parsed.producto?.tipo?.toLowerCase().includes('isowall'),
    accion: (parsed, base) => {
      const area = parsed.dimensiones?.area_m2 || 100 // default 100m2
      const precio = area * base.precios.base
      
      return {
        precio: Math.round(precio),
        descripcion: `Paredes exteriores de ${area}m²`,
        recomendaciones: [
          'Incluir sistema de fijación',
          'Considerar juntas de dilatación',
          'Verificar resistencia al viento'
        ]
      }
    },
    prioridad: 3
  }
]

// Base de conocimiento completa
export const KNOWLEDGE_BASE: KnowledgeBase = {
  productos: PRODUCTOS_BMC,
  reglas: REGLAS_COTIZACION,
  zonas: ZONAS_FLETE,
  servicios: SERVICIOS_ADICIONALES
}

// Función para buscar productos por consulta
export function buscarProductos(consulta: string): Product[] {
  const consultaLower = consulta.toLowerCase()
  
  return PRODUCTOS_BMC.filter(producto => 
    producto.sinonimos.some(sinonimo => consultaLower.includes(sinonimo.toLowerCase())) ||
    producto.palabras_clave.some(palabra => consultaLower.includes(palabra.toLowerCase())) ||
    producto.nombre.toLowerCase().includes(consultaLower)
  )
}

// Función para calcular precio base
export function calcularPrecioBase(producto: Product, parsed: any): number {
  let precio = producto.precios.base
  
  // Aplicar variaciones por grosor
  if (parsed.producto?.grosor && producto.precios.variaciones?.grosor) {
    const grosor = parseInt(parsed.producto.grosor.replace('mm', ''))
    const multiplicador = producto.precios.variaciones.grosor[grosor] || 1
    precio *= multiplicador
  }
  
  // Aplicar variaciones por color
  if (parsed.producto?.color && producto.precios.variaciones?.color) {
    const multiplicador = producto.precios.variaciones.color[parsed.producto.color] || 1
    precio *= multiplicador
  }
  
  return precio
}

// Función para calcular servicios adicionales
export function calcularServiciosAdicionales(parsed: any, zona: string = 'montevideo'): {
  instalacion: number
  flete: number
  accesorios: number
  total: number
} {
  const area = parsed.dimensiones?.area_m2 || 50
  const zonaData = ZONAS_FLETE[zona as keyof typeof ZONAS_FLETE] || ZONAS_FLETE.montevideo
  
  const instalacion = Math.max(
    SERVICIOS_ADICIONALES.instalacion.base + (area * SERVICIOS_ADICIONALES.instalacion.por_m2),
    SERVICIOS_ADICIONALES.instalacion.minimo
  )
  
  const flete = zonaData.flete_base * zonaData.multiplicador
  
  let accesorios = 0
  if (parsed.servicios?.accesorios) {
    // Calcular accesorios según el producto
    const producto = buscarProductos(parsed.producto?.tipo || '')[0]
    if (producto) {
      Object.values(SERVICIOS_ADICIONALES.accesorios).forEach(acc => {
        if (acc.requerido_con?.some(prod => producto.sinonimos.includes(prod))) {
          accesorios += acc.precio
        }
      })
    }
  }
  
  return {
    instalacion: Math.round(instalacion),
    flete: Math.round(flete),
    accesorios: Math.round(accesorios),
    total: Math.round(instalacion + flete + accesorios)
  }
}

// Función para generar cotización completa
export function generarCotizacion(parsed: any, zona: string = 'montevideo'): {
  producto: Product | null
  precio_base: number
  area: number
  servicios: any
  total: number
  recomendaciones: string[]
  descripcion: string
} {
  const productos = buscarProductos(parsed.producto?.tipo || parsed.consulta_original || '')
  const producto = productos[0] || null
  
  if (!producto) {
    return {
      producto: null,
      precio_base: 0,
      area: 0,
      servicios: { instalacion: 0, flete: 0, accesorios: 0, total: 0 },
      total: 0,
      recomendaciones: ['Producto no identificado. Contactar para cotización personalizada.'],
      descripcion: 'Producto no encontrado en base de datos'
    }
  }
  
  const area = parsed.dimensiones?.area_m2 || 
    (parsed.dimensiones?.largo && parsed.dimensiones?.ancho ? 
      (parsed.dimensiones.largo * parsed.dimensiones.ancho) / 10000 : 50)
  
  const precio_base = calcularPrecioBase(producto, parsed) * area
  const servicios = calcularServiciosAdicionales(parsed, zona)
  
  // Aplicar reglas de cotización
  let recomendaciones: string[] = []
  let descripcion = `${producto.nombre} - ${area}m²`
  
  for (const regla of REGLAS_COTIZACION) {
    if (regla.condicion(parsed)) {
      const resultado = regla.accion(parsed, producto)
      recomendaciones = [...recomendaciones, ...resultado.recomendaciones]
      descripcion = resultado.descripcion
      break
    }
  }
  
  const total = Math.round(precio_base + servicios.total)
  
  return {
    producto,
    precio_base: Math.round(precio_base),
    area: Math.round(area * 100) / 100,
    servicios,
    total,
    recomendaciones,
    descripcion
  }
}
