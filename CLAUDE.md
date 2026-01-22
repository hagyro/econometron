# Econometron Project Context

## Overview
Econometron is an elite econometrician AI agent built on the Claude Agent SDK. It provides publication-grade econometric analysis, code generation, and methodological guidance.

## Design Principles

1. **Rigorous by Default**: Never assume away endogeneity, selection, or dependence
2. **Structured Output**: Goal → Estimand → Identification → Estimation → Inference → Diagnostics → Robustness → Interpretation
3. **Multi-Language Support**: R (primary), Stata, Python
4. **Reproducibility**: Complete, runnable code with clear documentation
5. **Academic Standards**: Precise wording, explicit assumptions, no fabricated citations

## Key Components

### System Prompt
Located in `src/econometron.ts` and `src/econometron.py`. Contains:
- Core identity and expertise areas
- Operating rules (10 rules)
- Domain-specific knowledge sections
- Output format specifications

### Subagents
Four specialized agents for delegation:
- `code-generator`: Publication-quality code
- `diagnostics-checker`: Specification/inference issues
- `literature-synthesizer`: Methodology literature
- `robustness-designer`: Robustness protocols

### Slash Commands
Pre-built workflows for common analyses:
- `/did` - Difference-in-differences
- `/iv` - Instrumental variables
- `/rdd` - Regression discontinuity
- `/panel` - Panel data analysis

## Code Conventions

### R Preferences
- tidyverse style
- fixest/lfe for panel data
- sandwich/clubSandwich for robust SEs
- rdrobust for RDD
- did/synthdid for DID

### Stata Preferences
- Modern syntax
- reghdfe for fixed effects
- eststo/esttab for tables
- boottest for wild bootstrap

### Python Preferences
- statsmodels/linearmodels
- PEP8 style
- Type hints
- Error handling

## Testing

Run tests with:
```bash
pytest tests/ -v
```

## Common Workflows

### Adding a New Estimator
1. Add to system prompt knowledge section
2. Create slash command in `.claude/commands/`
3. Add example to README
4. Add tests

### Modifying Behavior
1. Update `ECONOMETRON_SYSTEM_PROMPT`
2. Sync changes between TypeScript and Python versions
3. Update skill file if needed

## References

- Agent SDK docs: https://docs.anthropic.com/en/docs/agent-sdk/overview
- Econometrics references: Keep methodological claims generic; never fabricate citations
