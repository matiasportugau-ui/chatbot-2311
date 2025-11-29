'use client'

import React, { useEffect, useMemo, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { RefreshCw, Pause, Play, ExternalLink, Store } from 'lucide-react'

interface MercadoLibreListing {
  id: string
  title: string
  price: number
  currency_id: string
  available_quantity: number
  sold_quantity?: number
  status: string
  permalink: string
  date_created?: string
  last_updated?: string
}

const statusColors: Record<string, string> = {
  active: 'bg-emerald-100 text-emerald-800',
  paused: 'bg-yellow-100 text-yellow-800',
  closed: 'bg-rose-100 text-rose-800'
}

function formatCurrency(value: number, currency: string) {
  try {
    return new Intl.NumberFormat('es-UY', {
      style: 'currency',
      currency: currency || 'USD',
      maximumFractionDigits: 2
    }).format(value)
  } catch {
    return `${value.toFixed(2)} ${currency || ''}`
  }
}

export function MercadoLibreListings() {
  const [listings, setListings] = useState<MercadoLibreListing[]>([])
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'paused' | 'closed'>('all')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const filteredListings = useMemo(() => {
    if (statusFilter === 'all') return listings
    return listings.filter((listing) => listing.status === statusFilter)
  }, [listings, statusFilter])

  const loadListings = async () => {
    setLoading(true)
    setError(null)
    try {
      const params = new URLSearchParams({ limit: '30' })
      if (statusFilter !== 'all') params.append('status', statusFilter)

      const response = await fetch(`/api/mercado-libre/listings/list?${params.toString()}`)
      if (!response.ok) {
        throw new Error('No se pudieron obtener las publicaciones')
      }
      const data = await response.json()
      setListings(data.listings || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadListings()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statusFilter])

  const handleStatusChange = async (id: string, status: 'active' | 'paused' | 'closed') => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch('/api/mercado-libre/listings/status', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, status })
      })
      if (!response.ok) {
        const payload = await response.json().catch(() => ({}))
        throw new Error(payload?.error || 'No se pudo actualizar la publicación')
      }
      await loadListings()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
      setLoading(false)
    }
  }

  const summary = useMemo(() => {
    return listings.reduce(
      (acc, listing) => {
        acc.total += 1
        acc.byStatus[listing.status] = (acc.byStatus[listing.status] || 0) + 1
        acc.inventory += listing.available_quantity
        return acc
      },
      {
        total: 0,
        inventory: 0,
        byStatus: {} as Record<string, number>
      }
    )
  }, [listings])

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <div>
            <CardTitle className="text-xl font-semibold flex items-center gap-2">
              <Store className="h-5 w-5" />
              Publicaciones Mercado Libre
            </CardTitle>
            <p className="text-sm text-muted-foreground">
              Gestión centralizada de publicaciones activas, pausadas y cerradas.
            </p>
          </div>
          <div className="flex gap-2">
            <select
              value={statusFilter}
              onChange={(event) => setStatusFilter(event.target.value as any)}
              className="px-3 py-2 border rounded-md text-sm"
            >
              <option value="all">Todos los estados</option>
              <option value="active">Activos</option>
              <option value="paused">Pausados</option>
              <option value="closed">Cerrados</option>
            </select>
            <Button onClick={loadListings} disabled={loading} variant="outline">
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Actualizar
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className="p-4 border rounded-lg">
              <p className="text-sm text-muted-foreground">Publicaciones totales</p>
              <p className="text-2xl font-semibold">{summary.total}</p>
            </div>
            <div className="p-4 border rounded-lg">
              <p className="text-sm text-muted-foreground">Inventario disponible</p>
              <p className="text-2xl font-semibold">{summary.inventory}</p>
            </div>
            <div className="p-4 border rounded-lg">
              <p className="text-sm text-muted-foreground">Activas</p>
              <p className="text-2xl font-semibold">{summary.byStatus['active'] || 0}</p>
            </div>
          </div>

          {error && (
            <div className="mb-4 rounded bg-red-50 text-red-700 px-4 py-2 text-sm">{error}</div>
          )}

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left border-b">
                  <th className="py-2 pr-4">Título</th>
                  <th className="py-2 pr-4">Precio</th>
                  <th className="py-2 pr-4">Stock</th>
                  <th className="py-2 pr-4">Estado</th>
                  <th className="py-2 pr-4">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {filteredListings.map((listing) => (
                  <tr key={listing.id} className="border-b last:border-0">
                    <td className="py-3 pr-4">
                      <div className="flex flex-col">
                        <span className="font-medium">{listing.title}</span>
                        <a
                          href={listing.permalink}
                          target="_blank"
                          rel="noreferrer"
                          className="text-indigo-600 text-xs flex items-center gap-1"
                        >
                          Ver publicación
                          <ExternalLink className="h-3 w-3" />
                        </a>
                      </div>
                    </td>
                    <td className="py-3 pr-4">{formatCurrency(listing.price, listing.currency_id)}</td>
                    <td className="py-3 pr-4">
                      {listing.available_quantity}{' '}
                      <span className="text-muted-foreground text-xs">
                        {listing.sold_quantity
                          ? `(${listing.sold_quantity} vendidos)`
                          : 'sin ventas registradas'}
                      </span>
                    </td>
                    <td className="py-3 pr-4">
                      <Badge className={statusColors[listing.status] || 'bg-gray-100 text-gray-700'}>
                        {listing.status}
                      </Badge>
                    </td>
                    <td className="py-3 pr-4">
                      <div className="flex gap-2">
                        {listing.status !== 'paused' && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleStatusChange(listing.id, 'paused')}
                          >
                            <Pause className="h-4 w-4 mr-1" /> Pausar
                          </Button>
                        )}
                        {listing.status === 'paused' && (
                          <Button
                            size="sm"
                            onClick={() => handleStatusChange(listing.id, 'active')}
                          >
                            <Play className="h-4 w-4 mr-1" /> Reanudar
                          </Button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
                {filteredListings.length === 0 && (
                  <tr>
                    <td colSpan={5} className="py-6 text-center text-muted-foreground">
                      {loading ? 'Sincronizando publicaciones...' : 'No hay publicaciones para mostrar.'}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

