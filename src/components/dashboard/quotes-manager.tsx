'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { 
  Search, 
  RefreshCw, 
  Filter, 
  Download,
  Eye,
  CheckCircle,
  Clock,
  AlertCircle,
  MessageSquare,
  Phone,
  MapPin,
  Calendar
} from 'lucide-react'

interface Quote {
  _id?: string
  arg: string
  estado: string
  fecha: string
  cliente: string
  origen: string
  telefono: string
  direccion: string
  consulta: string
  parsed?: any
  createdAt: string
  updatedAt: string
  rowNumber?: number
}

interface QuoteStats {
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
  ultimaActualizacion: string
}

export function QuotesManager({ className }: { className?: string }) {
  const [quotes, setQuotes] = useState<Quote[]>([])
  const [stats, setStats] = useState<QuoteStats | null>(null)
  const [loading, setLoading] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [filterEstado, setFilterEstado] = useState('all')
  const [filterOrigen, setFilterOrigen] = useState('all')

  const loadQuotes = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/sheets/sync')
      const data = await response.json()
      
      if (data.success) {
        // Combinar todas las cotizaciones
        const allQuotes = [
          ...data.data.pendientes.map((q: any) => ({ ...q, sheetTab: 'Admin' })),
          ...data.data.enviados.map((q: any) => ({ ...q, sheetTab: 'Enviados' })),
          ...data.data.confirmados.map((q: any) => ({ ...q, sheetTab: 'Confirmado' }))
        ]
        setQuotes(allQuotes)
        setStats(data.data.stats)
      }
    } catch (error) {
      console.error('Error loading quotes:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadQuotes()
    
    // Auto-refresh cada 30 segundos
    const interval = setInterval(loadQuotes, 30000)
    return () => clearInterval(interval)
  }, [])

  const getEstadoColor = (estado: string) => {
    switch (estado) {
      case 'Pendiente': return 'bg-yellow-100 text-yellow-800'
      case 'Adjunto': return 'bg-blue-100 text-blue-800'
      case 'Listo': return 'bg-green-100 text-green-800'
      case 'Enviado': return 'bg-purple-100 text-purple-800'
      case 'Asignado': return 'bg-orange-100 text-orange-800'
      case 'Confirmado': return 'bg-emerald-100 text-emerald-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getOrigenColor = (origen: string) => {
    switch (origen) {
      case 'WA': return 'bg-green-100 text-green-800'
      case 'LO': return 'bg-blue-100 text-blue-800'
      case 'EM': return 'bg-purple-100 text-purple-800'
      case 'CL': return 'bg-orange-100 text-orange-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getEstadoIcon = (estado: string) => {
    switch (estado) {
      case 'Pendiente': return <Clock className="w-4 h-4" />
      case 'Adjunto': return <AlertCircle className="w-4 h-4" />
      case 'Listo': return <CheckCircle className="w-4 h-4" />
      case 'Enviado': return <MessageSquare className="w-4 h-4" />
      case 'Asignado': return <CheckCircle className="w-4 h-4" />
      case 'Confirmado': return <CheckCircle className="w-4 h-4" />
      default: return <Clock className="w-4 h-4" />
    }
  }

  const filteredQuotes = quotes.filter(quote => {
    const matchesSearch = searchQuery === '' || 
      quote.cliente.toLowerCase().includes(searchQuery.toLowerCase()) ||
      quote.consulta.toLowerCase().includes(searchQuery.toLowerCase()) ||
      quote.arg.toLowerCase().includes(searchQuery.toLowerCase()) ||
      quote.telefono.includes(searchQuery)
    
    const matchesEstado = filterEstado === 'all' || quote.estado === filterEstado
    const matchesOrigen = filterOrigen === 'all' || quote.origen === filterOrigen
    
    return matchesSearch && matchesEstado && matchesOrigen
  })

  const updateQuoteStatus = async (arg: string, newStatus: string) => {
    try {
      const response = await fetch('/api/sheets/sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'update_status',
          data: {
            sheetName: 'Admin',
            row: quotes.find(q => q.arg === arg)?.rowNumber,
            column: 'B',
            status: newStatus
          }
        })
      })
      
      if (response.ok) {
        await loadQuotes() // Recargar datos
      }
    } catch (error) {
      console.error('Error updating quote status:', error)
    }
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Administrador de Cotizaciones
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Gestión en tiempo real de cotizaciones desde Google Sheets
          </p>
        </div>
        <Button 
          onClick={loadQuotes} 
          disabled={loading}
          className="flex items-center gap-2"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Actualizar
        </Button>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Pendientes</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-600">{stats.totalPendientes}</div>
              <p className="text-xs text-muted-foreground">
                Requieren atención
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Enviados</CardTitle>
              <MessageSquare className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-purple-600">{stats.totalEnviados}</div>
              <p className="text-xs text-muted-foreground">
                Presupuestos entregados
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Confirmados</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{stats.totalConfirmados}</div>
              <p className="text-xs text-muted-foreground">
                Clientes confirmados
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total</CardTitle>
              <AlertCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalGeneral}</div>
              <p className="text-xs text-muted-foreground">
                Cotizaciones totales
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input
                  placeholder="Buscar por cliente, consulta, código o teléfono..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <div className="flex gap-2">
              <select
                value={filterEstado}
                onChange={(e) => setFilterEstado(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm"
              >
                <option value="all">Todos los estados</option>
                <option value="Pendiente">Pendiente</option>
                <option value="Adjunto">Adjunto</option>
                <option value="Listo">Listo</option>
                <option value="Enviado">Enviado</option>
                <option value="Asignado">Asignado</option>
                <option value="Confirmado">Confirmado</option>
              </select>
              
              <select
                value={filterOrigen}
                onChange={(e) => setFilterOrigen(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm"
              >
                <option value="all">Todos los orígenes</option>
                <option value="WA">WhatsApp</option>
                <option value="LO">Local</option>
                <option value="EM">Email</option>
                <option value="CL">Cliente directo</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Quotes List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="w-5 h-5" />
            Cotizaciones ({filteredQuotes.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {filteredQuotes.map((quote) => (
              <div
                key={quote.arg}
                className="p-4 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <Badge className={getEstadoColor(quote.estado)}>
                        {getEstadoIcon(quote.estado)}
                        <span className="ml-1">{quote.estado}</span>
                      </Badge>
                      <Badge className={getOrigenColor(quote.origen)}>
                        {quote.origen}
                      </Badge>
                      <span className="text-sm font-mono text-gray-500">
                        {quote.arg}
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <h3 className="font-semibold text-lg">{quote.cliente}</h3>
                        <div className="flex items-center gap-2 text-sm text-gray-600 mt-1">
                          <Phone className="w-4 h-4" />
                          {quote.telefono}
                        </div>
                        <div className="flex items-center gap-2 text-sm text-gray-600 mt-1">
                          <MapPin className="w-4 h-4" />
                          {quote.direccion}
                        </div>
                        <div className="flex items-center gap-2 text-sm text-gray-600 mt-1">
                          <Calendar className="w-4 h-4" />
                          {quote.fecha}
                        </div>
                      </div>
                      
                      <div>
                        <p className="text-sm text-gray-700 line-clamp-3">
                          {quote.consulta}
                        </p>
                        
                        {quote.parsed && (
                          <div className="mt-2 text-xs text-gray-500">
                            <span className="font-medium">Producto:</span> {quote.parsed.producto?.tipo}
                            {quote.parsed.producto?.grosor && ` (${quote.parsed.producto.grosor})`}
                            {quote.parsed.dimensiones?.area_m2 && ` - ${quote.parsed.dimensiones.area_m2} m²`}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex gap-2 ml-4">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        // Implementar vista detallada
                        console.log('View details for:', quote.arg)
                      }}
                    >
                      <Eye className="w-4 h-4" />
                    </Button>
                    
                    {quote.estado === 'Pendiente' && (
                      <Button
                        size="sm"
                        onClick={() => updateQuoteStatus(quote.arg, 'Asignado')}
                      >
                        Asignar
                      </Button>
                    )}
                    
                    {quote.estado === 'Asignado' && (
                      <Button
                        size="sm"
                        onClick={() => updateQuoteStatus(quote.arg, 'Enviado')}
                      >
                        Marcar Enviado
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            ))}
            
            {filteredQuotes.length === 0 && !loading && (
              <div className="text-center py-8 text-gray-500">
                No se encontraron cotizaciones con los filtros aplicados
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
