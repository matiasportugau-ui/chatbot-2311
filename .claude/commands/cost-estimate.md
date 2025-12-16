---
description: "Calculate token usage and cost estimates for development phases"
---

# Cost Estimation Tool

Calculate token usage and USD cost for development work.

## Pricing (Claude Sonnet 4.5)
- **Input tokens:** $3.00 / 1M tokens
- **Output tokens:** $15.00 / 1M tokens
- **Web Search:** $10.00 / 1,000 requests

## Assumptions
- **Input/Output ratio:** 30% input, 70% output (conservative)
- **Tool overhead:** ~5% additional tokens for system/tool use
- **Web search:** $0.01 per search (when used)

## Token Usage Patterns

### By Activity
- **Planning:** 5,000-10,000 tokens
- **Implementation:** 20,000-40,000 tokens per phase
- **Documentation:** 5,000 tokens
- **Testing & debugging:** 10,000-20,000 tokens
- **Refactoring:** 8,000-15,000 tokens

### By Phase (Historical)
- **Phase 2 (Auth):** ~25,000 tokens
- **Phase 3 (Layout):** ~18,000 tokens
- **Phase 4 (State):** ~15,000 tokens
- **Phase 5 (Kanban):** ~22,000 tokens

## Calculate Cost

**Formula:**
```
cost = (input_tokens/1M * $3) + (output_tokens/1M * $15) + (searches/1000 * $10)
```

**Example (20k tokens, 2 searches):**
```
input = 20,000 * 0.30 = 6,000 tokens
output = 20,000 * 0.70 = 14,000 tokens

cost = (6k/1M * $3) + (14k/1M * $15) + (2/1000 * $10)
     = $0.018 + $0.210 + $0.020
     = $0.248 USD (~$0.25)
```

## Scenarios

**Economical (minimal assistance):**
- 10,000-15,000 tokens
- 0-1 web searches
- $0.10-$0.15 per phase

**Balanced (recommended):**
- 18,000-25,000 tokens
- 1-3 web searches
- $0.18-$0.27 per phase

**Exhaustive (max quality/speed):**
- 30,000-45,000 tokens
- 4-6 web searches
- $0.31-$0.48 per phase

## Session Budget

Current session limit: **200,000 tokens**

Example allocation:
- Phase 6: 25,000 tokens (balanced)
- Phase 7: 20,000 tokens (balanced)
- Phase 8: 18,000 tokens (balanced)
- Buffer: 137,000 tokens (68%)

## Monthly Budget Recommendations

**Hobby project:** $5/month (~50k tokens)
**Active development:** $15/month (~150k tokens)
**Professional:** $50/month (~500k tokens)

## Usage

Ask me:
- "Estimate cost for phase 6"
- "What's my token budget remaining?"
- "Show cost breakdown for next 3 phases"
