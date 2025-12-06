import React from 'react'
import Link from 'next/link'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { MessageSquare, Bot, Zap, Building2, ArrowRight } from 'lucide-react'

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
            BMC Chatbot System
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            Sistema inteligente de cotizaciones con múltiples interfaces de chat
          </p>
        </div>

        {/* Chat Interfaces Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Chat Interface - Basic */}
          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
                  <MessageSquare className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                </div>
                <CardTitle className="text-xl">Chat Básico</CardTitle>
              </div>
              <CardDescription>
                Interfaz estándar con gestión de contexto y compresión automática
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400 mb-6">
                <li className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  Gestión automática de contexto
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  Compresión inteligente
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  Monitoreo de tokens
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  Persistencia de sesiones
                </li>
              </ul>
              <Link href="/chat">
                <Button className="w-full" variant="default">
                  Abrir Chat Básico
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* Chat Interface - Evolved */}
          <Card className="hover:shadow-lg transition-shadow border-2 border-green-200 dark:border-green-800">
            <CardHeader>
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
                  <Zap className="w-6 h-6 text-green-600 dark:text-green-400" />
                </div>
                <CardTitle className="text-xl">Chat Evolucionado</CardTitle>
              </div>
              <CardDescription>
                Interfaz avanzada con streaming en tiempo real y AI SDK
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400 mb-6">
                <li className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  Streaming de respuestas
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  AI SDK integrado
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  Manejo optimizado de errores
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  Mejor rendimiento
                </li>
              </ul>
              <Link href="/chat-evolved">
                <Button className="w-full" variant="default">
                  Abrir Chat Evolucionado
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* BMC Chat Interface */}
          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
                  <Building2 className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                </div>
                <CardTitle className="text-xl">Chat BMC</CardTitle>
              </div>
              <CardDescription>
                Motor de cotización integrado con base de conocimiento BMC
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400 mb-6">
                <li className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  Cotizaciones automáticas
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  Motor de IA especializado
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  Productos y precios
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-green-500">✓</span>
                  Base de conocimiento BMC
                </li>
              </ul>
              <Link href="/bmc-chat">
                <Button className="w-full" variant="default">
                  Abrir Chat BMC
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>

        {/* Quick Access Section */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bot className="w-5 h-5" />
              Acceso Rápido
            </CardTitle>
            <CardDescription>
              Navega rápidamente entre las diferentes interfaces
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Link href="/chat">
                <Button variant="outline" className="w-full justify-start">
                  <MessageSquare className="w-4 h-4 mr-2" />
                  Chat Básico
                </Button>
              </Link>
              <Link href="/chat-evolved">
                <Button variant="outline" className="w-full justify-start">
                  <Zap className="w-4 h-4 mr-2" />
                  Chat Evolucionado
                </Button>
              </Link>
              <Link href="/bmc-chat">
                <Button variant="outline" className="w-full justify-start">
                  <Building2 className="w-4 h-4 mr-2" />
                  Chat BMC
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Info Footer */}
        <div className="mt-8 text-center text-sm text-gray-600 dark:text-gray-400">
          <p>Selecciona una interfaz de chat para comenzar a interactuar con el sistema</p>
        </div>
      </div>
    </main>
  )
}
