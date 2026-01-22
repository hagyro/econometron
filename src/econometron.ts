/**
 * Econometron: Elite Econometrician Agent
 * 
 * An AI agent specialized in econometrics, causal inference, and quantitative methods.
 * Built on the Claude Agent SDK for autonomous analysis and code generation.
 * 
 * @author Based on Claude Agent SDK
 * @version 1.0.0
 */

import { query, ClaudeAgentOptions, AgentDefinition, HookCallback } from "@anthropic-ai/claude-agent-sdk";
import { appendFileSync, existsSync, mkdirSync } from "fs";
import { join } from "path";

// =============================================================================
// SYSTEM PROMPT
// =============================================================================

const ECONOMETRON_SYSTEM_PROMPT = `You are Econometron, an elite econometrician and mathematical statistician.

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
- Synthetic control and matrix completion`;

// =============================================================================
// SUBAGENTS
// =============================================================================

const SUBAGENTS: Record<string, AgentDefinition> = {
  "code-generator": {
    description: "Generates publication-quality econometric code in R, Stata, or Python",
    prompt: `You are a code generation specialist for econometrics.
    
Your outputs must be:
- Correct and runnable without modification
- Well-commented with clear variable names
- Include diagnostic outputs and sanity checks
- Follow best practices for the target language
- Handle edge cases gracefully

For R: Use tidyverse style, prefer fixest/lfe for panel data, sandwich/clubSandwich for robust SEs
For Stata: Use modern syntax, include eststo/esttab for tables, handle factor variables properly
For Python: Use statsmodels/linearmodels, follow PEP8, include type hints

Always include a header comment with: purpose, inputs, outputs, dependencies.`,
    tools: ["Read", "Write", "Bash", "Glob", "Grep"]
  },
  
  "diagnostics-checker": {
    description: "Runs comprehensive econometric diagnostics and reports issues",
    prompt: `You are a diagnostics specialist for econometric analysis.
    
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

Be thorough but prioritize issues by severity.`,
    tools: ["Read", "Bash", "Glob", "Grep"]
  },
  
  "literature-synthesizer": {
    description: "Synthesizes econometric methodology literature and best practices",
    prompt: `You are a methodological literature expert in econometrics.
    
When asked about methods, provide:
- Standard references (without fabricating specific citations)
- Evolution of the method and current best practices
- Key assumptions and when they're likely violated
- Comparison with alternative approaches
- Practical implementation guidance

Be precise about what is established vs. contested in the literature.
Never fabricate specific paper titles, authors, or journal citations.`,
    tools: ["Read", "WebSearch", "WebFetch"]
  },
  
  "robustness-designer": {
    description: "Designs comprehensive robustness check protocols",
    prompt: `You are a robustness analysis specialist.
    
Design thorough robustness protocols covering:
1. Alternative specifications (functional form, controls, sample)
2. Alternative inference (different SE methods, bootstrap, RI)
3. Alternative identification (placebo tests, falsification)
4. Sensitivity analysis (bounds, coefficient stability)

For each check:
- Explain what assumption it probes
- Describe how to interpret results
- Specify what would constitute a "pass" or "fail"

Prioritize checks that are most informative for the specific context.`,
    tools: ["Read", "Glob", "Grep"]
  }
};

// =============================================================================
// HOOKS
// =============================================================================

// Audit logging hook for tracking all tool usage
const auditLog: HookCallback = async (input, toolUseId, context) => {
  const timestamp = new Date().toISOString();
  const logDir = "./logs";
  
  if (!existsSync(logDir)) {
    mkdirSync(logDir, { recursive: true });
  }
  
  const logEntry = {
    timestamp,
    toolUseId,
    tool: (input as any).tool_name || "unknown",
    input: JSON.stringify((input as any).tool_input || {}).slice(0, 500)
  };
  
  appendFileSync(
    join(logDir, "econometron-audit.jsonl"),
    JSON.stringify(logEntry) + "\n"
  );
  
  return {};
};

// Validation hook for code execution
const validateCodeExecution: HookCallback = async (input) => {
  const toolInput = (input as any).tool_input || {};
  const command = toolInput.command || "";
  
  // Block potentially dangerous operations
  const blockedPatterns = [
    /rm\s+-rf\s+\//,  // Destructive file operations
    /curl.*\|.*sh/,   // Piped remote execution
    /wget.*\|.*sh/,
  ];
  
  for (const pattern of blockedPatterns) {
    if (pattern.test(command)) {
      return {
        decision: "block",
        reason: "Potentially dangerous command blocked for safety"
      };
    }
  }
  
  return {};
};

// =============================================================================
// MAIN QUERY FUNCTION
// =============================================================================

interface EconometronOptions {
  prompt: string;
  workingDirectory?: string;
  language?: "R" | "Stata" | "Python" | "all";
  outputFormat?: "markdown" | "latex" | "html";
  includeCode?: boolean;
  verbose?: boolean;
  sessionId?: string;
}

export async function* runEconometron(options: EconometronOptions) {
  const {
    prompt,
    workingDirectory = process.cwd(),
    language = "R",
    outputFormat = "markdown",
    includeCode = true,
    verbose = false,
    sessionId
  } = options;

  // Build context-aware prompt
  const enhancedPrompt = buildEnhancedPrompt(prompt, { language, outputFormat, includeCode });

  // Configure agent options
  const agentOptions: ClaudeAgentOptions = {
    systemPrompt: ECONOMETRON_SYSTEM_PROMPT,
    allowedTools: [
      "Read",
      "Write", 
      "Edit",
      "Bash",
      "Glob",
      "Grep",
      "WebSearch",
      "WebFetch",
      "Task",           // For subagent delegation
      "AskUserQuestion" // For clarifying questions
    ],
    agents: SUBAGENTS,
    cwd: workingDirectory,
    permissionMode: "acceptEdits",
    hooks: {
      PostToolUse: [
        { matcher: ".*", hooks: [auditLog] }
      ],
      PreToolUse: [
        { matcher: "Bash", hooks: [validateCodeExecution] }
      ]
    },
    ...(sessionId && { resume: sessionId })
  };

  // Run the agent
  for await (const message of query({
    prompt: enhancedPrompt,
    options: agentOptions
  })) {
    if (verbose) {
      console.log(`[${message.type}]`, JSON.stringify(message).slice(0, 200));
    }
    yield message;
  }
}

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

function buildEnhancedPrompt(
  userPrompt: string,
  options: { language: string; outputFormat: string; includeCode: boolean }
): string {
  const { language, outputFormat, includeCode } = options;
  
  let contextBlock = "";
  
  if (language !== "all") {
    contextBlock += `\nPreferred programming language: ${language}`;
  }
  
  contextBlock += `\nOutput format: ${outputFormat}`;
  
  if (includeCode) {
    contextBlock += "\nInclude executable code examples where appropriate.";
  }
  
  return `${userPrompt}\n\n[Context]${contextBlock}`;
}

// =============================================================================
// SPECIALIZED WORKFLOWS
// =============================================================================

/**
 * Run a full econometric analysis workflow
 */
export async function* runFullAnalysis(
  researchQuestion: string,
  dataPath: string,
  options?: Partial<EconometronOptions>
) {
  const analysisPrompt = `
## Research Question
${researchQuestion}

## Data
The data is located at: ${dataPath}

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
`;

  yield* runEconometron({
    prompt: analysisPrompt,
    ...options
  });
}

/**
 * Review and critique an existing econometric analysis
 */
export async function* reviewAnalysis(
  analysisPath: string,
  options?: Partial<EconometronOptions>
) {
  const reviewPrompt = `
## Review Task
Please review the econometric analysis at: ${analysisPath}

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
`;

  yield* runEconometron({
    prompt: reviewPrompt,
    ...options
  });
}

/**
 * Generate replication code for a specific estimator
 */
export async function* generateEstimatorCode(
  estimator: string,
  dataDescription: string,
  language: "R" | "Stata" | "Python" = "R",
  options?: Partial<EconometronOptions>
) {
  const codePrompt = `
## Code Generation Task
Generate complete, publication-quality code for: ${estimator}

## Data Description
${dataDescription}

## Requirements
- Language: ${language}
- Include all necessary data preparation
- Implement proper standard error computation
- Add diagnostic tests
- Generate formatted output tables
- Include extensive comments
- Handle potential errors gracefully

The code should be ready to run after specifying data paths.
`;

  yield* runEconometron({
    prompt: codePrompt,
    language,
    includeCode: true,
    ...options
  });
}

// =============================================================================
// CLI ENTRY POINT
// =============================================================================

async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log(`
Econometron - Elite Econometrician Agent
=========================================

Usage:
  npx ts-node econometron.ts "<prompt>"
  npx ts-node econometron.ts --analyze "<research question>" --data "<data path>"
  npx ts-node econometron.ts --review "<analysis path>"
  npx ts-node econometron.ts --generate "<estimator>" --data "<description>" --lang R|Stata|Python

Options:
  --verbose    Show detailed message stream
  --lang       Programming language (R, Stata, Python)
  --format     Output format (markdown, latex, html)
`);
    process.exit(0);
  }

  // Parse arguments
  const verbose = args.includes("--verbose");
  const langIndex = args.indexOf("--lang");
  const language = langIndex >= 0 ? args[langIndex + 1] as "R" | "Stata" | "Python" : "R";
  
  let result = "";
  
  if (args.includes("--analyze")) {
    const analyzeIndex = args.indexOf("--analyze");
    const dataIndex = args.indexOf("--data");
    const question = args[analyzeIndex + 1];
    const dataPath = dataIndex >= 0 ? args[dataIndex + 1] : "./data";
    
    for await (const message of runFullAnalysis(question, dataPath, { verbose, language })) {
      if ("result" in message) {
        result = message.result as string;
      }
    }
  } else if (args.includes("--review")) {
    const reviewIndex = args.indexOf("--review");
    const analysisPath = args[reviewIndex + 1];
    
    for await (const message of reviewAnalysis(analysisPath, { verbose, language })) {
      if ("result" in message) {
        result = message.result as string;
      }
    }
  } else if (args.includes("--generate")) {
    const generateIndex = args.indexOf("--generate");
    const dataIndex = args.indexOf("--data");
    const estimator = args[generateIndex + 1];
    const dataDesc = dataIndex >= 0 ? args[dataIndex + 1] : "Standard panel data";
    
    for await (const message of generateEstimatorCode(estimator, dataDesc, language, { verbose })) {
      if ("result" in message) {
        result = message.result as string;
      }
    }
  } else {
    // Direct prompt
    const prompt = args.filter(a => !a.startsWith("--"))[0];
    
    for await (const message of runEconometron({ prompt, verbose, language })) {
      if ("result" in message) {
        result = message.result as string;
      }
    }
  }
  
  console.log("\n" + "=".repeat(80));
  console.log("RESULT:");
  console.log("=".repeat(80));
  console.log(result);
}

// Run if executed directly
if (require.main === module) {
  main().catch(console.error);
}
