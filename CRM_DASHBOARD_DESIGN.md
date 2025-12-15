# CRM Dashboard - Visual Design Mockup

## Layout Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  🏗️ BMC CRM                                    👤 Usuario    🔔 (3)    ⚙️   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  📊 Resumen General                                                  │   │
│  │  ┌──────────────┬──────────────┬──────────────┬──────────────┐      │   │
│  │  │ 💬 Pendientes│ 📧 Enviados  │ ✅ Confirmados│ 💰 Revenue   │      │   │
│  │  │     24       │     15       │      8       │  $45,230     │      │   │
│  │  │  ↑ +3 hoy   │  ↑ +5 hoy   │  ↑ +2 hoy   │  ↑ +$8.5K    │      │   │
│  │  └──────────────┴──────────────┴──────────────┴──────────────┘      │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  🔍 Buscar clientes, ARG, teléfono...              [Filtros ▼]      │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
│  ┌─────────────────────┬─────────────────────┬─────────────────────────┐   │
│  │   💬 PENDIENTES     │   📧 ENVIADOS       │   ✅ CONFIRMADOS        │   │
│  │   (24 cotizaciones) │   (15 cotizaciones) │   (8 cotizaciones)      │   │
│  ├─────────────────────┼─────────────────────┼─────────────────────────┤   │
│  │                     │                     │                         │   │
│  │ ┌─────────────────┐ │ ┌─────────────────┐ │ ┌─────────────────┐   │   │
│  │ │ WA121412345     │ │ │ WA121312234     │ │ │ ML121015678     │   │   │
│  │ │ Juan Pérez      │ │ │ María García    │ │ │ Pedro López     │   │   │
│  │ │ 📱 099 123 456  │ │ │ 📱 098 765 432  │ │ │ 📱 097 111 222  │   │   │
│  │ │ 📅 Hoy 10:30    │ │ │ 📅 Ayer 14:20   │ │ │ 📅 12/12 09:15  │   │   │
│  │ │ 💰 $2,450       │ │ │ 💰 $3,890       │ │ │ 💰 $12,500      │   │   │
│  │ │ 🏷️ WhatsApp     │ │ │ 🏷️ WhatsApp     │ │ │ 🏷️ Mercado Libre│   │   │
│  │ │ Panel Isodec... │ │ │ Chapa Isoroof...│ │ │ 50 paneles...   │   │   │
│  │ │                 │ │ │                 │ │ │                 │   │   │
│  │ │ [Ver] [Enviar]  │ │ │ [Ver] [✓ OK]    │ │ │ [Ver Detalles]  │   │   │
│  │ └─────────────────┘ │ └─────────────────┘ │ └─────────────────┘   │   │
│  │                     │                     │                         │   │
│  │ ┌─────────────────┐ │ ┌─────────────────┐ │ ┌─────────────────┐   │   │
│  │ │ WA121412346     │ │ │ WA121212123     │ │ │ WA121112890     │   │   │
│  │ │ Ana Rodríguez   │ │ │ Carlos Sosa     │ │ │ Laura Martínez  │   │   │
│  │ │ 📱 095 444 555  │ │ │ 📱 099 888 999  │ │ │ 📱 094 777 666  │   │   │
│  │ │ 📅 Hoy 12:15    │ │ │ 📅 13/12 18:00  │ │ │ 📅 11/12 11:30  │   │   │
│  │ │ 💰 $1,850       │ │ │ 💰 $5,200       │ │ │ 💰 $8,900       │   │   │
│  │ │ 🏷️ WhatsApp     │ │ │ 🏷️ WhatsApp     │ │ │ 🏷️ WhatsApp     │   │   │
│  │ │ Isowall 50mm... │ │ │ Instalación...  │ │ │ Panel + flete...│   │   │
│  │ │                 │ │ │                 │ │ │                 │   │   │
│  │ │ [Ver] [Enviar]  │ │ │ [Ver] [✓ OK]    │ │ │ [Ver Detalles]  │   │   │
│  │ └─────────────────┘ │ └─────────────────┘ │ └─────────────────┘   │   │
│  │                     │                     │                         │   │
│  │ ┌─────────────────┐ │ ┌─────────────────┐ │                         │   │
│  │ │ ML120915123     │ │ │ WA121112777     │ │  [Mostrar más...]       │   │
│  │ │ Roberto Silva   │ │ │ Sandra Torres   │ │                         │   │
│  │ │ ...             │ │ │ ...             │ │                         │   │
│  │ └─────────────────┘ │ └─────────────────┘ │                         │   │
│  │                     │                     │                         │   │
│  │  [+ Nueva Cotiz.]   │                     │                         │   │
│  │                     │                     │                         │   │
│  └─────────────────────┴─────────────────────┴─────────────────────────┘   │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Detailed View - Quote Card Click

When clicking "Ver" on any quote card:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ← Volver al tablero                                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  Cliente: Juan Pérez                              🏷️ lead → prospect │   │
│  │  📱 +598 99 123 456  │  📧 +59899123456@whatsapp.bmc.local           │   │
│  │  📍 Montevideo       │  📅 Cliente desde: 14/12/2024                 │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
│  ┌────────────────────────────────────┬────────────────────────────────────┐ │
│  │  📋 COTIZACIÓN WA121412345        │  📊 ESTADÍSTICAS CLIENTE           │ │
│  │                                    │                                    │ │
│  │  Estado: Pendiente                 │  💰 Total cotizaciones: 3          │ │
│  │  Fecha: 14/12/2024 10:30          │  💵 Valor total: $6,780            │ │
│  │  Origen: WhatsApp                  │  ✅ Conversiones: 1                │ │
│  │                                    │  📈 Tasa conversión: 33%           │ │
│  │  ┌──────────────────────────────┐  │  📅 Última interacción: Hoy        │ │
│  │  │ ITEMS                        │  │                                    │ │
│  │  ├──────────────────────────────┤  │  🔔 ACCIONES RÁPIDAS               │ │
│  │  │ • Panel Isodec 100mm         │  │  ┌──────────────────────────────┐  │ │
│  │  │   10 unidades x $150         │  │  │ [📧 Enviar Cotización]       │  │ │
│  │  │   = $1,500                   │  │  │ [✅ Marcar Confirmado]       │  │ │
│  │  │                              │  │  │ [📞 Registrar Llamada]       │  │ │
│  │  │ • Flete - Montevideo         │  │  │ [✉️ Enviar Email]            │  │ │
│  │  │   1 x $200                   │  │  │ [📝 Agregar Nota]            │  │ │
│  │  │   = $200                     │  │  └──────────────────────────────┘  │ │
│  │  │                              │  │                                    │ │
│  │  │ Subtotal:     $1,700         │  │                                    │ │
│  │  │ IVA (22%):     $374          │  │                                    │ │
│  │  │ TOTAL:        $2,074         │  │                                    │ │
│  │  └──────────────────────────────┘  │                                    │ │
│  │                                    │                                    │ │
│  │  📝 Consulta Original:             │                                    │ │
│  │  "Hola, necesito cotizar 10       │                                    │ │
│  │   paneles Isodec de 100mm para    │                                    │ │
│  │   Montevideo con flete"           │                                    │ │
│  │                                    │                                    │ │
│  └────────────────────────────────────┴────────────────────────────────────┘ │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  📅 LÍNEA DE TIEMPO (5 interacciones)                                │   │
│  │                                                                       │   │
│  │  • 14/12 10:35  📧 Cotización enviada por email                      │   │
│  │    Enviado a: +59899123456@whatsapp.bmc.local                       │   │
│  │                                                                       │   │
│  │  • 14/12 10:30  💬 Solicitud de cotización (WhatsApp)                │   │
│  │    "Hola, necesito cotizar 10 paneles Isodec de 100mm..."           │   │
│  │                                                                       │   │
│  │  • 10/12 15:20  📞 Llamada - No responde                             │   │
│  │    Nota: "Dejé mensaje de voz"                                       │   │
│  │                                                                       │   │
│  │  • 08/12 11:45  💬 Consulta anterior (WhatsApp)                      │   │
│  │    Cotización WA120812123 - $1,850                                   │   │
│  │                                                                       │   │
│  │  • 08/12 11:40  👤 Cliente creado                                    │   │
│  │    Origen: WhatsApp                                                  │   │
│  │                                                                       │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  📝 NOTAS (2)                                          [+ Nueva Nota] │   │
│  │                                                                       │   │
│  │  📌 IMPORTANTE (Fijada)                          Usuario - 13/12      │   │
│  │  "Cliente prefiere entregas los lunes. Pagar en efectivo."           │   │
│  │                                                                       │   │
│  │  💭 Nota                                            Usuario - 10/12   │   │
│  │  "Interesado en proyecto más grande para enero"                      │   │
│  │                                                                       │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Analytics Dashboard (Tab adicional)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  🏗️ BMC CRM  │  [Tablero]  [📊 Analytics]  [👥 Clientes]  [⚙️ Config]      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  📊 ANALYTICS - Último mes                                                   │
│                                                                               │
│  ┌────────────────────────┬────────────────────────┬────────────────────┐   │
│  │ 💰 REVENUE             │ 📈 CONVERSIÓN          │ 👥 CLIENTES        │   │
│  │                        │                        │                    │   │
│  │    $45,230             │      53%               │      127           │   │
│  │    ↑ +18% vs mes ant.  │      ↑ +5%             │      ↑ +23         │   │
│  │                        │                        │                    │   │
│  │  ▁▂▃▅▆█▇▆▅▃▂ (gráfico) │  ▂▃▄▅▆▇█ (gráfico)     │  ▁▂▃▄▅▆█ (gráfico) │   │
│  └────────────────────────┴────────────────────────┴────────────────────┘   │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  📊 COTIZACIONES POR DÍA                                             │   │
│  │                                                                       │   │
│  │   15│                                            █                   │   │
│  │   12│                                    █       █                   │   │
│  │    9│                        █           █   █   █   █               │   │
│  │    6│            █       █   █   █       █   █   █   █   █           │   │
│  │    3│    █   █   █   █   █   █   █   █   █   █   █   █   █   █       │   │
│  │    0└──────────────────────────────────────────────────────────────  │   │
│  │      1   3   5   7   9  11  13  15  17  19  21  23  25  27  29  31  │   │
│  │                                                                       │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
│  ┌─────────────────────────────────┬────────────────────────────────────┐   │
│  │  🏷️ POR ORIGEN                 │  📊 POR PRODUCTO                   │   │
│  │                                 │                                    │   │
│  │  WhatsApp      47 (62%)  ████  │  Isodec         23 (35%)   ████    │   │
│  │  Mercado Libre 21 (28%)  ███   │  Isoroof        18 (27%)   ███     │   │
│  │  Manual         8 (10%)  █     │  Chapa          15 (23%)   ███     │   │
│  │                                 │  Isowall         8 (12%)   ██      │   │
│  │                                 │  Instalación     2 (3%)    █       │   │
│  └─────────────────────────────────┴────────────────────────────────────┘   │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  🔥 TOP 10 CLIENTES POR REVENUE                                      │   │
│  │                                                                       │   │
│  │  1. Pedro López       $12,500  ███████████████  [Ver perfil]         │   │
│  │  2. María García       $8,900  ██████████       [Ver perfil]         │   │
│  │  3. Carlos Sosa        $5,200  ██████           [Ver perfil]         │   │
│  │  4. Laura Martínez     $3,890  ████             [Ver perfil]         │   │
│  │  5. Juan Pérez         $2,450  ███              [Ver perfil]         │   │
│  │  6. Ana Rodríguez      $1,850  ██               [Ver perfil]         │   │
│  │  7. Roberto Silva      $1,650  ██               [Ver perfil]         │   │
│  │  8. Sandra Torres      $1,420  █                [Ver perfil]         │   │
│  │  9. Diego Fernández    $1,200  █                [Ver perfil]         │   │
│  │  10. Mónica Vázquez    $1,100  █                [Ver perfil]         │   │
│  │                                                                       │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Customers List View (Tab adicional)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  🏗️ BMC CRM  │  [Tablero]  [Analytics]  [👥 Clientes]  [Config]             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  👥 CLIENTES (127)                                        [+ Nuevo Cliente]  │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  🔍 Buscar...                    [Status ▼]  [Origen ▼]  [Tags ▼]    │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ NOMBRE          TELÉFONO      STATUS    COTIZ.  REVENUE    ÚLTIMA    │   │
│  ├──────────────────────────────────────────────────────────────────────┤   │
│  │ Juan Pérez      099 123 456   🟡 Lead      3    $6,780    Hoy 10:30  │   │
│  │ 📱 WA  🏷️ construcción, urgente                          [Ver]       │   │
│  ├──────────────────────────────────────────────────────────────────────┤   │
│  │ María García    098 765 432   🟢 Customer  5    $18,920   Ayer 14:20 │   │
│  │ 📱 WA  🏷️ vip, wholesale                                 [Ver]       │   │
│  ├──────────────────────────────────────────────────────────────────────┤   │
│  │ Pedro López     097 111 222   🟢 Customer  8    $45,200   12/12 09:15│   │
│  │ 🛒 ML  🏷️ vip, recurrente                                [Ver]       │   │
│  ├──────────────────────────────────────────────────────────────────────┤   │
│  │ Carlos Sosa     099 888 999   🔵 Prospect 4    $12,450   13/12 18:00 │   │
│  │ 📱 WA  🏷️ hot-lead                                       [Ver]       │   │
│  ├──────────────────────────────────────────────────────────────────────┤   │
│  │ Ana Rodríguez   095 444 555   🟡 Lead      1    $1,850    Hoy 12:15  │   │
│  │ 📱 WA  🏷️ construcción                                   [Ver]       │   │
│  ├──────────────────────────────────────────────────────────────────────┤   │
│  │ ...                                                                   │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
│  Mostrando 1-10 de 127 clientes              [< Anterior]  [Siguiente >]    │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Color Scheme & Styling

### Colors
- **Primary**: Blue #2563eb (acciones principales)
- **Success**: Green #10b981 (confirmados, conversiones)
- **Warning**: Yellow #f59e0b (pendientes)
- **Info**: Cyan #06b6d4 (enviados)
- **Danger**: Red #ef4444 (rechazados, alertas)
- **Background**: White #ffffff / Light gray #f9fafb
- **Text**: Dark gray #111827 / Medium gray #6b7280

### Status Colors
- 🟡 **Lead** (Yellow) - Primer contacto
- 🔵 **Prospect** (Blue) - Interacción múltiple
- 🟢 **Customer** (Green) - Ha comprado
- ⚫ **Inactive** (Gray) - Sin actividad 6+ meses

### Typography
- **Headers**: Bold, 18-24px
- **Body**: Regular, 14-16px
- **Small**: 12-14px
- **Font**: System font stack (San Francisco, Segoe UI, etc.)

---

## Key Features

### 1. Kanban Board (Main View)
- ✅ Drag & drop entre columnas
- ✅ Filtros por origen, fecha, monto
- ✅ Búsqueda rápida
- ✅ Vista compacta de cards
- ✅ Acciones rápidas en cada card

### 2. Quote Detail View
- ✅ Información completa del cliente
- ✅ Items de cotización detallados
- ✅ Timeline de interacciones
- ✅ Notas con pin
- ✅ Acciones rápidas (enviar, confirmar, llamar)

### 3. Analytics Dashboard
- ✅ Widgets de métricas clave
- ✅ Gráficos de tendencias
- ✅ Distribución por origen/producto
- ✅ Top clientes
- ✅ Comparación períodos

### 4. Customer List
- ✅ Tabla sorteable y filtrable
- ✅ Búsqueda avanzada
- ✅ Vista rápida de estadísticas
- ✅ Tags visuales
- ✅ Exportar a CSV/Excel

### 5. Mobile Responsive
- ✅ Diseño adaptativo
- ✅ Touch gestures
- ✅ Menu hamburguesa
- ✅ Cards en lista vertical en mobile

---

## Interactions & Behaviors

### Drag & Drop
```
Usuario arrastra card "WA121412345" de PENDIENTES → ENVIADOS
→ Modal: "¿Marcar como enviado?"
   [Cancelar] [✓ Confirmar y Enviar Email]
→ Card se mueve
→ Status actualiza en DB
→ Se registra interacción
→ (Opcional) Se envía email
```

### Quick Actions
```
Usuario hace clic en [Enviar Cotización]
→ Modal con preview del email
→ Campo para ajustar email si es placeholder
→ [Cancelar] [📧 Enviar]
→ Email enviado
→ Quote movido a "Enviados"
→ Interacción registrada
```

### Search
```
Usuario escribe "099" en búsqueda
→ Filtro en tiempo real
→ Muestra todos los quotes con ese teléfono
→ Resalta matches
→ Puede filtrar más por status, origen
```

---

## Technical Notes

### Data Integration
- **MongoDB CRM** (primary) - Customers, interactions, notes, quotes
- **Google Sheets** (sync) - Legacy data, backup
- **Real-time updates** - WebSocket or polling for multi-user

### Performance
- **Lazy loading** - Cards cargan por demanda
- **Virtual scrolling** - Listas largas optimizadas
- **Caching** - Redux/Zustand para state
- **Pagination** - 20-50 items per page

### Stack Proposal
- **Framework**: Next.js 14 (ya en uso)
- **UI Library**: Tailwind CSS + Shadcn/ui
- **State**: React Query + Zustand
- **Drag & Drop**: @dnd-kit/core
- **Charts**: Recharts o Chart.js
- **Icons**: Lucide React

---

## Questions for You

Before I start building:

1. **Color preferences?** Do you like the blue/green/yellow scheme or prefer different colors?

2. **Priority features?** Start with:
   - Option A: Kanban board only (fastest)
   - Option B: Kanban + Analytics
   - Option C: Full dashboard (Kanban + Analytics + Customer List)

3. **Google Sheets sync?** Should the dashboard:
   - Read from MongoDB only (fast, new data)
   - Sync with Google Sheets bidirectionally (complex)
   - Display both but manage in MongoDB (hybrid)

4. **Mobile priority?** Desktop-first or mobile-first?

5. **User roles?** Single user or multi-user with permissions?

Let me know your preferences and I'll start building!
