import { GENERATED_PRODUCTS, ProductoDefinicion } from './generated-products'

// Base de conocimiento para productos BMC
// Mapping of internal product keys to BMC Website Variant IDs
export const PRODUCT_Variant_MAP: Record<string, string> = {
  // Isodec 50mm Blanco (Example from scrape)
  'isodec': '51643831419194',
  '01082025': '51643831419194' // Fallback for the generated name
};

export function generateCartLink(productKey: string, quantity: number): string | null {
  const variantId = PRODUCT_Variant_MAP[productKey.toLowerCase()];
  if (variantId) {
    // Shopify Permalink format: /cart/{variant_id}:{quantity}
    return `https://bmcuruguay.com.uy/cart/${variantId}:${quantity}`;
  }
  return null;
}

// Se combina la data generada automÃ¡ticamente con overrides manuales si es necesario
export const PRODUCTOS: Record<string, any> = {
  ...GENERATED_PRODUCTS,
  // Overrides manuales o productos que no estÃ¡n en los ODS
  'isodec_manual': {
    nombre: 'Isodec (Manual)',
    descripcion: 'Panel aislante tÃ©rmico (Backup Manual)',
    unidad: 'mÂ²',
    precios: {
      '50mm': 45,
      '100mm': 65,
      '150mm': 85
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
    dias: 0
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
  detalles?: string
  cartLink?: string | null
}

export function calculateFullQuote(request: CotizacionRequest): CotizacionResult {
  const { producto, dimensiones, servicios = [], cantidad = 1 } = request

  // Validar que producto existe
  if (!producto || typeof producto !== 'string') {
    throw new Error(`Error generando cotización: producto inválido o no proporcionado`)
  }

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

  // Detectar ancho útil del producto (si existe en variantes)
  let anchoUtil: number | null = null;
  if (productoData.variantes && Array.isArray(productoData.variantes)) {
    // Buscar variante que coincida con el espesor
    // Nota: la logica de variantes puede ser compleja, buscamos la primera que tenga width definido y coincida aprox o sea genérica
    // Por ahora, asumimos que todos los del mismo grupo tienen ancho similar o buscamos match de espesor
    const variant = productoData.variantes.find((v: any) => v.thickness === espesorKey || v.thickness === null);
    if (variant && variant.width) {
      anchoUtil = variant.width;
    } else {
      // Fallback: buscar cualquier variante con width en este grupo
      const anyVariant = productoData.variantes.find((v: any) => v.width);
      if (anyVariant) anchoUtil = anyVariant.width;
    }
  }

  // Calcular cantidad de paneles y área real
  let areaReal = dimensiones.ancho * dimensiones.largo;
  let numPaneles = cantidad; // Default si no se calcula por ancho
  let desgloseArea = `${areaReal.toFixed(2)}m²`;

  if (anchoUtil) {
    // Si tenemos ancho útil, calculamos cuántos paneles se necesitan para cubrir el ancho
    const anchoCobertura = dimensiones.ancho;
    const panelesNecesarios = Math.ceil(anchoCobertura / anchoUtil);
    numPaneles = panelesNecesarios * cantidad; // Multiplicamos por cantidad de estructuras iguales solicitadas

    // El área a cobrar es el área de los paneles completos
    areaReal = numPaneles * anchoUtil * dimensiones.largo;
    desgloseArea = `${panelesNecesarios} paneles de ${anchoUtil}m x ${dimensiones.largo}m (Total cobertura: ${(panelesNecesarios * anchoUtil).toFixed(2)}m de ancho)`;
  }

  // Calcular subtotal
  const subtotal = areaReal * precioUnitario

  // Calcular servicios (10% del subtotal por servicio)
  const costoPorServicio = subtotal * 0.1
  const costoServicios = servicios.length * costoPorServicio

  // Calcular total
  const total = subtotal + costoServicios

  // Aplicar descuento por volumen (5% si cantidad o paneles > 10)
  const descuento = numPaneles > 10 ? total * 0.05 : 0
  const precioFinal = total - descuento

  return {
    producto: productoData.nombre,
    dimensiones: `Ancho Total: ${dimensiones.ancho}m, Largo: ${dimensiones.largo}m, Espesor: ${dimensiones.espesor}mm`,
    cantidad: numPaneles,
    precioUnitario,
    subtotal,
    servicios,
    total,
    descuento: descuento > 0 ? descuento : undefined,
    precioFinal,
    detalles: anchoUtil ? `Cálculo basado en ancho útil de ${anchoUtil}m. ${desgloseArea}` : undefined,
    cartLink: generateCartLink(producto, numPaneles)
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
  if (!producto || typeof producto !== 'string') {
    return []
  }

  const productoData = PRODUCTOS[producto.toLowerCase() as keyof typeof PRODUCTOS]

  if (!productoData) {
    return []
  }

  return Object.keys(productoData.precios)
}

export function obtenerPrecio(producto: string, espesor: string): number | null {
  if (!producto || typeof producto !== 'string') {
    return null
  }

  const productoData = PRODUCTOS[producto.toLowerCase() as keyof typeof PRODUCTOS]

  if (!productoData) {
    return null
  }

  return productoData.precios[espesor as keyof typeof productoData.precios] || null
}