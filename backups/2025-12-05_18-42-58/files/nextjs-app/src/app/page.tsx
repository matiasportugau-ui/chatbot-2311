'use client'

import { ChatInterfaceEvolved } from '@/components/chat/chat-interface-evolved'

export default function Home() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black p-4">
      <main className="flex min-h-screen w-full max-w-6xl flex-col py-8 px-4">
        <div className="mb-4 text-center">
          <h1 className="text-3xl font-bold text-black dark:text-zinc-50 mb-2">
            BMC Chatbot - Sistema de Cotizaciones
          </h1>
          <p className="text-lg text-zinc-600 dark:text-zinc-400">
            Asistente inteligente para cotizaciones de construcción
          </p>
        </div>
        <div className="flex-1">
          <ChatInterfaceEvolved 
            userPhone="+59891234567"
            className="h-full"
          />
        </div>
      </main>
    </div>
  );
}
