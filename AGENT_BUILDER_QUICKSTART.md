# Agent Builder - Quick Start Guide

## Installation

No additional installation required! The Agent Builder uses only Python standard library modules.

## 1. First Time Setup (5 minutes)

### Start the Interactive CLI
```bash
python agent_builder_cli.py
```

### Create Your First Agent
1. Select option `1` (Create new agent)
2. Enter a name: `MyFirstAgent`
3. Choose type: `1` (Sales)
4. Enter capabilities: `sales, quotes, support`

✅ Your agent blueprint is created!

## 2. Your First Consultation (2 minutes)

### Consult with the Builder
1. Select option `4` (Consult with Builder)
2. Enter topic: `How do I set up my agent?`

You'll receive:
- ✅ Personalized recommendations
- ✅ Code examples
- ✅ Next steps
- ✅ Best practices

## 3. Create Development Tasks (3 minutes)

### Add Tasks
1. Select option `6` (Create task)
2. Title: `Set up agent configuration`
3. Priority: `3` (High)
4. Days until due: `3`
5. Estimated hours: `2`

### View Your Agenda
Select option `5` to see:
- 📅 Upcoming consultations
- 📝 Pending tasks
- 🎯 Milestones

## 4. Track Progress (1 minute)

### Check Your Progress
Select option `8` to see:
- Current development stage
- Completion percentage
- Task statistics
- Time estimates

## Progressive Learning

### Consultation Levels

As you consult more, you unlock deeper insights:

**Level 1 - Basic** (Consultation 1)
- Fundamental concepts
- Basic setup
- Simple examples

**Level 2 - Intermediate** (Consultations 2-4)
- Advanced features
- Integration patterns
- Context management

**Level 3 - Advanced** (Consultations 5-8)
- Complex workflows
- Performance optimization
- External integrations

**Level 4 - Expert** (Consultation 9+)
- Architecture patterns
- Multi-agent systems
- Production scaling

## Example Workflow

```
Day 1: Create agent + Basic consultation
↓
Day 2: Create tasks + Schedule next consultation
↓
Day 4: Intermediate consultation + Update tasks
↓
Day 7: Advanced consultation + Check milestone
↓
Day 14: Expert consultation + Production ready!
```

## Key Commands

| Option | What It Does |
|--------|--------------|
| 1 | Create new agent blueprint |
| 2 | List all your agents |
| 3 | Select agent to work with |
| 4 | Get consultation (progresses automatically) |
| 5 | View agenda and tasks |
| 6 | Create development task |
| 7 | Schedule consultation |
| 8 | View progress metrics |
| 9 | Generate detailed report |

## Tips for Success

### 🎯 Be Consistent
- Consult regularly (every 2-3 days)
- Complete tasks between consultations
- Track your progress weekly

### 💡 Be Specific
- Ask focused questions
- Include context in topics
- Follow suggested next steps

### 📊 Be Organized
- Create tasks after each consultation
- Set realistic due dates
- Update task status regularly

### 🚀 Be Progressive
- Don't skip consultation levels
- Implement recommendations before advancing
- Test incrementally

## Real Example

```bash
$ python agent_builder_cli.py

# Create agent
> Option: 1
> Name: BMC Sales Bot
> Type: 1 (Sales)
> Capabilities: quotes, products, sales

# First consultation
> Option: 4
> Topic: How to handle customer quotes

📋 RECOMMENDATIONS (4):
1. Define core purpose of sales agent
2. Identify main capabilities
3. Establish basic workflows
4. Set up agent configuration

# Create task from recommendation
> Option: 6
> Title: Set up sales agent config
> Priority: 3 (High)
> Days: 2
> Hours: 1.5

# Check progress
> Option: 8

📊 PROGRESS:
   Stage: planning
   Completion: 25%
   Consultations: 1
   Tasks: 1 (Pending: 1)
```

## Next Steps

After your first session:

1. ✅ Review the recommendations
2. ✅ Implement suggested changes
3. ✅ Complete at least one task
4. ✅ Schedule next consultation
5. ✅ Consult again to level up!

## Get Help

- 📚 Full documentation: `AGENT_BUILDER_GUIDE.md`
- 🧪 Run tests: `python test_agent_builder.py`
- 💻 See examples: `python agent_builder_example.py`
- 📖 Check README: Section "Agent Builder"

## Programmatic Usage

If you prefer code over CLI:

```python
from agent_builder import get_agent_builder, AgentType

# Get builder
builder = get_agent_builder()

# Create agent
agent = builder.create_agent_blueprint(
    agent_name="MyAgent",
    agent_type=AgentType.SALES
)

# Consult
consultation = builder.consult(
    agent.agent_id,
    "How do I implement routing?"
)

# View recommendations
for rec in consultation.recommendations:
    print(f"• {rec}")
```

---

**Ready to start?** Run: `python agent_builder_cli.py`

**Questions?** Check: `AGENT_BUILDER_GUIDE.md`

**Examples?** Run: `python agent_builder_example.py`
