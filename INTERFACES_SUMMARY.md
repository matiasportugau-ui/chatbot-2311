# Project Interfaces Summary

This document provides a comprehensive overview of all interfaces, models, and API endpoints in the BMC Chatbot project.

## Table of Contents
1. [Python Interfaces](#python-interfaces)
2. [API Request/Response Models](#api-requestresponse-models)
3. [Data Models (Dataclasses)](#data-models-dataclasses)
4. [FastAPI Endpoints](#fastapi-endpoints)
5. [Next.js API Routes](#nextjs-api-routes)
6. [React Components (UI Interfaces)](#react-components-ui-interfaces)
7. [TypeScript Type Definitions](#typescript-type-definitions)

---

## Python Interfaces

### Agent Interface System
**Location:** `scripts/orchestrator/agent_interface.py`

#### `AgentInterface` (Abstract Base Class)
Base interface for all agents in the system.

**Methods:**
- `execute_task(task_id: str, task_config: Dict[str, Any]) -> Dict[str, Any]` (abstract)
- `create_task_request(task_id: str, task_config: Dict[str, Any]) -> str`
- `save_task_result(task_id: str, result: Dict[str, Any]) -> str`
- `load_task_request(task_id: str) -> Optional[Dict[str, Any]]`

**Properties:**
- `agent_name: str`
- `agent_type: str`
- `task_dir: Path`

#### Concrete Agent Implementations:

1. **`RepositoryAgent`** - Handles repository and workspace analysis
   - `execute_task()` - Executes repository/workspace analysis tasks
   - `_analyze_repositories()` - Analyzes repository structure
   - `_analyze_workspace()` - Analyzes workspace structure

2. **`IntegrationAgent`** - Handles integration validation
   - `execute_task()` - Executes integration validation tasks
   - `_validate_integrations()` - Validates integrations

3. **`QuotationAgent`** - Handles BMC quotation engine tasks
   - `execute_task()` - Executes quotation engine tasks
   - `_inventory_bmc_components()` - Inventories BMC components
   - `_assess_quotation_engine()` - Assesses quotation engine

4. **`PlanningAgent`** - Analyzes PRs and generates implementation plans
   - `execute_task()` - Executes planning tasks
   - `analyze_pr()` - Analyzes pull requests
   - `analyze_local_changes()` - Analyzes local changes

#### `AgentCoordinator`
Coordinates communication between agents.

**Methods:**
- `delegate_task(agent_type: str, task_id: str, task_config: Dict[str, Any]) -> str`
- `execute_delegated_task(task_id: str, agent_type: str) -> Dict[str, Any]`
- `get_task_result(task_id: str) -> Optional[Dict[str, Any]]`
- `wait_for_task(task_id: str, timeout: int = 300) -> Optional[Dict[str, Any]]`

---

## API Request/Response Models

**Location:** `api_server.py`

### Request Models (Pydantic BaseModel)

#### `ChatRequest`
Request model for chat message processing.

**Fields:**
- `mensaje: str` - Message from the client (required)
- `telefono: str` - Client phone number (required)
- `sesionId: str | None` - Session ID (optional)

#### `QuoteRequest`
Request model for creating quotations.

**Fields:**
- `cliente: dict[str, Any]` - Client information (required)
- `especificaciones: dict[str, Any]` - Quotation specifications (required)
- `asignado_a: str | None` - Assigned to (default: "MA")
- `observaciones: str | None` - Observations (default: "")

### Response Models (Pydantic BaseModel)

#### `ChatResponse`
Response model for chat messages.

**Fields:**
- `mensaje: str` - Response message
- `tipo: str` - Response type
- `acciones: list[str]` - Actions to take
- `confianza: float` - Confidence score
- `necesita_datos: list[str]` - Required data fields
- `sesion_id: str` - Session ID
- `timestamp: str` - Timestamp

#### `QuoteResponse`
Response model for quotations.

**Fields:**
- `id: str` - Quotation ID
- `cliente: dict[str, Any]` - Client information
- `producto: str` - Product name
- `precio_total: float` - Total price
- `precio_m2: float` - Price per square meter
- `estado: str` - Status
- `fecha: str` - Date

---

## Data Models (Dataclasses)

**Location:** `sistema_cotizaciones.py`

### `Cliente`
Client data structure.

**Fields:**
- `nombre: str` - Name
- `telefono: str` - Phone
- `direccion: str` - Address
- `zona: str` - Zone (default: "")
- `email: str` - Email (default: "")

### `Producto`
Product data structure.

**Fields:**
- `codigo: str` - Product code
- `nombre: str` - Product name
- `espesor: str` - Thickness
- `relleno: str` - Filling
- `color: str` - Color
- `precio_base: Decimal` - Base price
- `link_web: str` - Web link (default: "")
- `terminaciones_disponibles: list[str]` - Available finishes (default: None)
- `anclajes_incluidos: bool` - Anchors included (default: False)
- `traslado_incluido: bool` - Transport included (default: False)

### `EspecificacionCotizacion`
Quotation specification structure.

**Fields:**
- `producto: str` - Product
- `espesor: str` - Thickness
- `relleno: str` - Filling
- `largo_metros: Decimal` - Length in meters
- `ancho_metros: Decimal` - Width in meters
- `color: str` - Color
- `termina_front: str` - Front finish (default: "")
- `termina_sup: str` - Top finish (default: "")
- `termina_lat_1: str` - Side 1 finish (default: "")
- `termina_lat_2: str` - Side 2 finish (default: "")
- `anclajes: str` - Anchors (default: "")
- `traslado: str` - Transport (default: "")
- `direccion: str` - Address (default: "")
- `forma: str` - Shape (default: "")
- `origen: str` - Origin (default: "")

### `Cotizacion`
Complete quotation structure.

**Fields:**
- `id: str` - Quotation ID
- `cliente: Cliente` - Client
- `especificaciones: EspecificacionCotizacion` - Specifications
- `fecha: datetime.datetime` - Date
- `estado: str` - Status
- `asignado_a: str` - Assigned to
- `precio_total: Decimal` - Total price (default: 0)
- `precio_metro_cuadrado: Decimal` - Price per m² (default: 0)
- `observaciones: str` - Observations (default: "")

---

## FastAPI Endpoints

**Location:** `api_server.py`

### Health & Monitoring

#### `GET /health` or `GET /api/health`
Health check endpoint with dependency checks.

**Rate Limit:** 30/minute

**Response:** Health status with MongoDB, Qdrant, and OpenAI status

#### `GET /api/debug/request/{request_id}`
Retrieve request details by ID for debugging.

**Rate Limit:** 20/minute

**Parameters:**
- `request_id: str` - Request ID or client request ID

#### `GET /api/monitoring/rate-limits`
Get current rate limit status for all providers.

**Rate Limit:** 10/minute

**Response:** Rate limit information for all providers

#### `GET /metrics`
Prometheus metrics endpoint.

**Response:** Prometheus metrics in text format

### Chat & Messaging

#### `POST /chat/process`
Process a chat message and return response.

**Rate Limit:** 10 requests per minute

**Request Body:** `ChatRequest`
**Response:** `ChatResponse`

### Quotations

#### `POST /quote/create`
Create a new quotation.

**Rate Limit:** 5 requests per minute

**Request Body:** `QuoteRequest`
**Response:** `QuoteResponse`

### Insights & Data

#### `GET /insights`
Get insights from the knowledge base.

**Response:** Insights data

#### `GET /conversations`
Get recent conversations from MongoDB.

**Rate Limit:** 20/minute

**Query Parameters:**
- `limit: int` - Number of conversations to return (default: 50)

**Response:** List of conversations

### Authentication

#### `GET /auth/login`
Login endpoint to obtain JWT token.

**Query Parameters:**
- `username: str` - Username
- `password: str` - Password

**Response:** JWT access token

---

## Next.js API Routes

**Location:** `src/app/api/`

### Chat Routes
- `POST /api/chat` - Process chat messages
- `POST /api/chat/stream` - Stream chat responses

### Quote Engine Routes
- `POST /api/quote-engine` - Quote engine processing
- `POST /api/integrated-quote` - Integrated quote processing
- `POST /api/parse-quote` - Parse quote data

### Context Management Routes
- `GET /api/context` - Get context
- `POST /api/context` - Update context
- `GET /api/context/shared` - Get shared context
- `POST /api/context/export` - Export context
- `POST /api/context/import` - Import context

### Backup & Recovery Routes
- `GET /api/backup` - List backups
- `POST /api/backup` - Create backup
- `GET /api/backup/[id]` - Get backup by ID
- `DELETE /api/backup/[id]` - Delete backup
- `POST /api/backup/autosave` - Auto-save backup
- `GET /api/backup/monitoring` - Backup monitoring
- `POST /api/recovery` - Recover from backup

### Google Sheets Integration Routes
- `POST /api/sheets/sync` - Sync with Google Sheets
- `POST /api/sheets/enhanced-sync` - Enhanced sync

### WhatsApp Integration Routes
- `POST /api/whatsapp/webhook` - WhatsApp webhook handler

### MongoDB Routes
- `POST /api/mongodb/validate` - Validate MongoDB connection

### Analytics Routes
- `GET /api/analytics/quotes` - Quote analytics
- `GET /api/trends` - Trend analysis

### Mercado Libre Integration Routes
- `GET /api/mercado-libre/auth/start` - Start authentication
- `GET /api/mercado-libre/auth/callback` - Auth callback
- `GET /api/mercado-libre/auth/token` - Get token
- `POST /api/mercado-libre/listings/[action]` - Listing actions
- `POST /api/mercado-libre/orders/[action]` - Order actions
- `POST /api/mercado-libre/webhook` - Webhook handler

### System Routes
- `GET /api/health` - Health check
- `GET /api/search` - Search functionality
- `GET /api/notifications` - Get notifications
- `POST /api/notifications` - Create notification
- `GET /api/settings` - Get settings
- `POST /api/settings` - Update settings
- `POST /api/export` - Export data
- `POST /api/import` - Import data

---

## React Components (UI Interfaces)

**Location:** `src/components/`

### Chat Components
- `chat/bmc-chat-interface.tsx` - BMC chat interface
- `chat/chat-interface.tsx` - Main chat interface
- `chat/chat-interface-evolved.tsx` - Evolved chat interface

### Dashboard Components
- `dashboard/main-dashboard.tsx` - Main dashboard
- `dashboard/overview.tsx` - Overview dashboard
- `dashboard/header.tsx` - Dashboard header
- `dashboard/sidebar.tsx` - Dashboard sidebar
- `dashboard/footer.tsx` - Dashboard footer

### Metrics & Analytics Components
- `dashboard/metrics-overview.tsx` - Metrics overview
- `dashboard/performance-metrics.tsx` - Performance metrics
- `dashboard/quote-analytics.tsx` - Quote analytics
- `dashboard/trend-analysis.tsx` - Trend analysis
- `dashboard/kpi-card.tsx` - KPI card component

### Chart Components
- `dashboard/charts/conversation-chart.tsx` - Conversation chart
- `dashboard/charts/hourly-chart.tsx` - Hourly chart
- `dashboard/charts/performance-chart.tsx` - Performance chart

### Management Components
- `dashboard/quotes-manager.tsx` - Quotes manager
- `dashboard/context-management.tsx` - Context management
- `dashboard/google-sheets-dashboard.tsx` - Google Sheets dashboard
- `dashboard/mercado-libre-listings.tsx` - Mercado Libre listings
- `dashboard/mercado-libre-orders.tsx` - Mercado Libre orders

### System Components
- `dashboard/system-health.tsx` - System health
- `dashboard/real-time-monitoring.tsx` - Real-time monitoring
- `dashboard/integrated-system-metrics.tsx` - Integrated system metrics
- `dashboard/ai-insights.tsx` - AI insights
- `dashboard/improvement-suggestions.tsx` - Improvement suggestions

### Utility Components
- `dashboard/export-import.tsx` - Export/import functionality
- `dashboard/notifications.tsx` - Notifications
- `dashboard/settings.tsx` - Settings
- `dashboard/search-filters.tsx` - Search filters
- `dashboard/user-feedback.tsx` - User feedback
- `dashboard/help-support.tsx` - Help and support

### UI Components (Base Components)
- `ui/button.tsx` - Button component
- `ui/card.tsx` - Card component
- `ui/input.tsx` - Input component
- `ui/badge.tsx` - Badge component
- `ui/table.tsx` - Table component
- `ui/tabs.tsx` - Tabs component
- `ui/progress.tsx` - Progress component
- `ui/separator.tsx` - Separator component

---

## TypeScript Type Definitions

**Location:** `src/types/`

### `api.ts`
API request/response type definitions

### `analytics.ts`
Analytics data type definitions

### `import-export.ts`
Import/export type definitions

### `notifications.ts`
Notification type definitions

### `recovery.ts`
Recovery type definitions

### `settings.ts`
Settings type definitions

### Mercado Libre Types
**Location:** `src/lib/mercado-libre/types.ts`
- Mercado Libre API types
- Listing types
- Order types
- Webhook types

---

## Web Interface

**Location:** `chat-interface.html`
- Standalone HTML chat interface
- Connects to FastAPI backend at `http://localhost:8000`
- WebSocket support for real-time messaging

---

## Summary

This project has a comprehensive interface architecture:

1. **Python Layer:**
   - Abstract base classes for agent system
   - Pydantic models for API validation
   - Dataclasses for business logic

2. **API Layer:**
   - FastAPI REST endpoints
   - Next.js API routes
   - WebSocket support

3. **Frontend Layer:**
   - React/Next.js components
   - TypeScript type definitions
   - Standalone HTML interface

4. **Integration Layer:**
   - WhatsApp webhooks
   - Google Sheets sync
   - Mercado Libre integration
   - MongoDB persistence

All interfaces follow consistent patterns and are well-documented for maintainability and extensibility.

