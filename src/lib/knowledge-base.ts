import connectMongoose from './mongoose'
import Product from '../models/Product'
import { GENERATED_PRODUCTS } from './generated-products'

// Mapping of internal product keys to BMC Website Variant IDs
export const PRODUCT_Variant_MAP: Record<string, string> = {
  'isodec': '51643831419194',
  '01082025': '51643831419194'
};

export function generateCartLink(productKey: string, quantity: number): string | null {
  const variantId = PRODUCT_Variant_MAP[productKey.toLowerCase()];
  if (variantId) {
    return `https://bmcuruguay.com.uy/cart/${variantId}:${quantity}`;
  }
  return null;
}

/**
 * @deprecated Use Database instead. Keeping for backward compatibility.
 */
export const PRODUCTOS: Record<string, any> = {
  ...GENERATED_PRODUCTS,
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
  detalles?: string
  cartLink?: string | null
}

/**
 * Calculates a quote using MongoDB data (Async).
 * Falls back to legacy logic if product not found in DB.
 */
export async function calculateFullQuote(request: CotizacionRequest): Promise<CotizacionResult> {
  const { producto, dimensiones, servicios = [], cantidad = 1 } = request

  if (!producto || typeof producto !== 'string') {
    throw new Error(`Error generando cotización: producto inválido o no proporcionado`)
  }

  try {
    await connectMongoose();
    const productSlug = producto.toLowerCase();
    const productoDB = await Product.findOne({ slug: productSlug });

    if (!productoDB) {
      console.warn(`Product '${producto}' not found in MongoDB. Falling back to static data.`);
      return calculateFullQuoteLegacy(request);
    }

    // Using Base Price from DB as unit price
    // Note: Python system had flat prices, TS system had thickness-based prices.
    // Ideally we should have a price matrix in DB. For now, using Base Price as strict Authority.
    const precioUnitario = productoDB.basePrice;

    // Calculate Area
    const area = dimensiones.ancho * dimensiones.largo;
    const totalArea = area * cantidad;

    const subtotal = totalArea * precioUnitario;

    // Services (Simple 10% logic preserved from original)
    const costoPorServicio = subtotal * 0.1;
    const costoServicios = servicios.length * costoPorServicio;

    const total = subtotal + costoServicios;

    // Volume discount > 10 units
    const descuento = cantidad > 10 ? total * 0.05 : 0;
    const precioFinal = total - descuento;

    return {
      producto: productoDB.name,
      dimensiones: `${dimensiones.ancho}m x ${dimensiones.largo}m x ${dimensiones.espesor}mm`,
      cantidad,
      precioUnitario,
      subtotal,
      servicios,
      total,
      descuento: descuento > 0 ? descuento : undefined,
      precioFinal,
      cartLink: generateCartLink(producto, cantidad)
    };

  } catch (error) {
    console.error("Error in calculateFullQuote (DB):", error);
    // Fallback on error logic
    return calculateFullQuoteLegacy(request);
  }
}

/**
 * @deprecated Legacy static calculation
 */
export function calculateFullQuoteLegacy(request: CotizacionRequest): CotizacionResult {
  const { producto, dimensiones, servicios = [], cantidad = 1 } = request

  if (!producto || typeof producto !== 'string') {
    throw new Error(`Error generando cotización: producto inválido o no proporcionado`)
  }

  const productoData = PRODUCTOS[producto.toLowerCase() as keyof typeof PRODUCTOS]

  if (!productoData) {
    throw new Error(`Producto no encontrado: ${producto}`)
  }

  // Find price key directly (e.g. '100mm')
  const espesorKey = `${dimensiones.espesor}mm`
  let precioUnitario: number = 0;

  if (productoData.precios && productoData.precios[espesorKey]) {
    precioUnitario = productoData.precios[espesorKey];
  } else {
    // If specific thickness not found, try to find a default or throw
    // For legacy safety, let's look for any price or default to 0 (and log error?)
    // Original code threw error.
    const prices = Object.values(productoData.precios) as number[];
    if (prices.length > 0) precioUnitario = prices[0];
    else throw new Error(`Espesor no disponible: ${espesorKey}`);
  }

  // Calculate logic including 'anchoUtil' if variants exist (legacy complex logic)
  let areaReal = dimensiones.ancho * dimensiones.largo
  let numPaneles = cantidad
  let desgloseArea: string | undefined

  // Check for variants/width logic
  let anchoUtil: number | null = null;
  // @ts-ignore
  if (productoData.variantes && Array.isArray(productoData.variantes)) {
    // @ts-ignore
    const variant = productoData.variantes.find((v: any) => v.thickness === espesorKey || v.thickness === null);
    if (variant && variant.width) {
      anchoUtil = variant.width;
    } else {
      // @ts-ignore
      const anyVariant = productoData.variantes.find((v: any) => v.width);
      if (anyVariant) anchoUtil = anyVariant.width;
    }
  }

  if (anchoUtil) {
    const anchoCobertura = dimensiones.ancho;
    const panelesNecesarios = Math.ceil(anchoCobertura / anchoUtil);
    numPaneles = panelesNecesarios * cantidad;

    areaReal = numPaneles * anchoUtil * dimensiones.largo;
    desgloseArea = `${panelesNecesarios} paneles de ${anchoUtil}m x ${dimensiones.largo}m`;
  } else {
    // Simple calculation
    areaReal = areaReal * cantidad; // Total area
  }

  const subtotal = areaReal * precioUnitario
  const costoPorServicio = subtotal * 0.1
  const costoServicios = servicios.length * costoPorServicio
  const total = subtotal + costoServicios
  const descuento = numPaneles > 10 ? total * 0.05 : 0
  const precioFinal = total - descuento

  return {
    producto: productoData.nombre,
    dimensiones: `${dimensiones.ancho}m x ${dimensiones.largo}m x ${dimensiones.espesor}mm`,
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
  if (!producto || typeof producto !== 'string') return []
  const productoData = PRODUCTOS[producto.toLowerCase() as keyof typeof PRODUCTOS]
  if (!productoData || !productoData.precios) return []
  return Object.keys(productoData.precios)
}

export function obtenerPrecio(producto: string, espesor: string): number | null {
  if (!producto || typeof producto !== 'string') return null
  const productoData = PRODUCTOS[producto.toLowerCase() as keyof typeof PRODUCTOS]
  if (!productoData || !productoData.precios) return null
  return productoData.precios[espesor as keyof typeof productoData.precios] || null
}