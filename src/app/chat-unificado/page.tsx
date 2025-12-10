import React from 'react'
import { ChatInterfaceUnified } from '@/components/chat/unified-chat-interface'

export default function UnifiedChatPage() {
    return (
        <main className="min-h-screen bg-gray-50 dark:bg-gray-900">
            <div className="container mx-auto px-4 py-8">
                <div className="max-w-6xl mx-auto space-y-6">
                    <div className="flex flex-col gap-2">
                        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                            Chat Unificado
                        </h1>
                        <p className="text-gray-600 dark:text-gray-400 max-w-3xl">
                            Versión consolidada que mezcla el streaming y control de contexto del chat evolucionado, la
                            presentación amigable del chat original y los badges de cotización del flujo BMC.
                        </p>
                    </div>

                    <ChatInterfaceUnified />
                </div>
            </div>
        </main>
    )
}
