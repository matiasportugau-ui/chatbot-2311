export interface Quote {
  _id?: string
  arg: string
  estado: 'Pendiente' | 'Adjunto' | 'Listo' | 'Enviado' | 'Asignado' | 'Confirmado'
  fecha: string
  cliente: string
  origen: 'WA' | 'LO' | 'EM' | 'CL'
  telefono: string
  direccion: string
  consulta: string
  
  // Datos parseados por IA
  parsed?: {
    producto: {
      tipo: string
      grosor?: string
      color?: string
      cantidad?: number
      unidad?: string
    }
    dimensiones?: {
      largo?: number
      ancho?: number
      alto?: number
      area_m2?: number
    }
    servicios: {
      flete: boolean
      instalacion: boolean
      accesorios: boolean
    }
    estado_info: 'completo' | 'pendiente_info' | 'ver_plano'
    confianza: number
  }
  
  // Metadata
  createdAt: Date
  updatedAt: Date
  rowNumber?: number
  sheetTab?: 'Admin' | 'Enviados' | 'Confirmado'
  
  // Historial de cambios
  history?: Array<{
    timestamp: Date
    action: string
    oldValue?: any
    newValue?: any
    user?: string
  }>
}

export interface QuoteStats {
  totalPendientes: number
  totalEnviados: number
  totalConfirmados: number
  totalGeneral: number
  porOrigen: {
    WA: number
    LO: number
    EM: number
    CL: number
  }
  porEstado: {
    Pendiente: number
    Adjunto: number
    Listo: number
    Enviado: number
    Asignado: number
    Confirmado: number
  }
  ultimaActualizacion: Date
}
