import { getDatabase } from './mongodb'
import { Quote, QuoteStats } from '@/models/Quote'

export class QuoteService {
  private collectionName = 'quotes'
  
  async createQuote(quoteData: Omit<Quote, '_id' | 'createdAt' | 'updatedAt'>): Promise<Quote> {
    const db = await getDatabase()
    const collection = db.collection(this.collectionName)
    
    const quote: Quote = {
      ...quoteData,
      createdAt: new Date(),
      updatedAt: new Date(),
      history: [{
        timestamp: new Date(),
        action: 'created',
        newValue: quoteData
      }]
    }
    
    const result = await collection.insertOne(quote)
    return { ...quote, _id: result.insertedId.toString() }
  }
  
  async getQuoteById(id: string): Promise<Quote | null> {
    const db = await getDatabase()
    const collection = db.collection(this.collectionName)
    
    const quote = await collection.findOne({ _id: id })
    return quote as Quote | null
  }
  
  async getQuoteByArg(arg: string): Promise<Quote | null> {
    const db = await getDatabase()
    const collection = db.collection(this.collectionName)
    
    const quote = await collection.findOne({ arg })
    return quote as Quote | null
  }
  
  async getQuotesByPhone(phone: string): Promise<Quote[]> {
    const db = await getDatabase()
    const collection = db.collection(this.collectionName)
    
    const quotes = await collection.find({ telefono: { $regex: phone, $options: 'i' } })
      .sort({ createdAt: -1 })
      .toArray()
    
    return quotes as Quote[]
  }
  
  async updateQuoteStatus(arg: string, newStatus: Quote['estado'], user?: string): Promise<boolean> {
    const db = await getDatabase()
    const collection = db.collection(this.collectionName)
    
    const quote = await this.getQuoteByArg(arg)
    if (!quote) return false
    
    const oldStatus = quote.estado
    
    const result = await collection.updateOne(
      { arg },
      {
        $set: {
          estado: newStatus,
          updatedAt: new Date()
        },
        $push: {
          history: {
            timestamp: new Date(),
            action: 'status_update',
            oldValue: oldStatus,
            newValue: newStatus,
            user
          }
        }
      }
    )
    
    return result.modifiedCount > 0
  }
  
  async updateQuoteParsedData(arg: string, parsedData: Quote['parsed']): Promise<boolean> {
    const db = await getDatabase()
    const collection = db.collection(this.collectionName)
    
    const result = await collection.updateOne(
      { arg },
      {
        $set: {
          parsed: parsedData,
          updatedAt: new Date()
        },
        $push: {
          history: {
            timestamp: new Date(),
            action: 'parsed_data_update',
            newValue: parsedData
          }
        }
      }
    )
    
    return result.modifiedCount > 0
  }
  
  async getQuotesByEstado(estado: Quote['estado']): Promise<Quote[]> {
    const db = await getDatabase()
    const collection = db.collection(this.collectionName)
    
    const quotes = await collection.find({ estado })
      .sort({ createdAt: -1 })
      .toArray()
    
    return quotes as Quote[]
  }
  
  async getAllQuotes(limit: number = 100, skip: number = 0): Promise<Quote[]> {
    const db = await getDatabase()
    const collection = db.collection(this.collectionName)
    
    const quotes = await collection.find({})
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(limit)
      .toArray()
    
    return quotes as Quote[]
  }
  
  async getStats(): Promise<QuoteStats> {
    const db = await getDatabase()
    const collection = db.collection(this.collectionName)
    
    const [totalPendientes, totalEnviados, totalConfirmados, totalGeneral] = await Promise.all([
      collection.countDocuments({ estado: 'Pendiente' }),
      collection.countDocuments({ estado: 'Enviado' }),
      collection.countDocuments({ estado: 'Confirmado' }),
      collection.countDocuments({})
    ])
    
    // Estadísticas por origen
    const porOrigen = await collection.aggregate([
      { $group: { _id: '$origen', count: { $sum: 1 } } }
    ]).toArray()
    
    const porOrigenMap = {
      WA: 0,
      LO: 0,
      EM: 0,
      CL: 0
    }
    
    porOrigen.forEach((item: any) => {
      if (item._id in porOrigenMap) {
        porOrigenMap[item._id as keyof typeof porOrigenMap] = item.count
      }
    })
    
    // Estadísticas por estado
    const porEstado = await collection.aggregate([
      { $group: { _id: '$estado', count: { $sum: 1 } } }
    ]).toArray()
    
    const porEstadoMap = {
      Pendiente: 0,
      Adjunto: 0,
      Listo: 0,
      Enviado: 0,
      Asignado: 0,
      Confirmado: 0
    }
    
    porEstado.forEach((item: any) => {
      if (item._id in porEstadoMap) {
        porEstadoMap[item._id as keyof typeof porEstadoMap] = item.count
      }
    })
    
    return {
      totalPendientes,
      totalEnviados,
      totalConfirmados,
      totalGeneral,
      porOrigen: porOrigenMap,
      porEstado: porEstadoMap,
      ultimaActualizacion: new Date()
    }
  }
  
  async searchQuotes(query: string): Promise<Quote[]> {
    const db = await getDatabase()
    const collection = db.collection(this.collectionName)
    
    const quotes = await collection.find({
      $or: [
        { cliente: { $regex: query, $options: 'i' } },
        { consulta: { $regex: query, $options: 'i' } },
        { arg: { $regex: query, $options: 'i' } },
        { telefono: { $regex: query, $options: 'i' } }
      ]
    })
      .sort({ createdAt: -1 })
      .limit(50)
      .toArray()
    
    return quotes as Quote[]
  }
  
  async deleteQuote(arg: string): Promise<boolean> {
    const db = await getDatabase()
    const collection = db.collection(this.collectionName)
    
    const result = await collection.deleteOne({ arg })
    return result.deletedCount > 0
  }
}
