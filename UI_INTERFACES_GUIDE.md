# Chatbot UI Interfaces Guide

This document describes how the chat interface and dashboard look and work.

---

## 📱 Chat Interface Layout

### 1. **Standalone HTML Chat Interface** (`chat-interface.html`)

A mobile-friendly chat widget styled like WhatsApp/iMessage.

#### **Visual Layout:**

```
┌─────────────────────────────────────┐
│  [S] Chat with Superchapita  [●] [⋯] [×] │ ← Header (Blue background)
├─────────────────────────────────────┤
│                                     │
│  [S] ¡Hola! Soy Superchapita...     │ ← Welcome message
│                                     │
│  [S] Bot message here...            │ ← Bot messages (left, gray)
│                                     │
│                    User message... [U] │ ← User messages (right, blue)
│                                     │
│  [S] Another bot response...        │
│                                     │
│  [Quick Action] [Quick Action]     │ ← Quick action buttons
│                                     │
├─────────────────────────────────────┤
│  [🎤] Type message...        [✈]   │ ← Input area
└─────────────────────────────────────┘
```

#### **Key Features:**

1. **Header Section:**
   - Profile icon with "S" (Superchapita)
   - Title: "Chat with Superchapita"
   - Connection status indicator (green/red dot)
   - Menu button (⋯) for settings
   - Close button (×)

2. **Messages Area:**
   - **Bot messages:** Left-aligned, gray background (#e5e5ea)
   - **User messages:** Right-aligned, blue background (#007aff)
   - Timestamps below each message
   - Profile icons (S for bot, U for user)
   - Auto-scrolls to latest message

3. **Quick Action Buttons:**
   - Appear below bot messages
   - Light blue buttons (#BBDEFB)
   - Click to send pre-defined responses

4. **Input Area:**
   - Microphone icon (🎤)
   - Text input with placeholder
   - Send button (✈) - orange (#FF6B35)
   - Disabled state when loading

5. **Settings Panel:**
   - Opens from menu button
   - Configure API URL
   - Set default phone number
   - Save/Cancel buttons

6. **Loading Indicator:**
   - Three animated dots
   - Shows when bot is thinking

7. **Error Handling:**
   - Red error messages
   - Retry button on failed requests
   - Connection status updates

#### **Color Scheme:**
- **Primary Blue:** #2196F3 (BMC brand)
- **User Message Blue:** #007aff
- **Send Button Orange:** #FF6B35
- **Background:** #f0f2f5 (light gray)
- **Chat Container:** White with shadow

#### **Responsive Design:**
- Desktop: 400px wide, 600px tall
- Mobile: Full screen, border-radius removed

---

### 2. **React Chat Interface** (`bmc-chat-interface.tsx`)

A more advanced React component with additional features.

#### **Visual Layout:**

```
┌─────────────────────────────────────────────────┐
│ 💬 Chat BMC - +59891234567  [Comprimir] [Nuevo] │ ← Header
├─────────────────────────────────────────────────┤
│                                                 │
│  👋 ¡Hola! Soy el asistente de BMC...          │
│                                                 │
│  [Cotización]                                   │
│  ┌─────────────────────────────────────────┐   │
│  │ 💰 Cotización Generada                  │   │
│  │ Producto: Isodec 100mm                   │   │
│  │ Precio Base: $1,200                      │   │
│  │ Total: $60,000                           │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  🏗️ Productos Sugeridos                         │
│  ┌─────────────────────────────────────────┐   │
│  │ Isoroof - $1,500/m²                     │   │
│  │ Isopanel - $1,800/m²                    │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
├─────────────────────────────────────────────────┤
│ Contexto: 2,500/8,000 tokens [████░░░░] 50%    │ ← Context bar
│ [Type message...]                    [Send]     │ ← Input
└─────────────────────────────────────────────────┘
```

#### **Key Features:**

1. **Message Types:**
   - **User messages:** Right-aligned, primary color
   - **Assistant messages:** Left-aligned, muted background
   - **System messages:** Italic, secondary color

2. **Rich Message Content:**
   - **Quotation cards:** Green background, shows product details
   - **Product suggestions:** Blue cards with pricing
   - **FAQ suggestions:** Purple cards
   - **Metadata badges:** Show message type (cotización, información, etc.)

3. **Context Management:**
   - Progress bar showing token usage
   - Color-coded: Green (<50%), Yellow (50-80%), Red (>80%)
   - "Comprimir" button to reduce context

4. **Actions:**
   - **Nuevo Chat:** Start fresh conversation
   - **Comprimir:** Compress context when >50% used

5. **Loading State:**
   - Spinning refresh icon
   - "Procesando tu consulta..." message

---

## 🎛️ Dashboard Interface Layout

### **Main Dashboard** (`main-dashboard.tsx`)

A comprehensive admin dashboard with multiple views.

#### **Overall Layout:**

```
┌─────────────────────────────────────────────────────────────┐
│  [Header: Logo, User, Notifications]                         │ ← Top Header
├──────────┬──────────────────────────────────────────────────┤
│          │  [Overview] [Analytics] [Performance] [Health]  │ ← Tab Navigation
│          │  [Context] [Chat] [Sistema] [Mercado Libre]...  │
│ Sidebar  ├──────────────────────────────────────────────────┤
│          │                                                  │
│ [Menu]   │  ┌────────────────────────────────────────────┐ │
│          │  │  Overview Dashboard                        │ │
│ - Overview│  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐    │ │
│ - Analytics│ │  │ 1234 │ │ 89   │ │ $2.5K│ │ 68%  │    │ │
│ - Performance││  │Quotes│ │Month │ │Avg   │ │Conv  │    │ │
│ - Health  │  │  └──────┘ └──────┘ └──────┘ └──────┘    │ │
│ - Context │  │  [Charts and Metrics]                     │ │
│ - Chat    │  └────────────────────────────────────────────┘ │
│ - ...     │                                                  │
│          │                                                  │
│          │  [More dashboard content...]                    │
│          │                                                  │
├──────────┴──────────────────────────────────────────────────┤
│  [Footer: Links, Copyright]                                 │
└─────────────────────────────────────────────────────────────┘
```

#### **Dashboard Sections:**

1. **Header Component:**
   - Logo/Branding
   - User menu
   - Notifications bell
   - Search bar
   - Theme toggle (light/dark)

2. **Sidebar Navigation:**
   - Collapsible sidebar
   - Menu items with icons
   - Active state highlighting
   - Grouped sections

3. **Tab Navigation:**
   - Horizontal tab bar
   - Icons + labels
   - Active tab highlighted
   - Scrollable if many tabs

4. **Main Content Area:**
   - Tab-based content switching
   - Cards and widgets
   - Charts and graphs
   - Data tables

#### **Available Dashboard Tabs:**

1. **Overview** - Main dashboard with KPIs
2. **Analytics** - Quote analytics and charts
3. **Performance** - System performance metrics
4. **System Health** - Health checks and status
5. **Context Management** - Conversation context
6. **Live Chat** - Embedded chat interface
7. **Sistema Integrado** - Integrated system metrics
8. **Mercado Libre** - ML listings and orders
9. **Google Sheets** - Sheets integration dashboard
10. **Trends** - Trend analysis
11. **Feedback** - User feedback management
12. **AI Insights** - AI-generated insights
13. **Monitoring** - Real-time monitoring
14. **Improvements** - Improvement suggestions
15. **Export/Import** - Data export/import
16. **Notifications** - Notification center
17. **Search** - Search and filters
18. **Help** - Help and support
19. **Settings** - System settings

---

## 🎨 Design System

### **Colors:**

**Primary:**
- Blue: #2196F3 (BMC brand)
- Orange: #FF6B35 (Actions)

**Message Colors:**
- Bot: #e5e5ea (light gray)
- User: #007aff (blue)
- System: Secondary color

**Status Colors:**
- Success: Green (#4caf50)
- Error: Red (#f44336)
- Warning: Yellow/Orange
- Info: Blue

### **Typography:**
- **Headers:** 'Trirong' serif font (BMC brand)
- **Body:** 'Red Hat Display' sans-serif
- **Sizes:** Responsive, scales with screen size

### **Components:**

1. **Cards:**
   - White background
   - Border radius: 8px
   - Shadow: 0 4px 12px rgba(0,0,0,0.1)

2. **Buttons:**
   - Primary: Blue background, white text
   - Secondary: Gray outline
   - Icon buttons: Circular, 40px

3. **Inputs:**
   - Rounded: 20px border-radius
   - Border: 1px solid #ccc
   - Focus: Blue outline

4. **Badges:**
   - Small, rounded
   - Colored backgrounds
   - Used for status, types

---

## 🔄 User Flow

### **Chat Flow:**

1. **User opens chat**
   - Welcome message appears
   - Connection status checked
   - Session ID created

2. **User types message**
   - Input enabled
   - Send button active

3. **Message sent**
   - User message appears (right, blue)
   - Loading indicator shows
   - Send button disabled

4. **Bot responds**
   - Loading indicator removed
   - Bot message appears (left, gray)
   - Quick actions shown (if available)
   - Context updated

5. **Error handling**
   - Error message displayed
   - Retry button shown
   - Connection status updated

### **Dashboard Flow:**

1. **User logs in**
   - Redirected to Overview
   - Sidebar expanded
   - Default tab: Overview

2. **Navigation**
   - Click tab to switch views
   - Sidebar for quick navigation
   - Breadcrumbs for deep navigation

3. **Data interaction**
   - Charts update in real-time
   - Filters apply instantly
   - Export/import available

4. **Settings**
   - Settings tab for configuration
   - Changes save automatically
   - Notifications for updates

---

## 📱 Responsive Behavior

### **Mobile (< 480px):**
- Chat: Full screen
- Dashboard: Stacked layout
- Sidebar: Collapsible/hidden
- Tabs: Scrollable horizontal

### **Tablet (480px - 1024px):**
- Chat: 400px width
- Dashboard: 2-column layout
- Sidebar: Collapsible

### **Desktop (> 1024px):**
- Chat: 400px centered
- Dashboard: Full layout
- Sidebar: Always visible
- Multi-column grids

---

## ♿ Accessibility Features

1. **ARIA Labels:**
   - All buttons have aria-labels
   - Messages have role="log"
   - Status updates use aria-live

2. **Keyboard Navigation:**
   - Tab through all elements
   - Enter to send messages
   - Escape to close modals

3. **Screen Reader Support:**
   - Semantic HTML
   - Alt text for icons
   - Status announcements

4. **Focus Management:**
   - Visible focus indicators
   - Focus trap in modals
   - Auto-focus on input

---

## 🎯 Key Interactions

### **Chat:**
- **Send:** Click send button or press Enter
- **Quick Actions:** Click button to send
- **Settings:** Click menu (⋯) button
- **Retry:** Click retry button on errors
- **New Chat:** Click "Nuevo Chat" button

### **Dashboard:**
- **Switch Tabs:** Click tab button
- **Toggle Sidebar:** Click sidebar toggle
- **Filter Data:** Use search/filter components
- **Export Data:** Click export button
- **View Details:** Click on cards/charts

---

## 🚀 Performance Features

1. **Message History:**
   - Stored in localStorage
   - Persists across sessions
   - Auto-cleanup after 100 messages

2. **Connection Monitoring:**
   - Health check every 30 seconds
   - Visual status indicator
   - Auto-retry on failure

3. **Context Management:**
   - Token usage tracking
   - Auto-compression when needed
   - Progress visualization

4. **Lazy Loading:**
   - Components load on demand
   - Images lazy-loaded
   - Code splitting for routes

---

This guide provides a complete overview of how the chat and dashboard interfaces look and function. The design is modern, accessible, and optimized for both desktop and mobile use.

