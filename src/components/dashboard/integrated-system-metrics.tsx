'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  Brain, 
  TrendingUp, 
  Users, 
  MessageSquare, 
  Target,
  RefreshCw,
  BarChart3,
  Lightbulb,
  Database,
  Zap
} from 'lucide-react'

interface SystemMetrics {
  total_interacciones: number
  cotizaciones_generadas: number
  conversiones: number
  tasa_conversion: number
  patrones_identificados: number
  productos_conocidos: number
  confianza_promedio: number
}

interface PatternAnalysis {
  patrones_identificados: number
  productos_mas_consultados: string
  zonas_mas_activas: string
  horarios_pico: string
}

export function IntegratedSystemMetrics() {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null)
  const [patterns, setPatterns] = useState<PatternAnalysis | null>(null)
  const [loading, setLoading] = useState(true)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)

  const fetchMetrics = async () => {
    try {
      setLoading(true)
      
      // Obtener métricas del sistema
      const metricsResponse = await fetch('/api/integrated-quote', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'metrics' })
      })
      
      if (metricsResponse.ok) {
        const metricsData = await metricsResponse.json()
        setMetrics(metricsData.data.metricas)
      }

      // Obtener análisis de patrones
      const patternsResponse = await fetch('/api/integrated-quote', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'analyze_patterns' })
      })
      
      if (patternsResponse.ok) {
        const patternsData = await patternsResponse.json()
        setPatterns(patternsData.data)
      }

      setLastUpdate(new Date())
    } catch (error) {
      console.error('Error fetching metrics:', error)
    } finally {
      setLoading(false)
    }
  }

  const updateKnowledgeBase = async () => {
    try {
      setLoading(true)
      
      const response = await fetch('/api/integrated-quote', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'update_knowledge' })
      })
      
      if (response.ok) {
        // Refrescar métricas después de actualizar
        await fetchMetrics()
      }
    } catch (error) {
      console.error('Error updating knowledge base:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchMetrics()
    
    // Actualizar métricas cada 30 segundos
    const interval = setInterval(fetchMetrics, 30000)
    return () => clearInterval(interval)
  }, [])

  const getConversionColor = (rate: number) => {
    if (rate >= 0.3) return 'text-green-600'
    if (rate >= 0.2) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600'
    if (confidence >= 0.6) return 'text-yellow-600'
    return 'text-red-600'
  }

  if (loading && !metrics) {
    return (
      <Card className="h-[calc(100vh-120px)] flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4" />
          <p>Cargando métricas del sistema...</p>
        </div>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header con botones de acción */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold flex items-center">
            <Brain className="w-6 h-6 mr-2" />
            Sistema Integrado BMC
          </h2>
          <p className="text-muted-foreground">
            Métricas del motor de cotización con base de conocimiento evolutiva
          </p>
        </div>
        <div className="flex space-x-2">
          <Button 
            onClick={fetchMetrics} 
            disabled={loading}
            variant="outline"
            size="sm"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Actualizar
          </Button>
          <Button 
            onClick={updateKnowledgeBase} 
            disabled={loading}
            size="sm"
          >
            <Zap className="w-4 h-4 mr-2" />
            Actualizar Conocimiento
          </Button>
        </div>
      </div>

      {/* Métricas principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Interacciones Totales</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics?.total_interacciones || 0}</div>
            <p className="text-xs text-muted-foreground">
              Conversaciones procesadas
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Cotizaciones Generadas</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics?.cotizaciones_generadas || 0}</div>
            <p className="text-xs text-muted-foreground">
              Presupuestos creados
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tasa de Conversión</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${getConversionColor(metrics?.tasa_conversion || 0)}`}>
              {((metrics?.tasa_conversion || 0) * 100).toFixed(1)}%
            </div>
            <p className="text-xs text-muted-foreground">
              Cotizaciones → Ventas
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Confianza Promedio</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${getConfidenceColor(metrics?.confianza_promedio || 0)}`}>
              {((metrics?.confianza_promedio || 0) * 100).toFixed(1)}%
            </div>
            <p className="text-xs text-muted-foreground">
              Precisión del sistema
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Análisis de patrones */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Lightbulb className="w-5 h-5 mr-2" />
              Patrones de Venta Identificados
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">Patrones Activos</span>
                <Badge variant="secondary">{metrics?.patrones_identificados || 0}</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">Productos Conocidos</span>
                <Badge variant="secondary">{metrics?.productos_conocidos || 0}</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">Conversiones</span>
                <Badge variant="secondary">{metrics?.conversiones || 0}</Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Database className="w-5 h-5 mr-2" />
              Base de Conocimiento
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">Estado</span>
                <Badge variant="default">Activa</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">Aprendizaje</span>
                <Badge variant="default">Automático</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">Última Actualización</span>
                <span className="text-xs text-muted-foreground">
                  {lastUpdate ? lastUpdate.toLocaleTimeString() : 'N/A'}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Análisis detallado */}
      {patterns && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <BarChart3 className="w-5 h-5 mr-2" />
              Análisis de Patrones
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 border rounded-lg">
                <Users className="w-8 h-8 mx-auto mb-2 text-blue-600" />
                <h3 className="font-semibold">Productos Más Consultados</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  {patterns.productos_mas_consultados || 'Análisis en desarrollo'}
                </p>
              </div>
              <div className="text-center p-4 border rounded-lg">
                <MapPin className="w-8 h-8 mx-auto mb-2 text-green-600" />
                <h3 className="font-semibold">Zonas Más Activas</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  {patterns.zonas_mas_activas || 'Análisis en desarrollo'}
                </p>
              </div>
              <div className="text-center p-4 border rounded-lg">
                <Clock className="w-8 h-8 mx-auto mb-2 text-purple-600" />
                <h3 className="font-semibold">Horarios Pico</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  {patterns.horarios_pico || 'Análisis en desarrollo'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Estado del sistema */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Zap className="w-5 h-5 mr-2" />
            Estado del Sistema
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm font-medium">Sistema Activo</span>
            </div>
            <div className="text-sm text-muted-foreground">
              Base de conocimiento evolutiva funcionando
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
