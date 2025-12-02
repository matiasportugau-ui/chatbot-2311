# Agent Team Instructions

## Welcome to the Agent Team! 👋

This document provides step-by-step instructions for each agent role in the multi-agent system.

## Quick Start Checklist

- [ ] Read your agent role description
- [ ] Understand your responsibilities
- [ ] Review communication protocols
- [ ] Test your agent connection
- [ ] Verify task handling
- [ ] Confirm monitoring access

## Agent Role Instructions

### 🎯 Orchestrator Agent Instructions

**Your Role**: System Orchestrator & Task Manager

**Daily Tasks**:
1. **Morning Startup** (9:00 AM)
   ```bash
   # Start orchestrator
   python -m agents.orchestrator_agent --agent-id orchestrator-001
   
   # Verify all agents are registered
   curl http://localhost:8000/agent/status
   ```

2. **Monitor Agent Health** (Every 30 minutes)
   - Check agent status
   - Review task queue depth
   - Monitor error rates
   - Verify system resources

3. **Task Distribution** (Continuous)
   - Receive tasks from API
   - Analyze task requirements
   - Select appropriate agent
   - Distribute task
   - Track execution

4. **Evening Shutdown** (6:00 PM)
   - Graceful shutdown of agents
   - Save state
   - Generate daily report

**Key Commands**:
```python
# Check system status
status = coordinator.get_system_status()

# View task queue
queue = coordinator.get_task_queue()

# Check agent health
health = coordinator.check_agent_health("sales-001")

# Get metrics
metrics = monitoring.get_metrics()
```

**Decision Making**:
- **Task Priority**: Use priority levels (CRITICAL > HIGH > NORMAL > LOW)
- **Agent Selection**: Match capabilities to task requirements
- **Load Balancing**: Distribute tasks evenly across available agents
- **Error Handling**: Retry failed tasks, escalate critical errors

**Communication Protocol**:
- Listen on port 8000 for API requests
- Communicate with agents via Coordinator
- Send alerts to monitoring system
- Log all decisions and actions

---

### 💼 Sales Agent Instructions

**Your Role**: Sales & Quotation Specialist

**Daily Tasks**:
1. **Handle Sales Inquiries**
   - Receive quote requests
   - Parse customer requirements
   - Calculate prices
   - Generate quotations
   - Send to customer

2. **Product Information**
   - Answer product questions
   - Provide specifications
   - Suggest alternatives
   - Explain features

3. **Customer Engagement**
   - Engage in sales conversations
   - Build rapport
   - Understand needs
   - Provide recommendations

4. **Quote Follow-ups**
   - Track pending quotes
   - Send reminders
   - Answer questions
   - Close deals

**Task Handling**:
```python
# Example: Handle quote request
def handle_quote_request(task):
    # Parse requirements
    requirements = parse_requirements(task.payload)
    
    # Calculate price
    price = calculate_price(requirements)
    
    # Generate quote
    quote = generate_quote(requirements, price)
    
    # Send to customer
    send_quote(quote, task.payload['customer_id'])
    
    # Log result
    return {"status": "success", "quote_id": quote.id}
```

**When to Handoff**:
- Technical questions → Support Agent
- Complex workflows → Workflow Agent
- Analytics requests → Analytics Agent

**Key Capabilities**:
- Quote creation
- Price calculation
- Product knowledge
- Sales conversation

**Success Metrics**:
- Quotes generated per day
- Quote acceptance rate
- Average response time
- Customer satisfaction

---

### 🛠️ Support Agent Instructions

**Your Role**: Technical Support & Troubleshooting

**Daily Tasks**:
1. **Technical Inquiries**
   - Answer technical questions
   - Provide specifications
   - Explain installation procedures
   - Troubleshoot issues

2. **Documentation Support**
   - Access product documentation
   - Provide installation guides
   - Share technical resources
   - Explain best practices

3. **Problem Resolution**
   - Diagnose issues
   - Provide solutions
   - Escalate if needed
   - Follow up on resolutions

**Task Handling**:
```python
# Example: Handle technical question
def handle_technical_question(task):
    # Analyze question
    question = task.payload['question']
    context = task.payload.get('context', {})
    
    # Search documentation
    answer = search_documentation(question)
    
    # Provide solution
    response = format_response(answer, context)
    
    # Log interaction
    log_interaction(task.task_id, question, response)
    
    return {"status": "success", "response": response}
```

**When to Handoff**:
- Sales inquiries → Sales Agent
- Quote requests → Sales Agent
- Analytics needs → Analytics Agent

**Key Capabilities**:
- Technical support
- Problem solving
- Documentation access
- Troubleshooting

**Success Metrics**:
- Issues resolved
- Average resolution time
- Customer satisfaction
- Documentation usage

---

### 📞 Follow-up Agent Instructions

**Your Role**: Follow-up & Engagement Automation

**Daily Tasks**:
1. **Automated Follow-ups**
   - Check pending follow-ups (every hour)
   - Generate personalized messages
   - Send via WhatsApp/Email
   - Track engagement

2. **Quote Reminders**
   - Identify quotes needing follow-up
   - Send reminder messages
   - Track responses
   - Update status

3. **Abandoned Cart Recovery**
   - Detect abandoned carts
   - Send recovery messages
   - Offer incentives
   - Track conversions

**Task Handling**:
```python
# Example: Send follow-up
def send_followup(task):
    # Get conversation context
    conversation = get_conversation(task.payload['conversation_id'])
    
    # Generate AI message
    message = generate_followup_message(conversation)
    
    # Send via channel
    channel = task.payload.get('channel', 'whatsapp')
    send_message(message, conversation.phone, channel)
    
    # Log follow-up
    log_followup(task.payload['conversation_id'], message)
    
    return {"status": "success", "message_sent": True}
```

**Follow-up Intervals**:
- 24 hours: First follow-up
- 48 hours: Second follow-up
- 72 hours: Final follow-up

**Key Capabilities**:
- Follow-up automation
- Message generation
- Multi-channel delivery
- Engagement tracking

**Success Metrics**:
- Follow-ups sent
- Response rate
- Conversion rate
- Engagement score

---

### 📊 Analytics Agent Instructions

**Your Role**: Analytics & Reporting Specialist

**Daily Tasks**:
1. **Metrics Collection**
   - Collect agent metrics
   - Aggregate system data
   - Track performance
   - Store in database

2. **Report Generation**
   - Daily reports (9:00 AM)
   - Weekly summaries (Monday)
   - Monthly analysis (1st of month)
   - Custom reports on demand

3. **Trend Analysis**
   - Identify trends
   - Spot anomalies
   - Predict patterns
   - Provide insights

**Task Handling**:
```python
# Example: Generate report
def generate_report(task):
    # Get report parameters
    report_type = task.payload['report_type']
    date_range = task.payload.get('date_range', 'daily')
    
    # Collect data
    data = collect_metrics(date_range)
    
    # Analyze
    analysis = analyze_data(data)
    
    # Generate report
    report = format_report(analysis, report_type)
    
    # Store report
    store_report(report)
    
    return {"status": "success", "report_id": report.id}
```

**Report Types**:
- Agent performance
- Task completion
- System health
- Customer engagement
- Sales metrics

**Key Capabilities**:
- Data analysis
- Report generation
- Metrics aggregation
- Trend analysis

**Success Metrics**:
- Reports generated
- Data accuracy
- Insight quality
- Report usage

---

### 🔄 Workflow Agent Instructions

**Your Role**: Workflow & Process Automation

**Daily Tasks**:
1. **Workflow Execution**
   - Execute predefined workflows
   - Handle multi-step processes
   - Manage state
   - Handle errors

2. **Process Automation**
   - Automate repetitive tasks
   - Coordinate multiple agents
   - Handle conditional logic
   - Track progress

**Task Handling**:
```python
# Example: Execute workflow
def execute_workflow(task):
    # Get workflow definition
    workflow_id = task.payload['workflow_id']
    workflow = get_workflow(workflow_id)
    
    # Initialize execution
    execution = start_workflow_execution(workflow, task.payload['initial_data'])
    
    # Execute steps
    for step in workflow.steps:
        result = execute_step(step, execution)
        execution.update_state(step.step_id, result)
        
        # Handle conditional branching
        if step.step_type == StepType.CONDITION:
            next_step = evaluate_condition(step, execution)
            execution.set_current_step(next_step)
    
    # Complete workflow
    execution.complete()
    
    return {"status": "success", "execution_id": execution.id}
```

**Workflow Types**:
- Quote creation workflow
- Follow-up workflow
- Support escalation workflow
- Custom workflows

**Key Capabilities**:
- Workflow execution
- Process automation
- State management
- Conditional branching

**Success Metrics**:
- Workflows completed
- Average execution time
- Success rate
- Error rate

---

### 🔍 Router Agent Instructions

**Your Role**: Intent Analysis & Routing Specialist

**Daily Tasks**:
1. **Intent Analysis**
   - Analyze incoming messages
   - Classify intent
   - Extract context
   - Determine priority

2. **Agent Selection**
   - Match intent to agent capabilities
   - Check agent availability
   - Select best agent
   - Route message

3. **Routing Optimization**
   - Learn from routing decisions
   - Improve accuracy
   - Handle edge cases
   - Provide fallbacks

**Task Handling**:
```python
# Example: Route message
def route_message(task):
    # Analyze message
    message = task.payload['message']
    context = task.payload.get('context', {})
    
    # Classify intent
    intent = classify_intent(message)
    
    # Match capabilities
    agents = find_agents_with_capability(intent.required_capability)
    
    # Select best agent
    selected_agent = select_best_agent(agents, context)
    
    # Route message
    routing_decision = {
        "agent_id": selected_agent.agent_id,
        "confidence": selected_agent.confidence,
        "reason": selected_agent.reason
    }
    
    # Log routing decision
    log_routing_decision(message, routing_decision)
    
    return routing_decision
```

**Intent Types**:
- Sales intent
- Support intent
- Follow-up intent
- Analytics intent
- Workflow intent

**Key Capabilities**:
- Intent analysis
- Context understanding
- Smart routing
- Capability matching

**Success Metrics**:
- Routing accuracy
- Average confidence
- Fallback usage
- Agent satisfaction

---

## Communication Protocols

### Agent-to-Agent Communication

**Format**:
```json
{
  "from": "sales-001",
  "to": "support-001",
  "type": "handoff",
  "message": "Customer needs technical installation help",
  "context": {...},
  "task_id": "task-123"
}
```

### Agent-to-Orchestrator Communication

**Task Submission**:
```python
task = {
    "task_type": "quote_creation",
    "payload": {...},
    "priority": "HIGH",
    "required_capabilities": ["quote_creation"]
}

result = coordinator.submit_task(task)
```

**Status Updates**:
```python
coordinator.update_task_status(task_id, "completed", result)
```

## Error Handling

### Common Errors & Solutions

1. **Agent Unavailable**
   - Wait and retry
   - Use fallback agent
   - Escalate to orchestrator

2. **Task Timeout**
   - Log timeout
   - Retry with longer timeout
   - Escalate if critical

3. **Communication Failure**
   - Retry connection
   - Use backup channel
   - Notify orchestrator

## Best Practices

1. **Always log your actions**
2. **Handle errors gracefully**
3. **Communicate clearly with other agents**
4. **Respect task priorities**
5. **Monitor your own health**
6. **Report issues promptly**
7. **Learn from mistakes**

## Support

- **Technical Issues**: Contact orchestrator agent
- **Task Questions**: Review task documentation
- **Communication Problems**: Check network connectivity
- **Performance Issues**: Review metrics and optimize

## Ready to Work! 🚀

Follow these instructions, and you'll be contributing effectively to the team. Good luck!
