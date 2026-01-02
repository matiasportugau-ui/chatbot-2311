import React from 'react';
import { BMCChatInterface } from '@/components/chat/bmc-chat-interface';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { Building2, MessageSquare, Calculator, Info, CheckCircle } from 'lucide-react';

export default function BMCChatPage() {
  return (
    <div className="container mx-auto p-4 grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-40px)]">
      <div className="lg:col-span-2">
        <BMCChatInterface userPhone="+59891234567" />
      </div>
      
      <Card className="lg:col-span-1 flex flex-col">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building2 className="w-5 h-5" />
            Chat BMC - Motor de Cotización
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-grow overflow-auto text-sm text-muted-foreground">
          <p className="mb-4">
            Este es el chat inteligente de BMC Construcciones con motor de cotización integrado.
            Puedes hacer consultas sobre productos, solicitar cotizaciones y obtener información detallada.
          </p>
          
          <Separator className="my-4" />
          
          <h3 className="font-semibold mb-2 flex items-center gap-2">
            <MessageSquare className="w-4 h-4" />
            Funcionalidades del Chat
          </h3>
          <ul className="list-disc pl-5 space-y-1 mb-4">
            <li><strong>Cotizaciones Automáticas:</strong> Genera presupuestos en tiempo real</li>
            <li><strong>Información de Productos:</strong> Detalles técnicos y especificaciones</li>
            <li><strong>Preguntas Frecuentes:</strong> Respuestas a consultas comunes</li>
            <li><strong>Gestión de Contexto:</strong> Mantiene el hilo de la conversación</li>
            <li><strong>Integración WhatsApp:</strong> Conecta con el sistema de mensajería</li>
          </ul>
          
          <Separator className="my-4" />
          
          <h3 className="font-semibold mb-2 flex items-center gap-2">
            <Calculator className="w-4 h-4" />
            Productos Disponibles
          </h3>
          <div className="space-y-2 mb-4">
            <Badge variant="outline" className="mr-1 mb-1">Isodec EPS</Badge>
            <Badge variant="outline" className="mr-1 mb-1">Isoroof</Badge>
            <Badge variant="outline" className="mr-1 mb-1">Isopanel</Badge>
            <Badge variant="outline" className="mr-1 mb-1">Isowall</Badge>
            <Badge variant="outline" className="mr-1 mb-1">Chapas</Badge>
            <Badge variant="outline" className="mr-1 mb-1">Calamería</Badge>
          </div>
          
          <Separator className="my-4" />
          
          <h3 className="font-semibold mb-2 flex items-center gap-2">
            <Info className="w-4 h-4" />
            Ejemplos de Consultas
          </h3>
          <div className="space-y-2 text-xs">
            <div className="p-2 bg-blue-50 dark:bg-blue-900/20 rounded">
              <strong>Cotización:</strong> &quot;Necesito cotizar Isodec 100mm para galpón de 50m2&quot;
            </div>
            <div className="p-2 bg-green-50 dark:bg-green-900/20 rounded">
              <strong>Información:</strong> &quot;¿Qué es Isoroof y para qué se usa?&quot;
            </div>
            <div className="p-2 bg-purple-50 dark:bg-purple-900/20 rounded">
              <strong>Pregunta:</strong> &quot;¿Cuánto tiempo tarda la entrega?&quot;
            </div>
          </div>
          
          <Separator className="my-4" />
          
          <h3 className="font-semibold mb-2 flex items-center gap-2">
            <CheckCircle className="w-4 h-4" />
            Características Técnicas
          </h3>
          <ul className="list-disc pl-5 space-y-1 text-xs">
            <li>Motor de IA con base de conocimiento BMC</li>
            <li>Parsing inteligente de consultas</li>
            <li>Cálculo automático de precios</li>
            <li>Integración con Google Sheets</li>
            <li>Gestión de contexto optimizada</li>
            <li>Respuestas en tiempo real</li>
          </ul>
          
          <Separator className="my-4" />
          
          <p className="italic text-xs">
            💡 <strong>Tip:</strong> Sé específico en tus consultas para obtener cotizaciones más precisas. 
            Incluye dimensiones, tipo de producto y servicios necesarios.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
