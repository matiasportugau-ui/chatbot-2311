'use client';

import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  type?: string;
  confidence?: number;
}

interface Conversation {
  sessionId: string;
  phone: string;
  messages: Message[];
  createdAt: string;
}

export default function SimulatorPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [phone, setPhone] = useState('+59891234567');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<string | null>(null);
  const [modelParams, setModelParams] = useState({
    temperature: 0.7,
    model: 'gpt-4o-mini'
  });

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || process.env.PY_CHAT_SERVICE_URL || 'http://localhost:8000';

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    // For now, conversations are stored in MongoDB
    // This would require a new endpoint to fetch from MongoDB
    // For simulation, we'll use local state
    try {
      // Try to fetch from MongoDB if endpoint exists
      const response = await fetch(`${apiUrl}/conversations`);
      if (response.ok) {
        const data = await response.json();
        setConversations(data);
      }
    } catch (error) {
      // If endpoint doesn't exist, that's ok for simulation mode
      console.log('Conversations endpoint not available, using local state');
    }
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch(`${apiUrl}/chat/process`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          mensaje: userMessage.content,
          telefono: phone,
          sesionId: sessionId
        }),
      });

      if (!response.ok) {
        throw new Error('Error processing message');
      }

      const data = await response.json();
      
      if (data.sesion_id && !sessionId) {
        setSessionId(data.sesion_id);
      }

      const assistantMessage: Message = {
        role: 'assistant',
        content: data.mensaje || data.message || 'No response',
        timestamp: data.timestamp || new Date().toISOString(),
        type: data.tipo || data.type,
        confidence: data.confianza || data.confidence
      };

      setMessages(prev => [...prev, assistantMessage]);
      await loadConversations();
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Error al procesar el mensaje. Por favor intenta de nuevo.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const startNewConversation = () => {
    setMessages([]);
    setSessionId(null);
    setSelectedConversation(null);
  };

  const loadConversation = async (sessionId: string) => {
    try {
      const response = await fetch(`${apiUrl}/conversations/${sessionId}`);
      if (response.ok) {
        const data = await response.json();
        setMessages(data.messages || []);
        setSessionId(sessionId);
        setSelectedConversation(sessionId);
      }
    } catch (error) {
      console.error('Error loading conversation:', error);
    }
  };

  const updateModelParams = async () => {
    try {
      const response = await fetch(`${apiUrl}/config`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(modelParams),
      });
      if (response.ok) {
        alert('Parámetros del modelo actualizados');
      }
    } catch (error) {
      console.error('Error updating model params:', error);
    }
  };

  return (
    <div className="container mx-auto p-6 max-w-7xl">
      <h1 className="text-3xl font-bold mb-6">Simulador de Chatbot BMC</h1>

      <Tabs defaultValue="chat" className="space-y-4">
        <TabsList>
          <TabsTrigger value="chat">Chat</TabsTrigger>
          <TabsTrigger value="conversations">Conversaciones</TabsTrigger>
          <TabsTrigger value="settings">Configuración</TabsTrigger>
        </TabsList>

        <TabsContent value="chat" className="space-y-4">
          <Card className="p-4">
            <div className="flex gap-4 mb-4">
              <div className="flex-1">
                <label className="block text-sm font-medium mb-1">Teléfono</label>
                <Input
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="+59891234567"
                />
              </div>
              <div className="flex items-end">
                <Button onClick={startNewConversation} variant="outline">
                  Nueva Conversación
                </Button>
              </div>
            </div>

            <div className="border rounded-lg p-4 h-96 overflow-y-auto mb-4 bg-gray-50">
              {messages.length === 0 ? (
                <div className="text-center text-gray-500 mt-20">
                  Inicia una conversación enviando un mensaje
                </div>
              ) : (
                messages.map((msg, idx) => (
                  <div
                    key={idx}
                    className={`mb-4 flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                        msg.role === 'user'
                          ? 'bg-blue-500 text-white'
                          : 'bg-white border border-gray-200'
                      }`}
                    >
                      <p className="text-sm">{msg.content}</p>
                      {msg.type && (
                        <div className="mt-2 flex gap-2">
                          <Badge variant="outline">{msg.type}</Badge>
                          {msg.confidence && (
                            <Badge variant="outline">
                              Confianza: {(msg.confidence * 100).toFixed(0)}%
                            </Badge>
                          )}
                        </div>
                      )}
                      <p className="text-xs mt-1 opacity-70">
                        {new Date(msg.timestamp).toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                ))
              )}
            </div>

            <div className="flex gap-2">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && !loading && sendMessage()}
                placeholder="Escribe tu mensaje..."
                disabled={loading}
              />
              <Button onClick={sendMessage} disabled={loading || !input.trim()}>
                {loading ? 'Enviando...' : 'Enviar'}
              </Button>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="conversations" className="space-y-4">
          <Card className="p-4">
            <h2 className="text-xl font-semibold mb-4">Conversaciones Recientes</h2>
            {conversations.length === 0 ? (
              <p className="text-gray-500">No hay conversaciones guardadas</p>
            ) : (
              <div className="space-y-2">
                {conversations.map((conv) => (
                  <div
                    key={conv.sessionId}
                    className={`p-3 border rounded-lg cursor-pointer hover:bg-gray-50 ${
                      selectedConversation === conv.sessionId ? 'bg-blue-50 border-blue-300' : ''
                    }`}
                    onClick={() => loadConversation(conv.sessionId)}
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-medium">{conv.phone}</p>
                        <p className="text-sm text-gray-500">
                          {conv.messages.length} mensajes
                        </p>
                      </div>
                      <p className="text-xs text-gray-400">
                        {new Date(conv.createdAt).toLocaleString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </TabsContent>

        <TabsContent value="settings" className="space-y-4">
          <Card className="p-4">
            <h2 className="text-xl font-semibold mb-4">Parámetros del Modelo</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Temperature</label>
                <Input
                  type="number"
                  min="0"
                  max="2"
                  step="0.1"
                  value={modelParams.temperature}
                  onChange={(e) =>
                    setModelParams({
                      ...modelParams,
                      temperature: parseFloat(e.target.value)
                    })
                  }
                />
                <p className="text-xs text-gray-500 mt-1">
                  Controla la creatividad (0.0 = determinista, 2.0 = muy creativo)
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Modelo</label>
                <select
                  className="w-full p-2 border rounded"
                  value={modelParams.model}
                  onChange={(e) =>
                    setModelParams({ ...modelParams, model: e.target.value })
                  }
                >
                  <option value="gpt-4o-mini">GPT-4o Mini</option>
                  <option value="gpt-4o">GPT-4o</option>
                  <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                </select>
              </div>
              <Button onClick={updateModelParams}>Guardar Parámetros</Button>
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

