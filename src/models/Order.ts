export interface MercadoLibreOrderRecord {
  _id?: string
  orderId: number
  status: string
  dateCreated: string
  lastUpdated: string
  totalAmount: number
  currencyId: string
  buyer: {
    id?: number
    nickname?: string
    full_name?: string
    email?: string
    phone?: string
  }
  payments: Array<{
    id: number
    status: string
    transaction_amount: number
    method?: string
  }>
  shipping: {
    status?: string
    tracking_number?: string
    mode?: string
  }
  acknowledged: boolean
  readyToShip: boolean
  tags: string[]
  lastSync: Date
  createdAt: Date
  updatedAt: Date
}


