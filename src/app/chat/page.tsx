import React from 'react'
import { ChatInterface } from '@/components/chat/chat-interface'

export default function ChatPage() {
  return (
    <main className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              Sistema de Chat con Gestión de Contexto
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Prueba el sistema de gestión de contexto en tiempo real
            </p>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Chat Interface */}
            <div className="lg:col-span-2">
              <ChatInterface userPhone="+59891234567" />
            </div>
            
            {/* Info Panel */}
            <div className="space-y-6">
              <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow">
                <h3 className="text-lg font-semibold mb-4">Características del Sistema</h3>
                <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                  <li>✅ Gestión automática de contexto</li>
                  <li>✅ Compresión inteligente de conversaciones</li>
                  <li>✅ Creación automática de nuevos chats</li>
                  <li>✅ Monitoreo de uso de tokens</li>
                  <li>✅ Persistencia de sesiones</li>
                  <li>✅ Integración con OpenAI</li>
                </ul>
              </div>
              
              <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow">
                <h3 className="text-lg font-semibold mb-4">Cómo Funciona</h3>
                <div className="space-y-3 text-sm text-gray-600 dark:text-gray-400">
                  <div>
                    <strong>1. Inicio:</strong> Se crea una nueva sesión automáticamente
                  </div>
                  <div>
                    <strong>2. Conversación:</strong> Los mensajes se almacenan con contexto
                  </div>
                  <div>
                    <strong>3. Compresión:</strong> Cuando se alcanza el 80% del límite
                  </div>
                  <div>
                    <strong>4. Nuevo Chat:</strong> Se crea automáticamente si es necesario
                  </div>
                </div>
              </div>
              
              <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow">
                <h3 className="text-lg font-semibold mb-4">Límites del Sistema</h3>
                <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                  <div>📊 Máximo: 8,000 tokens por sesión</div>
                  <div>💬 Máximo: 20 mensajes por sesión</div>
                  <div>⏰ Timeout: 30 minutos de inactividad</div>
                  <div>🔄 Compresión: Automática al 80%</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
