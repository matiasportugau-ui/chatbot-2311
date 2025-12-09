# Implementation Plan: Flexible Conversational Bot & CRM Integration

## Goal Description
Transform the current rigid, state-machine-based sales bot (`estado_cotizacion` loop) into a fluid, LLM-driven "Agentic" system. This system will use dynamic slot filling to gather information naturally and integrate directly with CRM tools (simulated or real) to manage leads, replacing the need for "robotic" questionnaires.

## User Review Required
> [!IMPORTANT]
> **Paradigm Shift:** We are moving from *Deterministic* logic (strict if/else states) to *Probabilistic* logic (LLM decides what to ask). This increases flexibility but requires robust "Guardrails" to ensure the bot effectively gathers required data.

## Proposed Changes

### 1. Architecture Refactor: From State Machine to Tools (`ia_conversacional_integrada.py`)
*   **Remove State Loops:** Delete the rigid `_manejar_cotizacion` state machine logic.
*   **Implement "Agentic" Loop**:
    *   Instead of hardcoded responses, the `procesar_mensaje` workflow will:
        1.  Receive user message.
        2.  LLM analyzes context + available *Tools*.
        3.  LLM decides to call a Tool (e.g., `update_lead_info`) OR respond to user.
        4.  If Tool is called, execute it and feed result back to LLM.
        5.  LLM generates final natural response.

### 2. Tool Definitions (`tools_crm.py` - [NEW])
*   Create a new module defining available actions for the LLM:
    *   `save_lead_info(phone, name, requirement)`: Upsert data to CRM.
    *   `calculate_quote(product, area, options)`: Dynamic calculator.
    *   `check_stock(product)`: Inventory check.
    *   `search_knowledge_base(query)`: RAG lookup (existing functionality wrapped as a tool).

### 3. Model Integrator Update (`model_integrator.py`)
*   Enhance `UnifiedModelIntegrator` to support **Function Calling** (or simulated JSON-based tool use for models that don't support native function calling).
*   Ensure `system_prompt` injection logic supports defining these tools.

### 4. System Prompt Overhaul (`ia_conversacional_integrada.py` & `prompts.py`)
*   Inject the **"Expert Sales Persona"**: Friendly, concise, proactive.
*   Add **"Chain of Thought"** instructions: "Analyze what info you have, what is missing, and ask *one* relevant question at a time."

## Verification Plan

### Automated Tests
*   **Conversation Simulation**: Create a test script `test_flexible_flow.py` that simulates a user providing data in random order (e.g., "I need a roof, 50m2" -> "My name is John") and verifies that:
    1.  The bot acknowledges the data.
    2.  The bot asks for the *missing* data (Phone number).
    3.  The bot eventually produces a quote without crashing.
*   **Tool Execution**: Unit tests for `tools_crm.py` to ensure they correctly process inputs.

### Manual Verification
*   **Chat Interface**: Use the existing `chat-interface.html` to have a free-form conversation.
    *   *Scenario 1*: Give all info in one massive paragraph. Bot should generate quote immediately.
    *   *Scenario 2*: Be vague ("I need insulation"). Bot should guide the user naturally.
    *   *Scenario 3*: Interrupt the flow ("Wait, is it fireproof?"). Bot should answer and then gently return to the sales process.
