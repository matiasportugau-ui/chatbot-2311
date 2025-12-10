import React from 'react'
import { ChatInterfaceEvolved } from '@/components/chat/chat-interface-evolved'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Building2, MessageSquare, Sparkles, Zap, ShieldCheck } from 'lucide-react'

export default function ChatPage() {
  return (
    <main className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto space-y-8">
          <div className="space-y-3">
            <div className="flex flex-wrap items-center gap-3">
              <Badge variant="outline" className="flex items-center gap-1">
                <Sparkles className="h-3 w-3" />
                Interfaz unificada
              </Badge>
              <Badge variant="secondary" className="flex items-center gap-1">
                <Zap className="h-3 w-3" />
                Streaming en vivo
              </Badge>
              <Badge variant="outline" className="flex items-center gap-1">
                <ShieldCheck className="h-3 w-3" />
                Gestión de contexto
              </Badge>
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                Chat Inteligente de Cotizaciones
              </h1>
              <p className="text-gray-600 dark:text-gray-400 max-w-3xl">
                Esta pantalla combina lo mejor de todas las versiones previas: streaming en tiempo real,
                manejo automático de sesiones, compresión de contexto y el enfoque de productos de BMC
                Construcciones en un solo front.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
            <div className="lg:col-span-2">
              <ChatInterfaceEvolved userPhone="+59891234567" className="h-full" />
            </div>

            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <MessageSquare className="h-5 w-5" />
                    Qué unificamos
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3 text-sm text-muted-foreground">
                  <p>
                    Flujo de conversación con streaming, compresión automática y creación de nuevas
                    sesiones cuando se alcanza el límite.
                  </p>
                  <Separator />
                  <ul className="list-disc pl-5 space-y-1">
                    <li>Gestión de contexto y compresión inteligente al 80%.</li>
                    <li>Persistencia y recuperación automática de la sesión.</li>
                    <li>Indicadores de confianza para respuestas de cotización.</li>
                    <li>Botones rápidos para reiniciar chat o comprimir contexto.</li>
                  </ul>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Building2 className="h-5 w-5" />
                    Enfoque BMC
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 text-sm text-muted-foreground">
                  <p>
                    Pensado para el motor de cotización de BMC Construcciones: conserva el detalle de
                    productos, integra cálculos y mantiene el hilo de WhatsApp.
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {['Isodec', 'Isoroof', 'Isopanel', 'Isowall', 'Chapas', 'Calamería'].map((producto) => (
                      <Badge key={producto} variant="outline">{producto}</Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Sparkles className="h-5 w-5" />
                    Atajos sugeridos
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3 text-sm text-muted-foreground">
                  <div className="p-3 rounded-lg bg-blue-50 dark:bg-blue-900/20">
                    &quot;Necesito cotizar Isodec 100mm para un galpón de 50m2 en Montevideo&quot;
                  </div>
                  <div className="p-3 rounded-lg bg-green-50 dark:bg-green-900/20">
                    &quot;¿Qué panel recomiendas para cámara frigorífica de 40m2?&quot;
                  </div>
                  <div className="p-3 rounded-lg bg-purple-50 dark:bg-purple-900/20">
                    &quot;Calcula tiempos de entrega y costos de envío para Isoroof 80mm&quot;
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
