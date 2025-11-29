'use client'

import React, { useEffect, useMemo, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { RefreshCw, CheckCircle, PackageCheck } from 'lucide-react'

interface StoredOrder {
  _id?: string
  orderId: number
  status: string
  totalAmount: number
  currencyId: string
  buyer: {
    full_name?: string
    nickname?: string
    email?: string
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
  }
  acknowledged: boolean
  readyToShip: boolean
  dateCreated: string
}

interface OrdersSummary {
  total: number
  pending: number
  paid: number
  delivered: number
  canceled: number
  totalRevenue: number
  currency: string
}

const statusVariant: Record<string, string> = {
  paid: 'bg-emerald-100 text-emerald-800',
  pending: 'bg-yellow-100 text-yellow-800',
  canceled: 'bg-rose-100 text-rose-800',
  delivered: 'bg-blue-100 text-blue-800',
  ready_to_ship: 'bg-indigo-100 text-indigo-800'
}

function formatCurrency(value: number, currency: string) {
  try {
    return new Intl.NumberFormat('es-UY', {
      style: 'currency',
      currency: currency || 'USD'
    }).format(value)
  } catch {
    return `${value.toFixed(2)} ${currency}`
  }
}

export function MercadoLibreOrders() {
  const [orders, setOrders] = useState<StoredOrder[]>([])
  const [summary, setSummary] = useState<OrdersSummary | null>(null)
  const [loading, setLoading] = useState(false)
  const [syncing, setSyncing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadOrders = async () => {
    setLoading(true)
    setError(null)
    try {
      const [ordersRes, summaryRes] = await Promise.all([
        fetch('/api/mercado-libre/orders/list'),
        fetch('/api/mercado-libre/orders/summary')
      ])

      if (!ordersRes.ok) throw new Error('No se pudieron obtener las órdenes')
      if (!summaryRes.ok) throw new Error('No se pudo obtener el resumen de órdenes')

      const ordersData = await ordersRes.json()
      const summaryData = await summaryRes.json()

      setOrders(ordersData.orders || [])
      setSummary(summaryData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadOrders()
  }, [])

  const syncOrders = async () => {
    setSyncing(true)
    setError(null)
    try {
      const response = await fetch('/api/mercado-libre/orders/sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ limit: 30 })
      })

      if (!response.ok) {
        const payload = await response.json().catch(() => ({}))
        throw new Error(payload?.error || 'Error sincronizando órdenes')
      }

      await loadOrders()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    } finally {
      setSyncing(false)
    }
  }

  const action = async (url: string, body: any) => {
    setError(null)
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })
    if (!response.ok) {
      const payload = await response.json().catch(() => ({}))
      throw new Error(payload?.error || 'Error actualizando la orden')
    }
    await loadOrders()
  }

  const handleAcknowledge = async (orderId: number) => {
    try {
      await action('/api/mercado-libre/orders/acknowledge', { orderId })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    }
  }

  const handleReadyToShip = async (orderId: number) => {
    try {
      await action('/api/mercado-libre/orders/ship', { orderId })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    }
  }

  const revenuePerOrder = useMemo(() => {
    if (!summary || summary.total === 0) return '—'
    return formatCurrency(summary.totalRevenue / summary.total, summary.currency)
  }, [summary])

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <div>
          <CardTitle className="text-xl font-semibold">Órdenes y Pagos</CardTitle>
          <p className="text-sm text-muted-foreground">
            Seguimiento de órdenes, pagos y estado logístico.
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={loadOrders} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Actualizar
          </Button>
          <Button onClick={syncOrders} disabled={syncing}>
            {syncing ? 'Sincronizando...' : 'Sincronizar con MELI'}
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {error && (
          <div className="mb-4 rounded bg-red-50 text-red-700 px-4 py-2 text-sm">{error}</div>
        )}

        {summary && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="p-4 border rounded-lg">
              <p className="text-sm text-muted-foreground">Órdenes totales</p>
              <p className="text-2xl font-semibold">{summary.total}</p>
            </div>
            <div className="p-4 border rounded-lg">
              <p className="text-sm text-muted-foreground">Ingresos</p>
              <p className="text-2xl font-semibold">
                {formatCurrency(summary.totalRevenue, summary.currency)}
              </p>
            </div>
            <div className="p-4 border rounded-lg">
              <p className="text-sm text-muted-foreground">Ticket promedio</p>
              <p className="text-2xl font-semibold">{revenuePerOrder}</p>
            </div>
            <div className="p-4 border rounded-lg">
              <p className="text-sm text-muted-foreground">Pagadas</p>
              <p className="text-2xl font-semibold">{summary.paid}</p>
            </div>
          </div>
        )}

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left border-b">
                <th className="py-2 pr-4">Orden</th>
                <th className="py-2 pr-4">Cliente</th>
                <th className="py-2 pr-4">Total</th>
                <th className="py-2 pr-4">Estado</th>
                <th className="py-2 pr-4">Pago</th>
                <th className="py-2 pr-4">Envío</th>
                <th className="py-2 pr-4">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {orders.map((order) => (
                <tr key={order.orderId} className="border-b last:border-0">
                  <td className="py-3 pr-4 font-mono text-xs">#{order.orderId}</td>
                  <td className="py-3 pr-4">
                    <div className="flex flex-col">
                      <span className="font-medium">{order.buyer?.full_name || order.buyer?.nickname}</span>
                      <span className="text-xs text-muted-foreground">{order.buyer?.email}</span>
                    </div>
                  </td>
                  <td className="py-3 pr-4 font-semibold">
                    {formatCurrency(order.totalAmount, order.currencyId)}
                  </td>
                  <td className="py-3 pr-4">
                    <Badge className={statusVariant[order.status] || 'bg-gray-100 text-gray-700'}>
                      {order.status}
                    </Badge>
                  </td>
                  <td className="py-3 pr-4">
                    {order.payments.length > 0 ? (
                      <div className="flex flex-col">
                        <span>{order.payments[0].status}</span>
                        <span className="text-xs text-muted-foreground">
                          {order.payments[0].method}
                        </span>
                      </div>
                    ) : (
                      <span className="text-muted-foreground">Sin datos</span>
                    )}
                  </td>
                  <td className="py-3 pr-4">
                    <div className="flex flex-col text-xs">
                      <span>{order.shipping?.status || '—'}</span>
                      {order.shipping?.tracking_number && (
                        <span className="text-muted-foreground">{order.shipping.tracking_number}</span>
                      )}
                    </div>
                  </td>
                  <td className="py-3 pr-4">
                    <div className="flex gap-2">
                      {!order.acknowledged && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleAcknowledge(order.orderId)}
                        >
                          <CheckCircle className="h-4 w-4 mr-1" />
                          Confirmar pago
                        </Button>
                      )}
                      {!order.readyToShip && (
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleReadyToShip(order.orderId)}
                        >
                          <PackageCheck className="h-4 w-4 mr-1" />
                          Listo para envío
                        </Button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
              {orders.length === 0 && (
                <tr>
                  <td colSpan={7} className="py-6 text-center text-muted-foreground">
                    {loading ? 'Cargando órdenes...' : 'No hay órdenes sincronizadas todavía.'}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  )
}

