"""
Econometron: Elite Econometrician Agent

An AI agent specialized in econometrics, causal inference, and quantitative methods.
Built on the Claude Agent SDK for autonomous analysis and code generation.

Author: Based on Claude Agent SDK
Version: 1.0.0
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import AsyncIterator, Literal, Optional, Any

from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AgentDefinition,
    HookMatcher,
)

# =============================================================================
# SYSTEM PROMPT
# =============================================================================

ECONOMETRON_SYSTEM_PROMPT = """You are Econometron, an elite econometrician and mathematical statistician.

## Core Identity

You think in estimands, identification, asymptotics, and finite-sample behavior.
You have deep working knowledge of:
- Causal inference (potential outcomes, DAGs, selection on observables/unobservables)
- Panel data (fixed effects, random effects, correlated random effects, dynamic panels)
- Time series (ARIMA, VAR, cointegration, state-space models)
- Microeconometrics (discrete choice, duration models, count data, sample selection)
- GMM/IV (moment conditions, weak instruments, many instruments)
- Bayesian methods (hierarchical models, MCMC diagnostics, model comparison)
- ML for causal/predictive tasks (LASSO, random forests, causal forests, double ML)
- Robust inference (cluster/HAC, randomization inference, wild bootstrap, weak IV)

## Primary Objective

Deliver correct, reproducible, publication-grade econometric guidance and outputs.

## Operating Rules

1. **Clarify the Target First**
   - Always begin by clarifying: prediction vs inference vs causal effect
   - Define the estimand in mathematical notation when appropriate
   - Ask clarifying questions if the research question is ambiguous

2. **Provide Structured Analysis**
   Follow this framework for substantive econometric questions:
   - **Goal**: What are we trying to learn?
   - **Estimand**: Mathematical definition of the target parameter
   - **Identification**: What assumptions map data to estimand?
   - **Estimation**: Which estimator? Why?
   - **Inference**: Standard errors, confidence intervals, tests
   - **Diagnostics**: What could go wrong? How to check?
   - **Robustness**: Alternative specifications and sensitivity
   - **Interpretation**: Economic/substantive meaning

3. **Never Assume Away Problems**
   Explicitly address each potential issue:
   - Endogeneity (omitted variables, reverse causality, measurement error)
   - Selection (sample selection, attrition, survivorship)
   - Measurement error (classical vs non-classical)
   - Missingness (MCAR, MAR, MNAR)
   - Dependence (serial correlation, spatial correlation, clustering)

4. **Estimator Specifications**
   When recommending an estimator, always specify:
   - Moment conditions or likelihood function
   - Standard error construction (robust/cluster/HAC/bootstrap)
   - Conditions for consistency and asymptotic normality
   - Key failure modes and their consequences
   - Finite-sample considerations

5. **Robustness by Default**
   Propose at least 3 robustness checks:
   - Alternative specification / functional form
   - Alternative inference (wild cluster bootstrap, randomization inference)
   - Alternative identification or placebo/falsification test

6. **Reproducible Workflows**
   When data are involved:
   - Clear variable definitions with units
   - Explicit data transformations and their justification
   - Sample construction and exclusion criteria
   - Pre-analysis checks (balance, summary statistics)
   - Version control and documentation standards

7. **Communication Standards**
   - Be concise, skeptical, explicit about assumptions
   - Use precise wording suitable for academic writing
   - Flag limitations prominently
   - Distinguish between statistical and economic significance
   - Never fabricate citations or results

8. **Code Quality**
   When providing code:
   - Correct, runnable code with comments
   - Minimize dependencies; use standard packages
   - Include diagnostic outputs
   - Sensible defaults with options for customization
   - Error handling for common edge cases

9. **Maintain High Standards**
   - If a model is weak, say so clearly
   - Propose better alternatives when appropriate
   - Acknowledge uncertainty in recommendations
   - Cite the econometric literature when making methodological claims

10. **Output Format**
    Default structure for technical responses:
    - Goal → Estimand → Identification → Estimation → Inference → Diagnostics → Robustness → Interpretation → Next steps
    - Use LaTeX math notation when helpful
    - Produce copy-ready deliverables when requested

## Personality

Calm, rigorous, direct. No fluff. Deep technical reasoning, but explain options and tradeoffs clearly. Act as a top coauthor who wants the paper to be bulletproof.

## Domain-Specific Knowledge

### Causal Inference
- Potential outcomes framework (Rubin causal model)
- Selection on observables: matching, propensity scores, IPW, doubly robust
- Selection on unobservables: IV, RDD, DID, synthetic control
- Heterogeneous treatment effects: CATE, LATE, MTE

### Panel Data
- Within vs between variation
- Mundlak/Chamberlain approach
- Nickell bias in dynamic panels
- System GMM vs difference GMM

### Time Series
- Stationarity and unit root tests
- Spurious regression problem
- Structural breaks and regime switching
- Forecasting vs structural analysis

### Inference
- Cluster-robust standard errors (CR0 vs CR2 vs CR3)
- Wild cluster bootstrap (Webb weights, Rademacher)
- Randomization inference for small samples
- Multiple testing corrections

### Modern Methods
- High-dimensional regression (LASSO, elastic net, ridge)
- Double/debiased ML for causal inference
- Causal forests and honest inference
- Synthetic control and matrix completion"""


# =============================================================================
# SUBAGENTS
# =============================================================================

SUBAGENTS = {
    "code-generator": AgentDefinition(
        description="Generates publication-quality econometric code in R, Stata, or Python",
        prompt="""You are a code generation specialist for econometrics.
    
Your outputs must be:
- Correct and runnable without modification
- Well-commented with clear variable names
- Include diagnostic outputs and sanity checks
- Follow best practices for the target language
- Handle edge cases gracefully

For R: Use tidyverse style, prefer fixest/lfe for panel data, sandwich/clubSandwich for robust SEs
For Stata: Use modern syntax, include eststo/esttab for tables, handle factor variables properly
For Python: Use statsmodels/linearmodels, follow PEP8, include type hints

Always include a header comment with: purpose, inputs, outputs, dependencies.""",
        tools=["Read", "Write", "Bash", "Glob", "Grep"]
    ),
    
    "diagnostics-checker": AgentDefinition(
        description="Runs comprehensive econometric diagnostics and reports issues",
        prompt="""You are a diagnostics specialist for econometric analysis.
    
Your job is to identify potential problems in econometric specifications:
- Endogeneity concerns
- Specification errors (functional form, omitted variables)
- Inference issues (heteroskedasticity, serial correlation, clustering)
- Data quality (outliers, influential observations, multicollinearity)
- Identification problems (weak instruments, parallel trends violations)

For each issue found:
1. Describe the problem clearly
2. Explain the consequence if ignored
3. Suggest specific tests or checks
4. Propose remedies

Be thorough but prioritize issues by severity.""",
        tools=["Read", "Bash", "Glob", "Grep"]
    ),
    
    "literature-synthesizer": AgentDefinition(
        description="Synthesizes econometric methodology literature and best practices",
        prompt="""You are a methodological literature expert in econometrics.
    
When asked about methods, provide:
- Standard references (without fabricating specific citations)
- Evolution of the method and current best practices
- Key assumptions and when they're likely violated
- Comparison with alternative approaches
- Practical implementation guidance

Be precise about what is established vs. contested in the literature.
Never fabricate specific paper titles, authors, or journal citations.""",
        tools=["Read", "WebSearch", "WebFetch"]
    ),
    
    "robustness-designer": AgentDefinition(
        description="Designs comprehensive robustness check protocols",
        prompt="""You are a robustness analysis specialist.
    
Design thorough robustness protocols covering:
1. Alternative specifications (functional form, controls, sample)
2. Alternative inference (different SE methods, bootstrap, RI)
3. Alternative identification (placebo tests, falsification)
4. Sensitivity analysis (bounds, coefficient stability)

For each check:
- Explain what assumption it probes
- Describe how to interpret results
- Specify what would constitute a "pass" or "fail"

Prioritize checks that are most informative for the specific context.""",
        tools=["Read", "Glob", "Grep"]
    )
}


# =============================================================================
# HOOKS
# =============================================================================

async def audit_log(input_data: dict, tool_use_id: str, context: Any) -> dict:
    """Log all tool usage for audit purposes."""
    timestamp = datetime.now().isoformat()
    log_dir = Path("./logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_entry = {
        "timestamp": timestamp,
        "tool_use_id": tool_use_id,
        "tool": input_data.get("tool_name", "unknown"),
        "input": json.dumps(input_data.get("tool_input", {}))[:500]
    }
    
    log_file = log_dir / "econometron-audit.jsonl"
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    
    return {}


async def validate_code_execution(input_data: dict, tool_use_id: str, context: Any) -> dict:
    """Validate bash commands before execution."""
    import re
    
    tool_input = input_data.get("tool_input", {})
    command = tool_input.get("command", "")
    
    # Block potentially dangerous operations
    blocked_patterns = [
        r"rm\s+-rf\s+/",      # Destructive file operations
        r"curl.*\|.*sh",      # Piped remote execution
        r"wget.*\|.*sh",
    ]
    
    for pattern in blocked_patterns:
        if re.search(pattern, command):
            return {
                "decision": "block",
                "reason": "Potentially dangerous command blocked for safety"
            }
    
    return {}


# =============================================================================
# MAIN QUERY FUNCTION
# =============================================================================

Language = Literal["R", "Stata", "Python", "all"]
OutputFormat = Literal["markdown", "latex", "html"]


async def run_econometron(
    prompt: str,
    working_directory: Optional[str] = None,
    language: Language = "R",
    output_format: OutputFormat = "markdown",
    include_code: bool = True,
    verbose: bool = False,
    session_id: Optional[str] = None,
) -> AsyncIterator[Any]:
    """
    Run Econometron agent with the given prompt.
    
    Args:
        prompt: The user's econometric question or task
        working_directory: Working directory for file operations
        language: Preferred programming language for code
        output_format: Format for output (markdown, latex, html)
        include_code: Whether to include executable code examples
        verbose: Whether to print detailed message stream
        session_id: Optional session ID to resume
        
    Yields:
        Message objects from the agent
    """
    if working_directory is None:
        working_directory = os.getcwd()
    
    # Build context-aware prompt
    enhanced_prompt = _build_enhanced_prompt(
        prompt, 
        language=language, 
        output_format=output_format, 
        include_code=include_code
    )
    
    # Configure agent options
    agent_options = ClaudeAgentOptions(
        system_prompt=ECONOMETRON_SYSTEM_PROMPT,
        allowed_tools=[
            "Read",
            "Write",
            "Edit",
            "Bash",
            "Glob",
            "Grep",
            "WebSearch",
            "WebFetch",
            "Task",            # For subagent delegation
            "AskUserQuestion"  # For clarifying questions
        ],
        agents=SUBAGENTS,
        cwd=working_directory,
        permission_mode="acceptEdits",
        hooks={
            "PostToolUse": [HookMatcher(matcher=".*", hooks=[audit_log])],
            "PreToolUse": [HookMatcher(matcher="Bash", hooks=[validate_code_execution])]
        },
    )
    
    if session_id:
        agent_options.resume = session_id
    
    # Run the agent
    async for message in query(
        prompt=enhanced_prompt,
        options=agent_options
    ):
        if verbose:
            print(f"[{message.type}]", str(message)[:200])
        yield message


def _build_enhanced_prompt(
    user_prompt: str,
    language: str,
    output_format: str,
    include_code: bool
) -> str:
    """Build an enhanced prompt with context information."""
    context_parts = []
    
    if language != "all":
        context_parts.append(f"Preferred programming language: {language}")
    
    context_parts.append(f"Output format: {output_format}")
    
    if include_code:
        context_parts.append("Include executable code examples where appropriate.")
    
    context_block = "\n".join(context_parts)
    
    return f"{user_prompt}\n\n[Context]\n{context_block}"


# =============================================================================
# SPECIALIZED WORKFLOWS
# =============================================================================

async def run_full_analysis(
    research_question: str,
    data_path: str,
    language: Language = "R",
    verbose: bool = False,
) -> AsyncIterator[Any]:
    """
    Run a full econometric analysis workflow.
    
    Args:
        research_question: The research question to investigate
        data_path: Path to the data file
        language: Preferred programming language
        verbose: Whether to print detailed messages
        
    Yields:
        Message objects from the agent
    """
    analysis_prompt = f"""
## Research Question
{research_question}

## Data
The data is located at: {data_path}

## Required Analysis
Please conduct a complete econometric analysis following this workflow:

1. **Data Exploration**: Load the data, examine structure, compute summary statistics
2. **Variable Construction**: Define and construct all necessary variables
3. **Preliminary Analysis**: Check for data quality issues, patterns
4. **Main Estimation**: Estimate the primary specification(s)
5. **Inference**: Compute appropriate standard errors and confidence intervals
6. **Diagnostics**: Run all relevant diagnostic tests
7. **Robustness**: Implement at least 3 robustness checks
8. **Output**: Generate publication-quality tables and figures

Provide complete, runnable code and interpret all results.
"""
    
    async for message in run_econometron(
        prompt=analysis_prompt,
        language=language,
        verbose=verbose,
        include_code=True
    ):
        yield message


async def review_analysis(
    analysis_path: str,
    language: Language = "R",
    verbose: bool = False,
) -> AsyncIterator[Any]:
    """
    Review and critique an existing econometric analysis.
    
    Args:
        analysis_path: Path to the analysis files
        language: Preferred programming language
        verbose: Whether to print detailed messages
        
    Yields:
        Message objects from the agent
    """
    review_prompt = f"""
## Review Task
Please review the econometric analysis at: {analysis_path}

Evaluate:
1. **Research Design**: Is the identification strategy credible?
2. **Estimation**: Are the estimators appropriate?
3. **Inference**: Are standard errors computed correctly?
4. **Robustness**: Are the robustness checks sufficient?
5. **Presentation**: Are results presented clearly and honestly?

For each issue found:
- Severity (critical / important / minor)
- Description of the problem
- Recommendation for fixing it
- Code snippet if applicable

Be constructive but rigorous.
"""
    
    async for message in run_econometron(
        prompt=review_prompt,
        language=language,
        verbose=verbose
    ):
        yield message


async def generate_estimator_code(
    estimator: str,
    data_description: str,
    language: Language = "R",
    verbose: bool = False,
) -> AsyncIterator[Any]:
    """
    Generate replication code for a specific estimator.
    
    Args:
        estimator: Name/description of the estimator
        data_description: Description of the data structure
        language: Programming language for code
        verbose: Whether to print detailed messages
        
    Yields:
        Message objects from the agent
    """
    code_prompt = f"""
## Code Generation Task
Generate complete, publication-quality code for: {estimator}

## Data Description
{data_description}

## Requirements
- Language: {language}
- Include all necessary data preparation
- Implement proper standard error computation
- Add diagnostic tests
- Generate formatted output tables
- Include extensive comments
- Handle potential errors gracefully

The code should be ready to run after specifying data paths.
"""
    
    async for message in run_econometron(
        prompt=code_prompt,
        language=language,
        verbose=verbose,
        include_code=True
    ):
        yield message


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

async def main():
    """CLI entry point for Econometron."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Econometron - Elite Econometrician Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python econometron.py "How should I estimate the effect of X on Y?"
  python econometron.py --analyze "Does minimum wage affect employment?" --data ./data/panel.csv
  python econometron.py --review ./analysis/
  python econometron.py --generate "difference-in-differences" --data "State-year panel, 2000-2020" --lang Stata
        """
    )
    
    parser.add_argument("prompt", nargs="?", help="Direct prompt for Econometron")
    parser.add_argument("--analyze", help="Research question for full analysis")
    parser.add_argument("--review", help="Path to analysis to review")
    parser.add_argument("--generate", help="Estimator to generate code for")
    parser.add_argument("--data", help="Data path or description")
    parser.add_argument("--lang", choices=["R", "Stata", "Python"], default="R",
                       help="Programming language (default: R)")
    parser.add_argument("--format", choices=["markdown", "latex", "html"], default="markdown",
                       help="Output format (default: markdown)")
    parser.add_argument("--verbose", action="store_true", help="Show detailed messages")
    
    args = parser.parse_args()
    
    result = ""
    
    if args.analyze:
        data_path = args.data or "./data"
        async for message in run_full_analysis(
            args.analyze, data_path, args.lang, args.verbose
        ):
            if hasattr(message, "result"):
                result = message.result
                
    elif args.review:
        async for message in review_analysis(args.review, args.lang, args.verbose):
            if hasattr(message, "result"):
                result = message.result
                
    elif args.generate:
        data_desc = args.data or "Standard panel data"
        async for message in generate_estimator_code(
            args.generate, data_desc, args.lang, args.verbose
        ):
            if hasattr(message, "result"):
                result = message.result
                
    elif args.prompt:
        async for message in run_econometron(
            args.prompt,
            language=args.lang,
            output_format=args.format,
            verbose=args.verbose
        ):
            if hasattr(message, "result"):
                result = message.result
    else:
        parser.print_help()
        return
    
    print("\n" + "=" * 80)
    print("RESULT:")
    print("=" * 80)
    print(result)


def cli():
    """Synchronous CLI entry point for setuptools console_scripts."""
    asyncio.run(main())


if __name__ == "__main__":
    cli()
