// Base de conocimiento para productos BMC
export const PRODUCTOS = {
  'isodec': {
    nombre: 'Isodec',
    descripcion: 'Panel aislante térmico',
    unidad: 'm²',
    precios: {
      '50mm': 45,
      '75mm': 55,
      '100mm': 65,
      '125mm': 75,
      '150mm': 85
    }
  },
  'poliestireno': {
    nombre: 'Poliestireno Expandido',
    descripcion: 'Aislante térmico',
    unidad: 'm²',
    precios: {
      '50mm': 25,
      '75mm': 35,
      '100mm': 45,
      '125mm': 55,
      '150mm': 65
    }
  },
  'lana_roca': {
    nombre: 'Lana de Roca',
    descripcion: 'Aislante térmico y acústico',
    unidad: 'm²',
    precios: {
      '50mm': 30,
      '75mm': 40,
      '100mm': 50,
      '125mm': 60,
      '150mm': 70
    }
  }
}

export const SERVICIOS_ADICIONALES = {
  'instalacion': {
    nombre: 'Instalación',
    costo: 50,
    unidad: 'servicio'
  },
  'transporte': {
    nombre: 'Transporte',
    costo: 30,
    unidad: 'servicio'
  },
  'corte_medida': {
    nombre: 'Corte a medida',
    costo: 20,
    unidad: 'servicio'
  }
}

export const ZONAS_FLETE = {
  'montevideo': {
    nombre: 'Montevideo',
    costo: 0,
    dias: 1
  },
  'canelones': {
    nombre: 'Canelones',
    costo: 15,
    dias: 2
  },
  'maldonado': {
    nombre: 'Maldonado',
    costo: 25,
    dias: 2
  },
  'interior': {
    nombre: 'Interior',
    costo: 40,
    dias: 3
  }
}

export interface CotizacionRequest {
  producto: string
  dimensiones: {
    ancho: number
    largo: number
    espesor: number
  }
  servicios?: string[]
  cantidad?: number
}

export interface CotizacionResult {
  producto: string
  dimensiones: string
  cantidad: number
  precioUnitario: number
  subtotal: number
  servicios: string[]
  total: number
  descuento?: number
  precioFinal: number
}

export function calculateFullQuote(request: CotizacionRequest): CotizacionResult {
  const { producto, dimensiones, servicios = [], cantidad = 1 } = request
  
  // Buscar producto en la base de conocimiento
  const productoData = PRODUCTOS[producto.toLowerCase() as keyof typeof PRODUCTOS]
  
  if (!productoData) {
    throw new Error(`Producto no encontrado: ${producto}`)
  }
  
  // Calcular área
  const area = dimensiones.ancho * dimensiones.largo
  
  // Buscar precio por espesor
  const espesorKey = `${dimensiones.espesor}mm`
  const precioUnitario = productoData.precios[espesorKey as keyof typeof productoData.precios]
  
  if (!precioUnitario) {
    throw new Error(`Espesor no disponible: ${espesorKey}`)
  }
  
  // Calcular subtotal
  const subtotal = area * precioUnitario * cantidad
  
  // Calcular servicios (10% del subtotal por servicio)
  const costoPorServicio = subtotal * 0.1
  const costoServicios = servicios.length * costoPorServicio
  
  // Calcular total
  const total = subtotal + costoServicios
  
  // Aplicar descuento por volumen (5% si cantidad > 10)
  const descuento = cantidad > 10 ? total * 0.05 : 0
  const precioFinal = total - descuento
  
  return {
    producto: productoData.nombre,
    dimensiones: `${dimensiones.ancho}m x ${dimensiones.largo}m x ${dimensiones.espesor}mm`,
    cantidad,
    precioUnitario,
    subtotal,
    servicios,
    total,
    descuento: descuento > 0 ? descuento : undefined,
    precioFinal
  }
}

export function buscarProducto(termino: string): string | null {
  const terminoLower = termino.toLowerCase()
  
  for (const [key, producto] of Object.entries(PRODUCTOS)) {
    if (
      key.includes(terminoLower) ||
      producto.nombre.toLowerCase().includes(terminoLower) ||
      producto.descripcion.toLowerCase().includes(terminoLower)
    ) {
      return key
    }
  }
  
  return null
}

export function obtenerEspesoresDisponibles(producto: string): string[] {
  const productoData = PRODUCTOS[producto.toLowerCase() as keyof typeof PRODUCTOS]
  
  if (!productoData) {
    return []
  }
  
  return Object.keys(productoData.precios)
}

export function obtenerPrecio(producto: string, espesor: string): number | null {
  const productoData = PRODUCTOS[producto.toLowerCase() as keyof typeof PRODUCTOS]
  
  if (!productoData) {
    return null
  }
  
  return productoData.precios[espesor as keyof typeof productoData.precios] || null
}