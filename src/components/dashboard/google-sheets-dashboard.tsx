'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from '@/components/ui/table'
import { 
  RefreshCw, 
  Search, 
  FileText, 
  Send, 
  CheckCircle, 
  Clock,
  TrendingUp,
  Users,
  Phone,
  MapPin,
  Calendar,
  Filter,
  Download,
  Upload
} from 'lucide-react'

interface AdminRow {
  rowNumber: number
  arg: string
  estado: string
  fecha: string
  cliente: string
  origen: string
  telefono: string
  direccion: string
  consulta: string
}

interface EnviadosRow {
  rowNumber: number
  arg: string
  estado: string
  fecha: string
  cliente: string
  origen: string
  telefono: string
  direccion: string
  consulta: string
  precio?: string
  fechaEnvio?: string
}

interface Statistics {
  totalPendientes: number
  totalEnviados: number
  totalConfirmados: number
  totalCotizaciones: number
  cotizacionesPorOrigen: Record<string, number>
  cotizacionesPorEstado: Record<string, number>
}

export function GoogleSheetsDashboard() {
  const [adminData, setAdminData] = useState<AdminRow[]>([])
  const [enviadosData, setEnviadosData] = useState<EnviadosRow[]>([])
  const [confirmadosData, setConfirmadosData] = useState<EnviadosRow[]>([])
  const [statistics, setStatistics] = useState<Statistics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [activeTab, setActiveTab] = useState<'admin' | 'enviados' | 'confirmados' | 'statistics'>('admin')

  const fetchData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await fetch('/api/sheets/enhanced-sync?action=all')
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      
      if (data.success) {
        setAdminData(data.data.admin)
        setEnviadosData(data.data.enviados)
        setConfirmadosData(data.data.confirmados)
        setStatistics(data.data.statistics)
      } else {
        throw new Error('Error fetching data')
      }
    } catch (e: any) {
      setError(e.message)
      console.error('Error fetching data:', e)
    } finally {
      setLoading(false)
    }
  }

  const searchByPhone = async (phone: string) => {
    if (!phone.trim()) return
    
    try {
      setLoading(true)
      const response = await fetch(`/api/sheets/enhanced-sync?action=search&phone=${encodeURIComponent(phone)}`)
      
      if (response.ok) {
        const data = await response.json()
        if (data.success) {
          setAdminData(data.data.results.pendientes)
          setEnviadosData(data.data.results.enviados)
          setConfirmadosData(data.data.results.confirmados)
        }
      }
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const moveToEnviados = async (rowNumber: number, arg: string) => {
    try {
      const response = await fetch('/api/sheets/enhanced-sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'move_to_enviados',
          data: { 
            rowNumber,
            additionalData: {
              precio: 'A cotizar',
              fechaEnvio: new Date().toLocaleDateString('es-UY')
            }
          }
        })
      })
      
      if (response.ok) {
        await fetchData() // Refrescar datos
      }
    } catch (e: any) {
      setError(e.message)
    }
  }

  const moveToConfirmado = async (rowNumber: number, arg: string) => {
    try {
      const response = await fetch('/api/sheets/enhanced-sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'move_to_confirmado',
          data: { 
            rowNumber,
            additionalData: {
              fechaConfirmacion: new Date().toLocaleDateString('es-UY')
            }
          }
        })
      })
      
      if (response.ok) {
        await fetchData() // Refrescar datos
      }
    } catch (e: any) {
      setError(e.message)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const getEstadoColor = (estado: string) => {
    switch (estado.toLowerCase()) {
      case 'pendiente':
        return 'bg-yellow-100 text-yellow-800'
      case 'enviado':
        return 'bg-blue-100 text-blue-800'
      case 'confirmado':
        return 'bg-green-100 text-green-800'
      case 'adjunto':
        return 'bg-purple-100 text-purple-800'
      case 'listo':
        return 'bg-orange-100 text-orange-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getOrigenIcon = (origen: string) => {
    switch (origen) {
      case 'WA':
        return '📱'
      case 'LO':
        return '🏢'
      case 'EM':
        return '📧'
      case 'CL':
        return '📞'
      default:
        return '❓'
    }
  }

  const filteredAdminData = adminData.filter(row => 
    searchTerm === '' || 
    row.cliente.toLowerCase().includes(searchTerm.toLowerCase()) ||
    row.telefono.includes(searchTerm) ||
    row.arg.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const filteredEnviadosData = enviadosData.filter(row => 
    searchTerm === '' || 
    row.cliente.toLowerCase().includes(searchTerm.toLowerCase()) ||
    row.telefono.includes(searchTerm) ||
    row.arg.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const filteredConfirmadosData = confirmadosData.filter(row => 
    searchTerm === '' || 
    row.cliente.toLowerCase().includes(searchTerm.toLowerCase()) ||
    row.telefono.includes(searchTerm) ||
    row.arg.toLowerCase().includes(searchTerm.toLowerCase())
  )

  if (loading && !statistics) {
    return (
      <Card className="h-[calc(100vh-120px)] flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4" />
          <p>Cargando datos de Google Sheets...</p>
        </div>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header con estadísticas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pendientes</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{statistics?.totalPendientes || 0}</div>
            <p className="text-xs text-muted-foreground">
              Cotizaciones en proceso
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Enviados</CardTitle>
            <Send className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{statistics?.totalEnviados || 0}</div>
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
            <div className="text-2xl font-bold">{statistics?.totalConfirmados || 0}</div>
            <p className="text-xs text-muted-foreground">
              Ventas concretadas
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{statistics?.totalCotizaciones || 0}</div>
            <p className="text-xs text-muted-foreground">
              Cotizaciones totales
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Controles */}
      <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="relative">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Buscar por cliente, teléfono o código..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-8 w-64"
            />
          </div>
          <Button 
            onClick={() => searchByPhone(searchTerm)}
            disabled={loading}
            size="sm"
          >
            <Search className="w-4 h-4 mr-2" />
            Buscar
          </Button>
        </div>

        <div className="flex items-center space-x-2">
          <Button 
            onClick={fetchData} 
            disabled={loading}
            variant="outline"
            size="sm"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Actualizar
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex space-x-1 bg-muted p-1 rounded-lg">
        <Button
          variant={activeTab === 'admin' ? 'default' : 'ghost'}
          size="sm"
          onClick={() => setActiveTab('admin')}
        >
          <Clock className="w-4 h-4 mr-2" />
          Pendientes ({filteredAdminData.length})
        </Button>
        <Button
          variant={activeTab === 'enviados' ? 'default' : 'ghost'}
          size="sm"
          onClick={() => setActiveTab('enviados')}
        >
          <Send className="w-4 h-4 mr-2" />
          Enviados ({filteredEnviadosData.length})
        </Button>
        <Button
          variant={activeTab === 'confirmados' ? 'default' : 'ghost'}
          size="sm"
          onClick={() => setActiveTab('confirmados')}
        >
          <CheckCircle className="w-4 h-4 mr-2" />
          Confirmados ({filteredConfirmadosData.length})
        </Button>
        <Button
          variant={activeTab === 'statistics' ? 'default' : 'ghost'}
          size="sm"
          onClick={() => setActiveTab('statistics')}
        >
          <TrendingUp className="w-4 h-4 mr-2" />
          Estadísticas
        </Button>
      </div>

      {/* Contenido de tabs */}
      <Card>
        <CardContent className="p-0">
          {activeTab === 'admin' && (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Código</TableHead>
                    <TableHead>Estado</TableHead>
                    <TableHead>Fecha</TableHead>
                    <TableHead>Cliente</TableHead>
                    <TableHead>Origen</TableHead>
                    <TableHead>Teléfono</TableHead>
                    <TableHead>Dirección</TableHead>
                    <TableHead>Consulta</TableHead>
                    <TableHead>Acciones</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredAdminData.map((row) => (
                    <TableRow key={row.rowNumber}>
                      <TableCell className="font-medium">{row.arg}</TableCell>
                      <TableCell>
                        <Badge className={getEstadoColor(row.estado)}>
                          {row.estado}
                        </Badge>
                      </TableCell>
                      <TableCell>{row.fecha}</TableCell>
                      <TableCell>{row.cliente}</TableCell>
                      <TableCell>
                        <span className="flex items-center">
                          {getOrigenIcon(row.origen)} {row.origen}
                        </span>
                      </TableCell>
                      <TableCell>{row.telefono}</TableCell>
                      <TableCell className="max-w-[150px] truncate">{row.direccion}</TableCell>
                      <TableCell className="max-w-[200px] truncate">{row.consulta}</TableCell>
                      <TableCell>
                        <Button
                          size="sm"
                          onClick={() => moveToEnviados(row.rowNumber, row.arg)}
                          className="mr-2"
                        >
                          <Send className="w-4 h-4 mr-1" />
                          Enviar
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}

          {activeTab === 'enviados' && (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Código</TableHead>
                    <TableHead>Estado</TableHead>
                    <TableHead>Fecha</TableHead>
                    <TableHead>Cliente</TableHead>
                    <TableHead>Origen</TableHead>
                    <TableHead>Teléfono</TableHead>
                    <TableHead>Precio</TableHead>
                    <TableHead>Fecha Envío</TableHead>
                    <TableHead>Acciones</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredEnviadosData.map((row) => (
                    <TableRow key={row.rowNumber}>
                      <TableCell className="font-medium">{row.arg}</TableCell>
                      <TableCell>
                        <Badge className={getEstadoColor(row.estado)}>
                          {row.estado}
                        </Badge>
                      </TableCell>
                      <TableCell>{row.fecha}</TableCell>
                      <TableCell>{row.cliente}</TableCell>
                      <TableCell>
                        <span className="flex items-center">
                          {getOrigenIcon(row.origen)} {row.origen}
                        </span>
                      </TableCell>
                      <TableCell>{row.telefono}</TableCell>
                      <TableCell>{row.precio || 'N/A'}</TableCell>
                      <TableCell>{row.fechaEnvio || 'N/A'}</TableCell>
                      <TableCell>
                        <Button
                          size="sm"
                          onClick={() => moveToConfirmado(row.rowNumber, row.arg)}
                          className="mr-2"
                        >
                          <CheckCircle className="w-4 h-4 mr-1" />
                          Confirmar
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}

          {activeTab === 'confirmados' && (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Código</TableHead>
                    <TableHead>Estado</TableHead>
                    <TableHead>Fecha</TableHead>
                    <TableHead>Cliente</TableHead>
                    <TableHead>Origen</TableHead>
                    <TableHead>Teléfono</TableHead>
                    <TableHead>Precio</TableHead>
                    <TableHead>Fecha Envío</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredConfirmadosData.map((row) => (
                    <TableRow key={row.rowNumber}>
                      <TableCell className="font-medium">{row.arg}</TableCell>
                      <TableCell>
                        <Badge className={getEstadoColor(row.estado)}>
                          {row.estado}
                        </Badge>
                      </TableCell>
                      <TableCell>{row.fecha}</TableCell>
                      <TableCell>{row.cliente}</TableCell>
                      <TableCell>
                        <span className="flex items-center">
                          {getOrigenIcon(row.origen)} {row.origen}
                        </span>
                      </TableCell>
                      <TableCell>{row.telefono}</TableCell>
                      <TableCell>{row.precio || 'N/A'}</TableCell>
                      <TableCell>{row.fechaEnvio || 'N/A'}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}

          {activeTab === 'statistics' && statistics && (
            <div className="p-6 space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Por Origen</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {Object.entries(statistics.cotizacionesPorOrigen).map(([origen, count]) => (
                        <div key={origen} className="flex justify-between items-center">
                          <span className="flex items-center">
                            {getOrigenIcon(origen)} {origen}
                          </span>
                          <Badge variant="secondary">{count}</Badge>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Por Estado</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {Object.entries(statistics.cotizacionesPorEstado).map(([estado, count]) => (
                        <div key={estado} className="flex justify-between items-center">
                          <span>{estado}</span>
                          <Badge className={getEstadoColor(estado)}>{count}</Badge>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="p-4">
            <p className="text-red-600">Error: {error}</p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
