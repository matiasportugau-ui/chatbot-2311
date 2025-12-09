# 📖 Usage Guide: Master BMC Ecosystem Analysis Prompt

**Purpose:** Instructions for using the `MASTER_BMC_ECOSYSTEM_ANALYSIS_PROMPT.md` with AI agents  
**Target Audience:** Developers, architects, AI agents analyzing the BMC ecosystem  
**Last Updated:** 2024-12-28

---

## 🎯 Quick Start

### For AI Agents (Claude, GPT-4, etc.)

1. **Copy the entire prompt** from `MASTER_BMC_ECOSYSTEM_ANALYSIS_PROMPT.md`
2. **Paste as system prompt** in your AI assistant
3. **Start the conversation** with: "Begin Phase 1: Reconnaissance & Repo Clustering"
4. **Follow the structured output format** provided in the prompt

### For Human Developers

1. **Read the master prompt** to understand the analysis framework
2. **Use the repository inventory** (`BMC_REPOSITORY_INVENTORY.md`) as reference
3. **Execute analysis phases** manually or via AI agent
4. **Review generated reports** in `.cursor/plans/` directory

---

## 📋 Step-by-Step Workflow

### Step 1: Initial Setup

**Action:** Provide the AI agent with:
- GitHub organization/user: `matiasportugau-ui`
- GitHub API token (if needed for private repos)
- Access to workspace files (if analyzing local code)

**Expected Output:** List of all repositories with Tier classification

### Step 2: Phase 1 - Reconnaissance

**Action:** Execute Task 1.1 and 1.2 from the prompt

**Expected Output:**
- Repository fingerprinting table
- Tech stack profile
- Tier classification (Tier 1/2/3)

**Time Estimate:** 30-60 minutes

### Step 3: Phase 2 - Component Mapping

**Action:** Execute Task 2.1, 2.2, and 2.3 using "Anchor" search strategy

**Expected Output:**
- Module inventory per repository
- Integration points identified
- Architecture patterns documented

**Time Estimate:** 1-2 hours per Tier 1 repository

### Step 4: Phase 3 - Logic Flow

**Action:** Execute Task 3.1 and 3.2 to trace data flows

**Expected Output:**
- Integration point diagrams
- Mermaid.js architecture diagrams
- Data flow visualizations

**Time Estimate:** 1-2 hours

### Step 5: Comparative Analysis

**Action:** Build comparison matrix and maturity rankings

**Expected Output:**
- Module comparison table
- Maturity scores (1-100) per module
- Tier classification (Exemplar/Mature/Developing/Needs Work)

**Time Estimate:** 2-3 hours

### Step 6: Evolution Recommendations

**Action:** Generate recommendations for each less-evolved module

**Expected Output:**
- Current state analysis
- Reference exemplar identification
- Detailed improvement suggestions
- Implementation guides

**Time Estimate:** 1-2 hours per module

### Step 7: Ecosystem Integration

**Action:** Propose cross-repository integration opportunities

**Expected Output:**
- Integration opportunity list
- Value propositions
- Implementation steps

**Time Estimate:** 1-2 hours

### Step 8: Report Generation

**Action:** Generate structured reports per repository

**Expected Output:**
- Executive summary
- Module maps
- Risk assessments
- Action plans

**Time Estimate:** 30 minutes per repository

---

## 🔧 Customization Options

### Focus Areas

You can customize the prompt to focus on specific areas:

**For Security Analysis:**
- Add emphasis to "Security Hardening" section
- Include OWASP Top 10 checks
- Focus on authentication/authorization patterns

**For Performance Optimization:**
- Add performance metrics collection
- Include load testing recommendations
- Focus on scalability improvements

**For Integration Focus:**
- Emphasize "Ecosystem Reach Expansion" section
- Add API standardization requirements
- Focus on microservices architecture

### Scope Limitation

To limit scope, modify the Tier classification:

**Quick Analysis (2-4 hours):**
- Only analyze Tier 1 repositories
- Skip Tier 3 repositories
- Focus on exemplar modules only

**Deep Analysis (1-2 days):**
- Analyze all Tier 1 and Tier 2 repositories
- Include Tier 3 if relevant
- Full comparative analysis

**Comprehensive Analysis (1 week):**
- Analyze all repositories
- Full ecosystem mapping
- Complete integration roadmap

---

## 📊 Output Management

### File Naming Convention

Generated reports should follow this naming:

```
BMC_ECOSYSTEM_ANALYSIS_[REPO_NAME].md
BMC_ECOSYSTEM_INTEGRATION_OPPORTUNITIES.md
BMC_ECOSYSTEM_EVOLUTION_ROADMAP.md
BMC_ECOSYSTEM_RISK_ASSESSMENT.md
```

### Directory Structure

```
.cursor/plans/
├── MASTER_BMC_ECOSYSTEM_ANALYSIS_PROMPT.md (this prompt)
├── BMC_REPOSITORY_INVENTORY.md (reference)
├── USAGE_GUIDE_MASTER_PROMPT.md (this file)
├── BMC_ECOSYSTEM_ANALYSIS_bmc-cotizacion-inteligente.md
├── BMC_ECOSYSTEM_ANALYSIS_Ultimate-CHATBOT.md
├── BMC_ECOSYSTEM_ANALYSIS_chatbot-2311.md
├── BMC_ECOSYSTEM_INTEGRATION_OPPORTUNITIES.md
└── BMC_ECOSYSTEM_EVOLUTION_ROADMAP.md
```

---

## 🎓 Best Practices

### For AI Agents

1. **Follow the structure** - Don't skip phases
2. **Provide file references** - Every recommendation needs concrete paths
3. **Use exemplar modules** - Reference Tier 1 modules when suggesting improvements
4. **Respect privacy** - Mark secrets as [REDACTED]
5. **Include export_seal** - All generated files need metadata

### For Human Reviewers

1. **Start with executive summary** - Get the big picture first
2. **Review exemplar modules** - Understand what "good" looks like
3. **Prioritize recommendations** - Focus on high-impact, low-effort improvements
4. **Validate file references** - Ensure suggested files actually exist
5. **Check integration opportunities** - Look for quick wins

---

## 🚨 Common Issues & Solutions

### Issue 1: Repository Access Denied

**Problem:** Cannot access private repositories

**Solution:**
- Provide GitHub API token with appropriate scopes
- Mark inaccessible repos as `#ZonaDesconocida`
- Focus on accessible repositories first

### Issue 2: Too Many Repositories

**Problem:** Analysis taking too long

**Solution:**
- Limit to Tier 1 repositories only
- Use "Anchor" search strategy to focus on specific modules
- Prioritize by business value

### Issue 3: Missing File References

**Problem:** Recommendations lack concrete file paths

**Solution:**
- Require AI agent to provide file paths for every recommendation
- Validate paths exist before accepting recommendations
- Use repository inventory as reference

### Issue 4: Vague Recommendations

**Problem:** Suggestions are too generic

**Solution:**
- Require step-by-step implementation guides
- Include code examples from exemplar modules
- Specify estimated effort and prerequisites

---

## 📈 Success Metrics

A successful analysis should produce:

✅ **Complete repository inventory** with Tier classification  
✅ **Module comparison matrix** with maturity scores  
✅ **At least 3 exemplar modules** identified (Tier 1)  
✅ **Evolution recommendations** for each less-evolved module  
✅ **Integration opportunities** with implementation steps  
✅ **Risk assessment** with prioritized action plan  
✅ **Architecture diagrams** (Mermaid.js) for data flows  

---

## 🔄 Iterative Improvement

### Version Control

- Track prompt versions using export_seal
- Document changes in prompt evolution
- Maintain backward compatibility

### Feedback Loop

1. **Execute analysis** using current prompt
2. **Review outputs** for quality and completeness
3. **Identify gaps** in analysis framework
4. **Update prompt** with improvements
5. **Re-execute** on subset to validate

### Continuous Refinement

- Add new analysis dimensions as needed
- Update repository inventory as repos evolve
- Incorporate lessons learned from previous analyses

---

## 📞 Support & Resources

### Reference Documents

- `MASTER_BMC_ECOSYSTEM_ANALYSIS_PROMPT.md` - Main prompt
- `BMC_REPOSITORY_INVENTORY.md` - Repository reference
- `BMC_ARCHITECT_PROMPT.md` - Production architect prompt
- `BMC_PRODUCTION_STATUS_ASSESSMENT.md` - Current status

### Key Contacts

- **Project:** Ultimate-CHATBOT
- **Organization:** BMC Uruguay
- **Language:** Spanish (es-UY)

---

## ✅ Checklist for Analysis Completion

Before considering analysis complete, verify:

- [ ] All Tier 1 repositories analyzed
- [ ] Module comparison matrix complete
- [ ] Exemplar modules identified
- [ ] Evolution recommendations generated
- [ ] Integration opportunities documented
- [ ] Risk assessment completed
- [ ] Architecture diagrams created
- [ ] Action plan prioritized
- [ ] All files include export_seal
- [ ] Reports saved in `.cursor/plans/`

---

**Export Seal:**
```json
{
  "export_seal": {
    "project": "Ultimate-CHATBOT",
    "prompt_id": "usage-guide-master-prompt",
    "version": "v1.0",
    "created_at": "2024-12-28T00:00:00Z",
    "author": "BMC",
    "origin": "ArchitectBot"
  }
}
```

