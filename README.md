# Econometron

**Elite Econometrician Agent** — Publication-grade econometric analysis powered by Claude Agent SDK

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Node 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)

---

## Overview

Econometron is an AI agent specialized in econometrics, causal inference, and quantitative methods. Built on the [Claude Agent SDK](https://docs.anthropic.com/en/docs/agent-sdk/overview), it provides autonomous analysis, code generation, and methodological guidance at publication quality.

### Key Capabilities

| Capability | Description |
|------------|-------------|
| **Structured Analysis** | Follows rigorous Goal → Estimand → Identification → Estimation → Inference → Diagnostics → Robustness → Interpretation framework |
| **Multi-Language Code** | Generates publication-ready code in R, Stata, and Python |
| **Subagent Delegation** | Specialized agents for code generation, diagnostics, literature synthesis, and robustness design |
| **Built-in Safety** | Hooks for audit logging and command validation |
| **Session Management** | Resume complex analyses across multiple interactions |

### Domain Expertise

- **Causal Inference**: Potential outcomes, DAGs, matching, IPW, DID, RDD, IV, synthetic control
- **Panel Data**: Fixed/random effects, dynamic panels, Nickell bias, system GMM
- **Time Series**: ARIMA, VAR, cointegration, state-space models
- **Microeconometrics**: Discrete choice, duration models, sample selection
- **Modern Methods**: Double ML, causal forests, LASSO, high-dimensional inference
- **Robust Inference**: Cluster-robust SEs, wild bootstrap, randomization inference

---

## Installation

### Prerequisites

1. **Claude Code Runtime** (required):
   ```bash
   # macOS/Linux/WSL
   curl -fsSL https://claude.ai/install.sh | bash
   
   # or Homebrew
   brew install --cask claude-code
   
   # or Windows
   winget install Anthropic.ClaudeCode
   ```

2. **API Key**:
   ```bash
   export ANTHROPIC_API_KEY=your-api-key
   ```

### TypeScript

```bash
cd econometron
npm install
npm run build
```

### Python

```bash
cd econometron
pip install -e .

# With econometrics packages
pip install -e ".[econometrics]"
```

---

## Quick Start

### TypeScript

```typescript
import { runEconometron } from "./src/econometron";

async function main() {
  for await (const message of runEconometron({
    prompt: "How should I estimate the causal effect of minimum wage on employment using state-level panel data?",
    language: "R",
    includeCode: true
  })) {
    if ("result" in message) {
      console.log(message.result);
    }
  }
}

main();
```

### Python

```python
import asyncio
from econometron import run_econometron

async def main():
    async for message in run_econometron(
        prompt="How should I estimate the causal effect of minimum wage on employment using state-level panel data?",
        language="R",
        include_code=True
    ):
        if hasattr(message, "result"):
            print(message.result)

asyncio.run(main())
```

### CLI

```bash
# Direct prompt
python src/econometron.py "What's the best approach for difference-in-differences with staggered adoption?"

# Full analysis workflow
python src/econometron.py --analyze "Does job training affect earnings?" --data ./data/training.csv --lang R

# Review existing analysis
python src/econometron.py --review ./analysis/did_results/

# Generate estimator code
python src/econometron.py --generate "two-way fixed effects" --data "Firm-year panel, 2010-2020" --lang Stata
```

---

## Architecture

### Core Components

```
econometron/
├── src/
│   ├── econometron.ts      # TypeScript implementation
│   └── econometron.py      # Python implementation
├── .claude/
│   └── skills/
│       └── ECONOMETRON.md  # Skill definition for Claude Code
├── logs/                   # Audit logs (auto-created)
├── package.json            # Node.js dependencies
├── pyproject.toml          # Python dependencies
└── README.md
```

### Subagents

Econometron delegates specialized tasks to focused subagents:

| Subagent | Purpose | Tools |
|----------|---------|-------|
| `code-generator` | Publication-quality code in R/Stata/Python | Read, Write, Bash, Glob, Grep |
| `diagnostics-checker` | Identifies specification and inference issues | Read, Bash, Glob, Grep |
| `literature-synthesizer` | Methodology literature and best practices | Read, WebSearch, WebFetch |
| `robustness-designer` | Comprehensive robustness protocols | Read, Glob, Grep |

### Hooks

Built-in hooks provide safety and observability:

- **Audit Logging**: All tool invocations logged to `logs/econometron-audit.jsonl`
- **Command Validation**: Dangerous bash commands blocked before execution

---

## API Reference

### `runEconometron(options)`

Main entry point for the Econometron agent.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | `string` | *required* | The econometric question or task |
| `workingDirectory` | `string` | `cwd()` | Working directory for file operations |
| `language` | `"R" \| "Stata" \| "Python" \| "all"` | `"R"` | Preferred programming language |
| `outputFormat` | `"markdown" \| "latex" \| "html"` | `"markdown"` | Output format |
| `includeCode` | `boolean` | `true` | Include executable code examples |
| `verbose` | `boolean` | `false` | Print detailed message stream |
| `sessionId` | `string` | `undefined` | Session ID to resume |

**Returns:** `AsyncIterator<Message>`

### Specialized Workflows

#### `runFullAnalysis(researchQuestion, dataPath, options?)`

Conducts complete econometric analysis including data exploration, estimation, diagnostics, and robustness.

#### `reviewAnalysis(analysisPath, options?)`

Reviews existing analysis for methodological issues with severity ratings and recommendations.

#### `generateEstimatorCode(estimator, dataDescription, language?, options?)`

Generates complete, runnable code for a specific estimator.

---

## Configuration

### Environment Variables

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Anthropic API key (required) |
| `CLAUDE_CODE_USE_BEDROCK` | Set to `1` for Amazon Bedrock |
| `CLAUDE_CODE_USE_VERTEX` | Set to `1` for Google Vertex AI |
| `CLAUDE_CODE_USE_FOUNDRY` | Set to `1` for Microsoft Foundry |

### Customizing the System Prompt

Modify `ECONOMETRON_SYSTEM_PROMPT` in the source files to adjust:
- Domain expertise emphasis
- Output format preferences
- Communication style
- Specific methodological requirements

### Adding Custom Subagents

```typescript
const agentOptions: ClaudeAgentOptions = {
  // ... existing options
  agents: {
    ...SUBAGENTS,
    "my-custom-agent": {
      description: "Custom agent for specific task",
      prompt: "Your custom instructions...",
      tools: ["Read", "Write", "Bash"]
    }
  }
};
```

---

## Examples

### Example 1: Difference-in-Differences with Staggered Treatment

```python
prompt = """
I have state-year panel data (2000-2020) where different states adopted a policy 
at different times between 2005-2015. I want to estimate the effect of the policy 
on employment.

Concerns:
- States that adopted early might be systematically different
- Pre-trends might not be parallel
- Effects might be heterogeneous over time

What's the right approach?
"""

async for msg in run_econometron(prompt=prompt, language="R"):
    if hasattr(msg, "result"):
        print(msg.result)
```

### Example 2: Instrumental Variables Analysis

```typescript
const prompt = `
I'm studying the effect of education on wages using quarter of birth as an instrument.
Data: CPS, N=500,000, years 1980-1990.

Questions:
1. Is this instrument likely valid?
2. How do I test for weak instruments?
3. What standard errors should I use?
4. How do I interpret LATE vs ATE?
`;

for await (const msg of runEconometron({ prompt, language: "Stata" })) {
  if ("result" in msg) console.log(msg.result);
}
```

### Example 3: Code Generation for Fixed Effects

```bash
python src/econometron.py --generate "two-way fixed effects with clustered SEs" \
  --data "Firm-year panel: firm_id, year, Y (outcome), D (treatment), X1-X5 (controls)" \
  --lang R
```

---

## Output Format

Econometron produces structured output following this framework:

```markdown
## Goal
[Clear statement of the research objective]

## Estimand
$$\theta = E[Y_i(1) - Y_i(0) | D_i = 1]$$
[Mathematical definition of the target parameter]

## Identification
[Key assumptions required to identify the estimand from data]
- Assumption 1: ...
- Assumption 2: ...

## Estimation
[Recommended estimator with justification]
- Moment conditions: ...
- Consistency requires: ...
- Efficiency considerations: ...

## Inference
[Standard error approach and test procedures]
- SE type: Cluster-robust at state level
- Justification: ...
- Confidence intervals: ...

## Diagnostics
[Tests and checks to validate assumptions]
1. Test 1: ...
2. Test 2: ...

## Robustness
[At least 3 robustness checks]
1. Alternative specification: ...
2. Alternative inference: ...
3. Placebo/falsification: ...

## Code
[Complete, runnable code if requested]

## Interpretation
[What the results mean substantively]

## Next Steps
[Recommendations for further analysis]
```

---

## Best Practices

### For Research Projects

1. **Start with the estimand**: Be explicit about what parameter you're trying to estimate
2. **Document assumptions**: Keep a running list of identification assumptions
3. **Plan robustness ex ante**: Define robustness checks before seeing results
4. **Version control everything**: Code, data definitions, and analysis decisions

### For Code Generation

1. **Specify the language clearly**: Different languages have different idioms
2. **Describe your data structure**: Variable names, types, and relationships
3. **Request diagnostic outputs**: Include tests in generated code
4. **Review before running**: Always check generated code for correctness

### For Complex Analyses

1. **Use session management**: Resume sessions to maintain context
2. **Delegate to subagents**: Let specialized agents handle focused tasks
3. **Iterate on robustness**: Build up robustness checks incrementally
4. **Document decisions**: Keep notes on methodological choices

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| "No API key found" | Set `ANTHROPIC_API_KEY` environment variable |
| "Claude Code not found" | Install Claude Code runtime |
| "Tool execution blocked" | Check audit logs; some commands are blocked for safety |
| "Session not found" | Session IDs expire; start a new session |

### Getting Help

- Check the [Claude Agent SDK documentation](https://docs.anthropic.com/en/docs/agent-sdk/overview)
- Review audit logs in `logs/econometron-audit.jsonl`
- Enable verbose mode (`--verbose`) for detailed debugging

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

### Development Setup

```bash
# TypeScript
npm install
npm run dev

# Python
pip install -e ".[dev]"
pytest
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Acknowledgments

Built on the [Claude Agent SDK](https://docs.anthropic.com/en/docs/agent-sdk/overview) by Anthropic.

Econometric methodology informed by decades of research in causal inference, panel data econometrics, and robust inference methods.
