// ============================================================================
// BMC MongoDB Playground - Sistema de Cotizaciones BMC Uruguay
// ============================================================================
// Este Playground está completamente alineado con el proyecto chatbot-2311
// Generado basándose en la estructura real del workspace
//
// NOTA IMPORTANTE SOBRE PRODUCTOS:
// BMC vende más de 400 productos. Los seeds de este Playground incluyen
// solo ejemplos de algunos productos comunes (Isodec, Isoroof, Isopanel,
// Poliestireno, Chapas, Calamería) para demostración.
// La estructura de datos es genérica y funciona para cualquier producto.
// ============================================================================

// ============================================================================
// 1. SELECCIÓN DE BASE DE DATOS
// ============================================================================
// Base de datos real del proyecto según env.example y mongodb_service.py
use('bmc_chat');

// ============================================================================
// 2. SEEDS AUTOMÁTICOS POR COLECCIÓN
// ============================================================================
// Nota: Los seeds son idempotentes - se pueden ejecutar múltiples veces
// sin crear duplicados si se verifica existencia antes de insertar

// ----------------------------------------------------------------------------
// 2.1. SEED: conversations (Conversaciones del chat)
// ----------------------------------------------------------------------------
// Estructura basada en api_server.py líneas 639-652
const conversationsSeed = [
  {
    session_id: "session_001_20250101",
    phone: "099123456",
    message: "Hola, necesito cotizar Isodec para un proyecto",
    response: "¡Hola! Te ayudo con la cotización de Isodec. ¿Podrías indicarme las dimensiones?",
    response_type: "question",
    confidence: 0.85,
    intent: "cotizacion",
    entities: {
      producto: "isodec",
      tipo_consulta: "cotizacion"
    },
    timestamp: new Date("2025-01-15T10:30:00Z"),
    source: "api"
  },
  {
    session_id: "session_002_20250101",
    phone: "098765432",
    message: "¿Cuál es el precio del poliestireno por metro cuadrado?",
    response: "El precio del poliestireno expandido varía según el espesor. ¿Qué espesor necesitas?",
    response_type: "question",
    confidence: 0.92,
    intent: "informacion_precio",
    entities: {
      producto: "poliestireno",
      tipo_consulta: "precio"
    },
    timestamp: new Date("2025-01-15T11:15:00Z"),
    source: "api"
  },
  {
    session_id: "session_003_20250101",
    phone: "097654321",
    message: "Necesito cotizar Isoroof para un techo",
    response: "Perfecto, Isoroof es ideal para techos. ¿Podrías indicarme las dimensiones y el espesor necesario?",
    response_type: "question",
    confidence: 0.88,
    intent: "cotizacion",
    entities: {
      producto: "isoroof",
      tipo_consulta: "cotizacion"
    },
    timestamp: new Date("2025-01-15T14:20:00Z"),
    source: "api"
  },
  {
    session_id: "session_004_20250101",
    phone: "096543210",
    message: "¿Tienen chapas galvanizadas?",
    response: "Sí, tenemos chapas galvanizadas disponibles. ¿Qué espesor y dimensiones necesitas?",
    response_type: "question",
    confidence: 0.90,
    intent: "informacion",
    entities: {
      producto: "chapa_galvanizada",
      tipo_consulta: "informacion"
    },
    timestamp: new Date("2025-01-15T15:00:00Z"),
    source: "api"
  },
  {
    session_id: "session_005_20250101",
    phone: "095432109",
    message: "Necesito Isopanel para paredes",
    response: "Isopanel es perfecto para paredes. ¿Qué espesor y dimensiones necesitas para tu proyecto?",
    response_type: "question",
    confidence: 0.87,
    intent: "cotizacion",
    entities: {
      producto: "isopanel",
      tipo_consulta: "cotizacion"
    },
    timestamp: new Date("2025-01-15T16:30:00Z"),
    source: "api"
  }
];

// Insertar conversations (verificar duplicados por session_id + timestamp)
conversationsSeed.forEach(conv => {
  const exists = db.conversations.findOne({
    session_id: conv.session_id,
    timestamp: conv.timestamp
  });
  if (!exists) {
    db.conversations.insertOne(conv);
  }
});

print("✅ Seeds de conversations insertados");

// ----------------------------------------------------------------------------
// 2.2. SEED: quotes (Cotizaciones)
// ----------------------------------------------------------------------------
// Estructura basada en src/models/Quote.ts y sistema_cotizaciones.py
const quotesSeed = [
  {
    arg: "COT-20250115103000",
    estado: "Pendiente",
    fecha: "2025-01-15",
    cliente: "Gabriel",
    origen: "WA",
    telefono: "099123456",
    direccion: "Cancha de Punta del Este",
    consulta: "Necesito Isodec 100mm, 10m x 5m, color blanco",
    parsed: {
      producto: {
        tipo: "isodec",
        grosor: "100mm",
        color: "Blanco",
        cantidad: 50,
        unidad: "m²"
      },
      dimensiones: {
        largo: 10,
        ancho: 5,
        area_m2: 50
      },
      servicios: {
        flete: true,
        instalacion: false,
        accesorios: true
      },
      estado_info: "completo",
      confianza: 0.85
    },
    createdAt: new Date("2025-01-15T10:30:00Z"),
    updatedAt: new Date("2025-01-15T10:30:00Z"),
    rowNumber: 1,
    sheetTab: "Admin",
    history: [
      {
        timestamp: new Date("2025-01-15T10:30:00Z"),
        action: "created",
        newValue: "Pendiente",
        user: "system"
      }
    ]
  },
  {
    arg: "COT-20250115111500",
    estado: "Enviado",
    fecha: "2025-01-15",
    cliente: "María",
    origen: "LO",
    telefono: "098765432",
    direccion: "Montevideo Centro",
    consulta: "Cotización poliestireno 75mm, 8m x 4m",
    parsed: {
      producto: {
        tipo: "poliestireno",
        grosor: "75mm",
        color: "Blanco",
        cantidad: 32,
        unidad: "m²"
      },
      dimensiones: {
        largo: 8,
        ancho: 4,
        area_m2: 32
      },
      servicios: {
        flete: false,
        instalacion: false,
        accesorios: false
      },
      estado_info: "completo",
      confianza: 0.92
    },
    createdAt: new Date("2025-01-15T11:15:00Z"),
    updatedAt: new Date("2025-01-15T12:00:00Z"),
    rowNumber: 2,
    sheetTab: "Enviados",
    history: [
      {
        timestamp: new Date("2025-01-15T11:15:00Z"),
        action: "created",
        newValue: "Pendiente",
        user: "system"
      },
      {
        timestamp: new Date("2025-01-15T12:00:00Z"),
        action: "status_changed",
        oldValue: "Pendiente",
        newValue: "Enviado",
        user: "MA"
      }
    ]
  },
  {
    arg: "COT-20250115142000",
    estado: "Confirmado",
    fecha: "2025-01-15",
    cliente: "Carlos",
    origen: "EM",
    telefono: "097654321",
    direccion: "Canelones",
    consulta: "Isoroof 50mm para techo, 5m x 5m",
    parsed: {
      producto: {
        tipo: "isoroof",
        grosor: "50mm",
        color: "Blanco",
        cantidad: 25,
        unidad: "m²"
      },
      dimensiones: {
        largo: 5,
        ancho: 5,
        area_m2: 25
      },
      servicios: {
        flete: true,
        instalacion: true,
        accesorios: false
      },
      estado_info: "completo",
      confianza: 0.88
    },
    createdAt: new Date("2025-01-15T14:20:00Z"),
    updatedAt: new Date("2025-01-15T16:30:00Z"),
    rowNumber: 3,
    sheetTab: "Confirmado",
    history: [
      {
        timestamp: new Date("2025-01-15T14:20:00Z"),
        action: "created",
        newValue: "Pendiente",
        user: "system"
      },
      {
        timestamp: new Date("2025-01-15T15:00:00Z"),
        action: "status_changed",
        oldValue: "Pendiente",
        newValue: "Listo",
        user: "MA"
      },
      {
        timestamp: new Date("2025-01-15T16:30:00Z"),
        action: "status_changed",
        oldValue: "Listo",
        newValue: "Confirmado",
        user: "cliente"
      }
    ]
  },
  {
    arg: "COT-20250115150000",
    estado: "Listo",
    fecha: "2025-01-15",
    cliente: "Ana",
    origen: "LO",
    telefono: "096543210",
    direccion: "Montevideo",
    consulta: "Cotización chapas galvanizadas 0.40mm, 20m x 3m",
    parsed: {
      producto: {
        tipo: "chapa_galvanizada",
        grosor: "0.40mm",
        color: "Galvanizado",
        cantidad: 60,
        unidad: "m²"
      },
      dimensiones: {
        largo: 20,
        ancho: 3,
        area_m2: 60
      },
      servicios: {
        flete: true,
        instalacion: false,
        accesorios: true
      },
      estado_info: "completo",
      confianza: 0.92
    },
    createdAt: new Date("2025-01-15T15:00:00Z"),
    updatedAt: new Date("2025-01-15T15:30:00Z"),
    rowNumber: 4,
    sheetTab: "Admin",
    history: [
      {
        timestamp: new Date("2025-01-15T15:00:00Z"),
        action: "created",
        newValue: "Pendiente",
        user: "system"
      },
      {
        timestamp: new Date("2025-01-15T15:30:00Z"),
        action: "status_changed",
        oldValue: "Pendiente",
        newValue: "Listo",
        user: "MA"
      }
    ]
  },
  {
    arg: "COT-20250115163000",
    estado: "Pendiente",
    fecha: "2025-01-15",
    cliente: "Roberto",
    origen: "WA",
    telefono: "095432109",
    direccion: "Maldonado",
    consulta: "Isopanel 100mm para paredes, 6m x 3m",
    parsed: {
      producto: {
        tipo: "isopanel",
        grosor: "100mm",
        color: "Blanco",
        cantidad: 18,
        unidad: "m²"
      },
      dimensiones: {
        largo: 6,
        ancho: 3,
        area_m2: 18
      },
      servicios: {
        flete: true,
        instalacion: false,
        accesorios: false
      },
      estado_info: "completo",
      confianza: 0.85
    },
    createdAt: new Date("2025-01-15T16:30:00Z"),
    updatedAt: new Date("2025-01-15T16:30:00Z"),
    rowNumber: 5,
    sheetTab: "Admin",
    history: [
      {
        timestamp: new Date("2025-01-15T16:30:00Z"),
        action: "created",
        newValue: "Pendiente",
        user: "system"
      }
    ]
  }
];

// Insertar quotes (verificar duplicados por arg)
quotesSeed.forEach(quote => {
  const exists = db.quotes.findOne({ arg: quote.arg });
  if (!exists) {
    db.quotes.insertOne(quote);
  }
});

print("✅ Seeds de quotes insertados");

// ----------------------------------------------------------------------------
// 2.3. SEED: orders (Órdenes de MercadoLibre)
// ----------------------------------------------------------------------------
// Estructura basada en src/models/Order.ts
const ordersSeed = [
  {
    orderId: 1234567890,
    status: "paid",
    dateCreated: "2025-01-10T08:00:00Z",
    lastUpdated: "2025-01-10T10:30:00Z",
    totalAmount: 15000.00,
    currencyId: "UYU",
    buyer: {
      id: 987654321,
      nickname: "COMPRADOR_URUGUAY",
      full_name: "Juan Pérez",
      email: "juan.perez@example.com",
      phone: "099111222"
    },
    payments: [
      {
        id: 111222333,
        status: "approved",
        transaction_amount: 15000.00,
        method: "credit_card"
      }
    ],
    shipping: {
      status: "ready_to_ship",
      tracking_number: "UR123456789",
      mode: "me2"
    },
    acknowledged: true,
    readyToShip: true,
    tags: ["urgent", "priority"],
    lastSync: new Date("2025-01-10T10:30:00Z"),
    createdAt: new Date("2025-01-10T08:00:00Z"),
    updatedAt: new Date("2025-01-10T10:30:00Z")
  },
  {
    orderId: 1234567891,
    status: "confirmed",
    dateCreated: "2025-01-12T14:20:00Z",
    lastUpdated: "2025-01-12T15:00:00Z",
    totalAmount: 8500.00,
    currencyId: "UYU",
    buyer: {
      id: 987654322,
      nickname: "CLIENTE_MONTEVIDEO",
      full_name: "Ana García",
      email: "ana.garcia@example.com",
      phone: "098333444"
    },
    payments: [
      {
        id: 111222334,
        status: "approved",
        transaction_amount: 8500.00,
        method: "bank_transfer"
      }
    ],
    shipping: {
      status: "pending",
      mode: "me2"
    },
    acknowledged: false,
    readyToShip: false,
    tags: ["normal"],
    lastSync: new Date("2025-01-12T15:00:00Z"),
    createdAt: new Date("2025-01-12T14:20:00Z"),
    updatedAt: new Date("2025-01-12T15:00:00Z")
  }
];

// Insertar orders (verificar duplicados por orderId)
ordersSeed.forEach(order => {
  const exists = db.orders.findOne({ orderId: order.orderId });
  if (!exists) {
    db.orders.insertOne(order);
  }
});

print("✅ Seeds de orders insertados");

// ----------------------------------------------------------------------------
// 2.4. SEED: kb_interactions (Interacciones de Base de Conocimiento)
// ----------------------------------------------------------------------------
// Estructura basada en base_conocimiento_dinamica.py líneas 18-33 y 250-266
const kbInteractionsSeed = [
  {
    timestamp: new Date("2025-01-10T09:00:00Z"),
    cliente_id: "099123456",
    tipo_interaccion: "cotizacion",
    mensaje_cliente: "Necesito cotizar Isodec para un proyecto en Punta del Este",
    respuesta_agente: "Te ayudo con la cotización. ¿Podrías indicarme las dimensiones y espesor necesario?",
    contexto: {
      producto_interes: "isodec",
      zona: "Punta del Este",
      tipo_proyecto: "residencial"
    },
    resultado: "exitoso",
    valor_cotizacion: 75000.00,
    valor_venta: null,
    satisfaccion_cliente: 4,
    lecciones_aprendidas: [
      "Clientes de Punta del Este suelen requerir instalación",
      "Isodec es popular para proyectos residenciales en zona costera"
    ]
  },
  {
    timestamp: new Date("2025-01-11T11:30:00Z"),
    cliente_id: "098765432",
    tipo_interaccion: "venta",
    mensaje_cliente: "Confirmo la compra del poliestireno que cotizamos",
    respuesta_agente: "Excelente, procederemos con el pedido. Te contactaremos para coordinar el envío.",
    contexto: {
      producto_interes: "poliestireno",
      zona: "Montevideo",
      tipo_proyecto: "comercial"
    },
    resultado: "exitoso",
    valor_cotizacion: 32000.00,
    valor_venta: 32000.00,
    satisfaccion_cliente: 5,
    lecciones_aprendidas: [
      "Poliestireno tiene buena tasa de conversión en proyectos comerciales",
      "Clientes de Montevideo valoran rapidez en respuesta"
    ]
  },
  {
    timestamp: new Date("2025-01-12T15:45:00Z"),
    cliente_id: "097654321",
    tipo_interaccion: "consulta",
    mensaje_cliente: "¿Qué diferencia hay entre Isodec y Isoroof?",
    respuesta_agente: "Isodec es un panel aislante con núcleo EPS y caras de chapa, ideal para techos. Isoroof es específicamente diseñado para techos con mejor resistencia a la intemperie.",
    contexto: {
      tipo_consulta: "comparacion_productos",
      productos_mencionados: ["isodec", "isoroof"]
    },
    resultado: "exitoso",
    valor_cotizacion: null,
    valor_venta: null,
    satisfaccion_cliente: 4,
    lecciones_aprendidas: [
      "Comparaciones de productos generan interés",
      "Explicaciones técnicas claras mejoran satisfacción"
    ]
  },
  {
    timestamp: new Date("2025-01-13T10:00:00Z"),
    cliente_id: "096543210",
    tipo_interaccion: "cotizacion",
    mensaje_cliente: "Necesito cotizar chapas galvanizadas para un galpón",
    respuesta_agente: "Perfecto, tenemos chapas galvanizadas disponibles. ¿Qué espesor y dimensiones necesitas?",
    contexto: {
      producto_interes: "chapa_galvanizada",
      zona: "Montevideo",
      tipo_proyecto: "galpon"
    },
    resultado: "exitoso",
    valor_cotizacion: 45000.00,
    valor_venta: null,
    satisfaccion_cliente: 5,
    lecciones_aprendidas: [
      "Chapas son populares para proyectos de galpones",
      "Clientes valoran rapidez en respuesta para materiales estructurales"
    ]
  },
  {
    timestamp: new Date("2025-01-14T14:30:00Z"),
    cliente_id: "095432109",
    tipo_interaccion: "venta",
    mensaje_cliente: "Confirmo la compra del Isopanel que cotizamos",
    respuesta_agente: "Excelente, procederemos con el pedido. Te contactaremos para coordinar el envío.",
    contexto: {
      producto_interes: "isopanel",
      zona: "Maldonado",
      tipo_proyecto: "residencial"
    },
    resultado: "exitoso",
    valor_cotizacion: 28000.00,
    valor_venta: 28000.00,
    satisfaccion_cliente: 5,
    lecciones_aprendidas: [
      "Isopanel tiene buena aceptación para proyectos residenciales",
      "Clientes de Maldonado valoran productos de calidad"
    ]
  }
];

// Insertar kb_interactions (verificar duplicados por cliente_id + timestamp)
kbInteractionsSeed.forEach(interaction => {
  const exists = db.kb_interactions.findOne({
    cliente_id: interaction.cliente_id,
    timestamp: interaction.timestamp
  });
  if (!exists) {
    db.kb_interactions.insertOne(interaction);
  }
});

print("✅ Seeds de kb_interactions insertados");

// ----------------------------------------------------------------------------
// 2.5. SEED: context (Contexto de Sesiones)
// ----------------------------------------------------------------------------
// Estructura basada en python-scripts/shared_context_service.py
const contextSeed = [
  {
    session_id: "session_001_20250101",
    user_phone: "099123456",
    cliente_id: "099123456",
    intent: "cotizacion",
    entities: {
      producto: "isodec",
      zona: "Punta del Este"
    },
    quote_state: {
      estado: "en_proceso",
      datos_cliente: {
        nombre: "Gabriel",
        telefono: "099123456",
        direccion: "Cancha de Punta del Este"
      },
      datos_producto: {
        tipo: "isodec",
        espesor: "100mm",
        dimensiones: {
          largo: 10,
          ancho: 5
        }
      }
    },
    messages: [
      {
        role: "user",
        content: "Hola, necesito cotizar Isodec para un proyecto",
        timestamp: new Date("2025-01-15T10:30:00Z")
      },
      {
        role: "assistant",
        content: "¡Hola! Te ayudo con la cotización de Isodec. ¿Podrías indicarme las dimensiones?",
        timestamp: new Date("2025-01-15T10:30:05Z")
      }
    ],
    last_activity: new Date("2025-01-15T10:30:05Z"),
    created_at: new Date("2025-01-15T10:30:00Z")
  }
];

// Insertar context (verificar duplicados por session_id)
contextSeed.forEach(ctx => {
  const exists = db.context.findOne({ session_id: ctx.session_id });
  if (!exists) {
    db.context.insertOne(ctx);
  }
});

print("✅ Seeds de context insertados");

// ----------------------------------------------------------------------------
// 2.6. SEED: sessions (Sesiones)
// ----------------------------------------------------------------------------
// Estructura basada en python-scripts/shared_context_service.py
const sessionsSeed = [
  {
    session_id: "session_001_20250101",
    user_phone: "099123456",
    created_at: new Date("2025-01-15T10:30:00Z"),
    last_activity: new Date("2025-01-15T10:30:05Z"),
    metadata: {
      agent_type: "fastapi",
      source: "api",
      request_id: "req_001"
    },
    active: true
  },
  {
    session_id: "session_002_20250101",
    user_phone: "098765432",
    created_at: new Date("2025-01-15T11:15:00Z"),
    last_activity: new Date("2025-01-15T11:20:00Z"),
    metadata: {
      agent_type: "fastapi",
      source: "api",
      request_id: "req_002"
    },
    active: true
  }
];

// Insertar sessions (verificar duplicados por session_id)
sessionsSeed.forEach(session => {
  const exists = db.sessions.findOne({ session_id: session.session_id });
  if (!exists) {
    db.sessions.insertOne(session);
  }
});

print("✅ Seeds de sessions insertados");

// ----------------------------------------------------------------------------
// 2.7. SEED: followups (Seguimientos)
// ----------------------------------------------------------------------------
// Estructura basada en background_agent_followup.py
const followupsSeed = [
  {
    quote_id: "COT-20250115103000",
    cliente_telefono: "099123456",
    estado: "pending",
    fecha_programada: new Date("2025-01-16T10:00:00Z"),
    tipo: "reminder",
    mensaje: "Recordatorio: seguimiento de cotización pendiente",
    created_at: new Date("2025-01-15T10:30:00Z"),
    executed_at: null
  },
  {
    quote_id: "COT-20250115111500",
    cliente_telefono: "098765432",
    estado: "completed",
    fecha_programada: new Date("2025-01-15T12:00:00Z"),
    tipo: "follow_up",
    mensaje: "Seguimiento post-envío de cotización",
    created_at: new Date("2025-01-15T11:15:00Z"),
    executed_at: new Date("2025-01-15T12:00:00Z")
  }
];

// Insertar followups (verificar duplicados por quote_id + fecha_programada)
followupsSeed.forEach(followup => {
  const exists = db.followups.findOne({
    quote_id: followup.quote_id,
    fecha_programada: followup.fecha_programada
  });
  if (!exists) {
    db.followups.insertOne(followup);
  }
});

print("✅ Seeds de followups insertados");

// ============================================================================
// 3. QUERIES BÁSICAS
// ============================================================================

// ----------------------------------------------------------------------------
// 3.1. CONVERSATIONS - Queries básicas
// ----------------------------------------------------------------------------
print("\n📊 QUERIES BÁSICAS - CONVERSATIONS");

// Contar total de conversaciones
const totalConversations = db.conversations.countDocuments({});
print(`Total de conversaciones: ${totalConversations}`);

// Buscar conversaciones por teléfono
const conversationsByPhone = db.conversations.find({
  phone: "099123456"
}).toArray();
print(`Conversaciones del teléfono 099123456: ${conversationsByPhone.length}`);

// Buscar conversaciones por intent
const conversationsByIntent = db.conversations.find({
  intent: "cotizacion"
}).toArray();
print(`Conversaciones con intent 'cotizacion': ${conversationsByIntent.length}`);

// Buscar conversaciones recientes (últimas 24 horas)
const recentConversations = db.conversations.find({
  timestamp: {
    $gte: new Date(Date.now() - 24 * 60 * 60 * 1000)
  }
}).sort({ timestamp: -1 }).limit(10).toArray();
print(`Conversaciones recientes (24h): ${recentConversations.length}`);

// Distinct de teléfonos únicos
const uniquePhones = db.conversations.distinct("phone");
print(`Teléfonos únicos: ${uniquePhones.length}`);

// ----------------------------------------------------------------------------
// 3.2. QUOTES - Queries básicas
// ----------------------------------------------------------------------------
print("\n📊 QUERIES BÁSICAS - QUOTES");

// Contar total de cotizaciones
const totalQuotes = db.quotes.countDocuments({});
print(`Total de cotizaciones: ${totalQuotes}`);

// Buscar cotizaciones por estado
const quotesByEstado = db.quotes.find({
  estado: "Pendiente"
}).toArray();
print(`Cotizaciones pendientes: ${quotesByEstado.length}`);

// Buscar cotizaciones por origen
const quotesByOrigen = db.quotes.find({
  origen: "WA"
}).toArray();
print(`Cotizaciones desde WhatsApp: ${quotesByOrigen.length}`);

// Buscar cotizaciones por cliente
const quotesByCliente = db.quotes.find({
  cliente: "Gabriel"
}).toArray();
print(`Cotizaciones del cliente Gabriel: ${quotesByCliente.length}`);

// Distinct de estados
const uniqueEstados = db.quotes.distinct("estado");
print(`Estados únicos: ${uniqueEstados.join(", ")}`);

// Distinct de orígenes
const uniqueOrigenes = db.quotes.distinct("origen");
print(`Orígenes únicos: ${uniqueOrigenes.join(", ")}`);

// ----------------------------------------------------------------------------
// 3.3. ORDERS - Queries básicas
// ----------------------------------------------------------------------------
print("\n📊 QUERIES BÁSICAS - ORDERS");

// Contar total de órdenes
const totalOrders = db.orders.countDocuments({});
print(`Total de órdenes: ${totalOrders}`);

// Buscar órdenes por estado
const ordersByStatus = db.orders.find({
  status: "paid"
}).toArray();
print(`Órdenes pagadas: ${ordersByStatus.length}`);

// Buscar órdenes listas para enviar
const readyToShip = db.orders.find({
  readyToShip: true
}).toArray();
print(`Órdenes listas para enviar: ${readyToShip.length}`);

// Buscar órdenes por rango de monto
const ordersByAmount = db.orders.find({
  totalAmount: {
    $gte: 10000,
    $lte: 20000
  }
}).toArray();
print(`Órdenes entre $10,000 y $20,000: ${ordersByAmount.length}`);

// Distinct de estados
const uniqueOrderStatuses = db.orders.distinct("status");
print(`Estados únicos de órdenes: ${uniqueOrderStatuses.join(", ")}`);

// ----------------------------------------------------------------------------
// 3.4. KB_INTERACTIONS - Queries básicas
// ----------------------------------------------------------------------------
print("\n📊 QUERIES BÁSICAS - KB_INTERACTIONS");

// Contar total de interacciones
const totalInteractions = db.kb_interactions.countDocuments({});
print(`Total de interacciones KB: ${totalInteractions}`);

// Buscar interacciones por tipo
const interactionsByType = db.kb_interactions.find({
  tipo_interaccion: "venta"
}).toArray();
print(`Interacciones de tipo 'venta': ${interactionsByType.length}`);

// Buscar interacciones exitosas
const successfulInteractions = db.kb_interactions.find({
  resultado: "exitoso"
}).toArray();
print(`Interacciones exitosas: ${successfulInteractions.length}`);

// Buscar interacciones con ventas
const interactionsWithSales = db.kb_interactions.find({
  valor_venta: { $ne: null }
}).toArray();
print(`Interacciones con ventas: ${interactionsWithSales.length}`);

// Distinct de tipos de interacción
const uniqueInteractionTypes = db.kb_interactions.distinct("tipo_interaccion");
print(`Tipos de interacción únicos: ${uniqueInteractionTypes.join(", ")}`);

// ============================================================================
// 4. QUERIES ANALÍTICAS (AGGREGATE)
// ============================================================================

// ----------------------------------------------------------------------------
// 4.1. CONVERSATIONS - Análisis agregado
// ----------------------------------------------------------------------------
print("\n📈 QUERIES ANALÍTICAS - CONVERSATIONS");

// Agregación: Conversaciones por intent
const conversationsByIntentAgg = db.conversations.aggregate([
  {
    $group: {
      _id: "$intent",
      count: { $sum: 1 },
      avgConfidence: { $avg: "$confidence" }
    }
  },
  {
    $sort: { count: -1 }
  }
]).toArray();
print("Conversaciones por intent:");
conversationsByIntentAgg.forEach(item => {
  print(`  ${item._id}: ${item.count} (confianza promedio: ${item.avgConfidence.toFixed(2)})`);
});

// Agregación: Conversaciones por día
const conversationsByDay = db.conversations.aggregate([
  {
    $group: {
      _id: {
        $dateToString: {
          format: "%Y-%m-%d",
          date: "$timestamp"
        }
      },
      count: { $sum: 1 }
    }
  },
  {
    $sort: { _id: -1 }
  }
]).toArray();
print("Conversaciones por día:");
conversationsByDay.forEach(item => {
  print(`  ${item._id}: ${item.count}`);
});

// Agregación: Top teléfonos por número de conversaciones
const topPhones = db.conversations.aggregate([
  {
    $group: {
      _id: "$phone",
      count: { $sum: 1 }
    }
  },
  {
    $sort: { count: -1 }
  },
  {
    $limit: 5
  }
]).toArray();
print("Top 5 teléfonos por conversaciones:");
topPhones.forEach((item, index) => {
  print(`  ${index + 1}. ${item._id}: ${item.count} conversaciones`);
});

// ----------------------------------------------------------------------------
// 4.2. QUOTES - Análisis agregado
// ----------------------------------------------------------------------------
print("\n📈 QUERIES ANALÍTICAS - QUOTES");

// Agregación: Cotizaciones por estado
const quotesByEstadoAgg = db.quotes.aggregate([
  {
    $group: {
      _id: "$estado",
      count: { $sum: 1 }
    }
  },
  {
    $sort: { count: -1 }
  }
]).toArray();
print("Cotizaciones por estado:");
quotesByEstadoAgg.forEach(item => {
  print(`  ${item._id}: ${item.count}`);
});

// Agregación: Cotizaciones por origen
const quotesByOrigenAgg = db.quotes.aggregate([
  {
    $group: {
      _id: "$origen",
      count: { $sum: 1 }
    }
  },
  {
    $sort: { count: -1 }
  }
]).toArray();
print("Cotizaciones por origen:");
quotesByOrigenAgg.forEach(item => {
  print(`  ${item._id}: ${item.count}`);
});

// Agregación: Productos más cotizados
const productosMasCotizados = db.quotes.aggregate([
  {
    $match: {
      "parsed.producto.tipo": { $exists: true }
    }
  },
  {
    $group: {
      _id: "$parsed.producto.tipo",
      count: { $sum: 1 }
    }
  },
  {
    $sort: { count: -1 }
  }
]).toArray();
print("Productos más cotizados:");
productosMasCotizados.forEach(item => {
  print(`  ${item._id}: ${item.count} cotizaciones`);
});

// Agregación: Cotizaciones por mes
const quotesByMonth = db.quotes.aggregate([
  {
    $group: {
      _id: {
        $dateToString: {
          format: "%Y-%m",
          date: "$createdAt"
        }
      },
      count: { $sum: 1 }
    }
  },
  {
    $sort: { _id: -1 }
  }
]).toArray();
print("Cotizaciones por mes:");
quotesByMonth.forEach(item => {
  print(`  ${item._id}: ${item.count}`);
});

// ----------------------------------------------------------------------------
// 4.3. ORDERS - Análisis agregado
// ----------------------------------------------------------------------------
print("\n📈 QUERIES ANALÍTICAS - ORDERS");

// Agregación: Órdenes por estado
const ordersByStatusAgg = db.orders.aggregate([
  {
    $group: {
      _id: "$status",
      count: { $sum: 1 },
      totalAmount: { $sum: "$totalAmount" }
    }
  },
  {
    $sort: { count: -1 }
  }
]).toArray();
print("Órdenes por estado:");
ordersByStatusAgg.forEach(item => {
  print(`  ${item._id}: ${item.count} órdenes, Total: $${item.totalAmount.toFixed(2)}`);
});

// Agregación: Total de ventas por mes
const salesByMonth = db.orders.aggregate([
  {
    $group: {
      _id: {
        $dateToString: {
          format: "%Y-%m",
          date: "$createdAt"
        }
      },
      count: { $sum: 1 },
      totalAmount: { $sum: "$totalAmount" }
    }
  },
  {
    $sort: { _id: -1 }
  }
]).toArray();
print("Ventas por mes:");
salesByMonth.forEach(item => {
  print(`  ${item._id}: ${item.count} órdenes, Total: $${item.totalAmount.toFixed(2)}`);
});

// Agregación: Métodos de pago más usados
const paymentMethods = db.orders.aggregate([
  {
    $unwind: "$payments"
  },
  {
    $group: {
      _id: "$payments.method",
      count: { $sum: 1 },
      totalAmount: { $sum: "$payments.transaction_amount" }
    }
  },
  {
    $sort: { count: -1 }
  }
]).toArray();
print("Métodos de pago:");
paymentMethods.forEach(item => {
  print(`  ${item._id || "N/A"}: ${item.count} pagos, Total: $${item.totalAmount.toFixed(2)}`);
});

// ----------------------------------------------------------------------------
// 4.4. KB_INTERACTIONS - Análisis agregado
// ----------------------------------------------------------------------------
print("\n📈 QUERIES ANALÍTICAS - KB_INTERACTIONS");

// Agregación: Interacciones por tipo
const interactionsByTypeAgg = db.kb_interactions.aggregate([
  {
    $group: {
      _id: "$tipo_interaccion",
      count: { $sum: 1 },
      avgSatisfaction: { $avg: "$satisfaccion_cliente" }
    }
  },
  {
    $sort: { count: -1 }
  }
]).toArray();
print("Interacciones por tipo:");
interactionsByTypeAgg.forEach(item => {
  const avgSat = item.avgSatisfaction ? item.avgSatisfaction.toFixed(2) : "N/A";
  print(`  ${item._id}: ${item.count} (satisfacción promedio: ${avgSat})`);
});

// Agregación: Tasa de conversión (cotización -> venta)
const conversionRate = db.kb_interactions.aggregate([
  {
    $group: {
      _id: null,
      totalInteractions: { $sum: 1 },
      totalSales: {
        $sum: {
          $cond: [{ $ne: ["$valor_venta", null] }, 1, 0]
        }
      },
      totalQuotes: {
        $sum: {
          $cond: [{ $ne: ["$valor_cotizacion", null] }, 1, 0]
        }
      }
    }
  },
  {
    $project: {
      totalInteractions: 1,
      totalSales: 1,
      totalQuotes: 1,
      conversionRate: {
        $cond: [
          { $gt: ["$totalQuotes", 0] },
          { $multiply: [{ $divide: ["$totalSales", "$totalQuotes"] }, 100] },
          0
        ]
      }
    }
  }
]).toArray();
if (conversionRate.length > 0) {
  const stats = conversionRate[0];
  print("Estadísticas de conversión:");
  print(`  Total interacciones: ${stats.totalInteractions}`);
  print(`  Total cotizaciones: ${stats.totalQuotes}`);
  print(`  Total ventas: ${stats.totalSales}`);
  print(`  Tasa de conversión: ${stats.conversionRate.toFixed(2)}%`);
}

// Agregación: Valor promedio de cotizaciones y ventas
const avgValues = db.kb_interactions.aggregate([
  {
    $group: {
      _id: null,
      avgQuote: { $avg: "$valor_cotizacion" },
      avgSale: { $avg: "$valor_venta" }
    }
  }
]).toArray();
if (avgValues.length > 0) {
  const avgs = avgValues[0];
  print("Valores promedio:");
  print(`  Cotización promedio: $${avgs.avgQuote ? avgs.avgQuote.toFixed(2) : "N/A"}`);
  print(`  Venta promedio: $${avgs.avgSale ? avgs.avgSale.toFixed(2) : "N/A"}`);
}

// ============================================================================
// 5. VALIDACIONES DE INTEGRIDAD
// ============================================================================

print("\n🔍 VALIDACIONES DE INTEGRIDAD");

// ----------------------------------------------------------------------------
// 5.1. Validar estructura de conversations
// ----------------------------------------------------------------------------
const conversationsInvalid = db.conversations.find({
  $or: [
    { session_id: { $exists: false } },
    { phone: { $exists: false } },
    { message: { $exists: false } },
    { timestamp: { $exists: false } }
  ]
}).toArray();
if (conversationsInvalid.length > 0) {
  print(`⚠️  Conversaciones con campos faltantes: ${conversationsInvalid.length}`);
} else {
  print("✅ Todas las conversaciones tienen campos requeridos");
}

// ----------------------------------------------------------------------------
// 5.2. Validar estructura de quotes
// ----------------------------------------------------------------------------
const quotesInvalid = db.quotes.find({
  $or: [
    { arg: { $exists: false } },
    { estado: { $exists: false } },
    { cliente: { $exists: false } },
    { origen: { $exists: false } }
  ]
}).toArray();
if (quotesInvalid.length > 0) {
  print(`⚠️  Cotizaciones con campos faltantes: ${quotesInvalid.length}`);
} else {
  print("✅ Todas las cotizaciones tienen campos requeridos");
}

// Validar estados válidos
const validEstados = ["Pendiente", "Adjunto", "Listo", "Enviado", "Asignado", "Confirmado"];
const quotesInvalidEstado = db.quotes.find({
  estado: { $nin: validEstados }
}).toArray();
if (quotesInvalidEstado.length > 0) {
  print(`⚠️  Cotizaciones con estados inválidos: ${quotesInvalidEstado.length}`);
} else {
  print("✅ Todos los estados de cotizaciones son válidos");
}

// Validar orígenes válidos
const validOrigenes = ["WA", "LO", "EM", "CL"];
const quotesInvalidOrigen = db.quotes.find({
  origen: { $nin: validOrigenes }
}).toArray();
if (quotesInvalidOrigen.length > 0) {
  print(`⚠️  Cotizaciones con orígenes inválidos: ${quotesInvalidOrigen.length}`);
} else {
  print("✅ Todos los orígenes de cotizaciones son válidos");
}

// ----------------------------------------------------------------------------
// 5.3. Validar estructura de orders
// ----------------------------------------------------------------------------
const ordersInvalid = db.orders.find({
  $or: [
    { orderId: { $exists: false } },
    { status: { $exists: false } },
    { totalAmount: { $exists: false } }
  ]
}).toArray();
if (ordersInvalid.length > 0) {
  print(`⚠️  Órdenes con campos faltantes: ${ordersInvalid.length}`);
} else {
  print("✅ Todas las órdenes tienen campos requeridos");
}

// Validar órdenes duplicadas
const duplicateOrders = db.orders.aggregate([
  {
    $group: {
      _id: "$orderId",
      count: { $sum: 1 }
    }
  },
  {
    $match: {
      count: { $gt: 1 }
    }
  }
]).toArray();
if (duplicateOrders.length > 0) {
  print(`⚠️  Órdenes duplicadas encontradas: ${duplicateOrders.length}`);
} else {
  print("✅ No hay órdenes duplicadas");
}

// ----------------------------------------------------------------------------
// 5.4. Validar referencias entre colecciones
// ----------------------------------------------------------------------------
// Verificar que las conversaciones tienen sesiones correspondientes
const conversationsWithoutSessions = db.conversations.find({
  session_id: { $exists: true }
}).toArray().filter(conv => {
  const session = db.sessions.findOne({ session_id: conv.session_id });
  return !session;
});
if (conversationsWithoutSessions.length > 0) {
  print(`⚠️  Conversaciones sin sesión correspondiente: ${conversationsWithoutSessions.length}`);
} else {
  print("✅ Todas las conversaciones tienen sesiones correspondientes");
}

// Verificar que los followups tienen quotes correspondientes
const followupsWithoutQuotes = db.followups.find({
  quote_id: { $exists: true }
}).toArray().filter(followup => {
  const quote = db.quotes.findOne({ arg: followup.quote_id });
  return !quote;
});
if (followupsWithoutQuotes.length > 0) {
  print(`⚠️  Followups sin cotización correspondiente: ${followupsWithoutQuotes.length}`);
} else {
  print("✅ Todos los followups tienen cotizaciones correspondientes");
}

// ============================================================================
// 6. ÍNDICES RECOMENDADOS
// ============================================================================

print("\n📑 CREANDO ÍNDICES RECOMENDADOS");

// ----------------------------------------------------------------------------
// 6.1. Índices para conversations
// ----------------------------------------------------------------------------
try {
  db.conversations.createIndex({ session_id: 1, timestamp: 1 });
  print("✅ Índice creado: conversations (session_id, timestamp)");
} catch (e) {
  print(`⚠️  Error creando índice conversations: ${e.message}`);
}

try {
  db.conversations.createIndex({ phone: 1, timestamp: -1 });
  print("✅ Índice creado: conversations (phone, timestamp)");
} catch (e) {
  print(`⚠️  Error creando índice conversations: ${e.message}`);
}

try {
  db.conversations.createIndex({ intent: 1 });
  print("✅ Índice creado: conversations (intent)");
} catch (e) {
  print(`⚠️  Error creando índice conversations: ${e.message}`);
}

try {
  db.conversations.createIndex({ timestamp: -1 });
  print("✅ Índice creado: conversations (timestamp)");
} catch (e) {
  print(`⚠️  Error creando índice conversations: ${e.message}`);
}

// ----------------------------------------------------------------------------
// 6.2. Índices para quotes
// ----------------------------------------------------------------------------
try {
  db.quotes.createIndex({ arg: 1 }, { unique: true });
  print("✅ Índice único creado: quotes (arg)");
} catch (e) {
  print(`⚠️  Error creando índice quotes: ${e.message}`);
}

try {
  db.quotes.createIndex({ estado: 1, createdAt: -1 });
  print("✅ Índice creado: quotes (estado, createdAt)");
} catch (e) {
  print(`⚠️  Error creando índice quotes: ${e.message}`);
}

try {
  db.quotes.createIndex({ origen: 1 });
  print("✅ Índice creado: quotes (origen)");
} catch (e) {
  print(`⚠️  Error creando índice quotes: ${e.message}`);
}

try {
  db.quotes.createIndex({ cliente: 1, telefono: 1 });
  print("✅ Índice creado: quotes (cliente, telefono)");
} catch (e) {
  print(`⚠️  Error creando índice quotes: ${e.message}`);
}

try {
  db.quotes.createIndex({ "parsed.producto.tipo": 1 });
  print("✅ Índice creado: quotes (parsed.producto.tipo)");
} catch (e) {
  print(`⚠️  Error creando índice quotes: ${e.message}`);
}

// ----------------------------------------------------------------------------
// 6.3. Índices para orders
// ----------------------------------------------------------------------------
try {
  db.orders.createIndex({ orderId: 1 }, { unique: true });
  print("✅ Índice único creado: orders (orderId)");
} catch (e) {
  print(`⚠️  Error creando índice orders: ${e.message}`);
}

try {
  db.orders.createIndex({ status: 1, createdAt: -1 });
  print("✅ Índice creado: orders (status, createdAt)");
} catch (e) {
  print(`⚠️  Error creando índice orders: ${e.message}`);
}

try {
  db.orders.createIndex({ readyToShip: 1 });
  print("✅ Índice creado: orders (readyToShip)");
} catch (e) {
  print(`⚠️  Error creando índice orders: ${e.message}`);
}

try {
  db.orders.createIndex({ "buyer.id": 1 });
  print("✅ Índice creado: orders (buyer.id)");
} catch (e) {
  print(`⚠️  Error creando índice orders: ${e.message}`);
}

// ----------------------------------------------------------------------------
// 6.4. Índices para kb_interactions
// ----------------------------------------------------------------------------
try {
  db.kb_interactions.createIndex({ cliente_id: 1, timestamp: -1 });
  print("✅ Índice creado: kb_interactions (cliente_id, timestamp)");
} catch (e) {
  print(`⚠️  Error creando índice kb_interactions: ${e.message}`);
}

try {
  db.kb_interactions.createIndex({ tipo_interaccion: 1 });
  print("✅ Índice creado: kb_interactions (tipo_interaccion)");
} catch (e) {
  print(`⚠️  Error creando índice kb_interactions: ${e.message}`);
}

try {
  db.kb_interactions.createIndex({ resultado: 1 });
  print("✅ Índice creado: kb_interactions (resultado)");
} catch (e) {
  print(`⚠️  Error creando índice kb_interactions: ${e.message}`);
}

// ----------------------------------------------------------------------------
// 6.5. Índices para context
// ----------------------------------------------------------------------------
try {
  db.context.createIndex({ session_id: 1 }, { unique: true });
  print("✅ Índice único creado: context (session_id)");
} catch (e) {
  print(`⚠️  Error creando índice context: ${e.message}`);
}

try {
  db.context.createIndex({ user_phone: 1, last_activity: -1 });
  print("✅ Índice creado: context (user_phone, last_activity)");
} catch (e) {
  print(`⚠️  Error creando índice context: ${e.message}`);
}

// ----------------------------------------------------------------------------
// 6.6. Índices para sessions
// ----------------------------------------------------------------------------
try {
  db.sessions.createIndex({ session_id: 1 }, { unique: true });
  print("✅ Índice único creado: sessions (session_id)");
} catch (e) {
  print(`⚠️  Error creando índice sessions: ${e.message}`);
}

try {
  db.sessions.createIndex({ user_phone: 1, last_activity: -1 });
  print("✅ Índice creado: sessions (user_phone, last_activity)");
} catch (e) {
  print(`⚠️  Error creando índice sessions: ${e.message}`);
}

try {
  db.sessions.createIndex({ active: 1 });
  print("✅ Índice creado: sessions (active)");
} catch (e) {
  print(`⚠️  Error creando índice sessions: ${e.message}`);
}

// ----------------------------------------------------------------------------
// 6.7. Índices para followups
// ----------------------------------------------------------------------------
try {
  db.followups.createIndex({ quote_id: 1, fecha_programada: 1 });
  print("✅ Índice creado: followups (quote_id, fecha_programada)");
} catch (e) {
  print(`⚠️  Error creando índice followups: ${e.message}`);
}

try {
  db.followups.createIndex({ estado: 1, fecha_programada: 1 });
  print("✅ Índice creado: followups (estado, fecha_programada)");
} catch (e) {
  print(`⚠️  Error creando índice followups: ${e.message}`);
}

// ============================================================================
// 7. UTILIDADES DE DEBUGGING
// ============================================================================

print("\n🔧 UTILIDADES DE DEBUGGING");

// ----------------------------------------------------------------------------
// 7.1. Estadísticas generales de la base de datos
// ----------------------------------------------------------------------------
print("\n📊 ESTADÍSTICAS GENERALES:");
const stats = {
  conversations: db.conversations.countDocuments({}),
  quotes: db.quotes.countDocuments({}),
  orders: db.orders.countDocuments({}),
  kb_interactions: db.kb_interactions.countDocuments({}),
  context: db.context.countDocuments({}),
  sessions: db.sessions.countDocuments({}),
  followups: db.followups.countDocuments({})
};
print(JSON.stringify(stats, null, 2));

// ----------------------------------------------------------------------------
// 7.2. Verificar colecciones existentes
// ----------------------------------------------------------------------------
print("\n📁 COLECCIONES EN LA BASE DE DATOS:");
const collections = db.getCollectionNames();
collections.forEach(col => {
  const count = db[col].countDocuments({});
  print(`  ${col}: ${count} documentos`);
});

// ----------------------------------------------------------------------------
// 7.3. Buscar documentos con campos faltantes
// ----------------------------------------------------------------------------
print("\n🔍 DOCUMENTOS CON CAMPOS FALTANTES:");
const missingFields = {
  conversations: db.conversations.countDocuments({
    $or: [
      { session_id: null },
      { phone: null },
      { message: null }
    ]
  }),
  quotes: db.quotes.countDocuments({
    $or: [
      { arg: null },
      { estado: null },
      { cliente: null }
    ]
  }),
  orders: db.orders.countDocuments({
    $or: [
      { orderId: null },
      { status: null }
    ]
  })
};
print(JSON.stringify(missingFields, null, 2));

// ----------------------------------------------------------------------------
// 7.4. Verificar índices existentes
// ----------------------------------------------------------------------------
print("\n📑 ÍNDICES EXISTENTES:");
const collectionsWithIndexes = ["conversations", "quotes", "orders", "kb_interactions", "context", "sessions", "followups"];
collectionsWithIndexes.forEach(colName => {
  const indexes = db[colName].getIndexes();
  print(`\n${colName}:`);
  indexes.forEach(idx => {
    print(`  - ${idx.name}: ${JSON.stringify(idx.key)}`);
  });
});

// ----------------------------------------------------------------------------
// 7.5. Query de ejemplo: Buscar cotización completa con contexto
// ----------------------------------------------------------------------------
print("\n🔍 EJEMPLO: Cotización completa con contexto relacionado");
const exampleQuote = db.quotes.findOne({ estado: "Pendiente" });
if (exampleQuote) {
  print(`Cotización: ${exampleQuote.arg}`);
  print(`Cliente: ${exampleQuote.cliente} (${exampleQuote.telefono})`);

  // Buscar conversaciones relacionadas
  const relatedConversations = db.conversations.find({
    phone: exampleQuote.telefono
  }).limit(3).toArray();
  print(`Conversaciones relacionadas: ${relatedConversations.length}`);

  // Buscar contexto de sesión
  const relatedContext = db.context.find({
    user_phone: exampleQuote.telefono
  }).limit(1).toArray();
  print(`Contextos relacionados: ${relatedContext.length}`);
}

// ============================================================================
// 8. EXPORT_SEAL
// ============================================================================
// Bloque de metadatos según política del proyecto BMC

const EXPORT_SEAL = {
  project: "BMC-Automatizaciones",
  prompt_id: "mongodb-playground-bmc-chatbot-2311",
  version: "1.0.0",
  file: "bmc_mongodb_playground.mongodb.js",
  lang: "javascript",
  created_at: new Date().toISOString(),
  author: "Cursor AI Agent",
  origin: "chatbot-2311-workspace-analysis",
  description: "MongoDB Playground completo para sistema BMC, generado desde estructura real del workspace",
  collections: [
    "conversations",
    "quotes",
    "orders",
    "kb_interactions",
    "context",
    "sessions",
    "followups"
  ],
  database: "bmc_chat",
  features: [
    "seeds_idempotentes",
    "queries_basicas",
    "queries_analiticas",
    "validaciones_integridad",
    "indices_recomendados",
    "utilidades_debugging"
  ]
};

print("\n✅ EXPORT_SEAL:");
print(JSON.stringify(EXPORT_SEAL, null, 2));

print("\n" + "=".repeat(80));
print("✅ MONGODB PLAYGROUND COMPLETO - BMC CHATBOT-2311");
print("=".repeat(80));
print("\nEste Playground está completamente alineado con el proyecto BMC.");
print("Todas las estructuras, campos y colecciones están basados en el código real.");
print("\nPara ejecutar este Playground:");
print("1. Abre MongoDB Compass o MongoDB Shell");
print("2. Conecta a tu base de datos (MONGODB_URI del .env)");
print("3. Copia y pega este archivo completo");
print("4. Ejecuta sección por sección o completo");
print("\n⚠️  NOTA: Los seeds son idempotentes y verifican duplicados antes de insertar.");
print("=".repeat(80));

