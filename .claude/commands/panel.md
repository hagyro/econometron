# Panel Data Analysis

Conduct a rigorous panel data analysis.

## Input Required
- Research question
- Panel structure: entity (i) × time (t) dimensions
- Treatment/exposure variable
- Outcome variable(s)
- Time-varying and time-invariant controls
- Suspected sources of endogeneity

## Analysis Steps

1. **Panel Structure Diagnostics**
   - Balance check: is panel balanced?
   - Attrition analysis if unbalanced
   - Describe N, T, and N×T
   - Within vs between variation decomposition

2. **Model Selection**
   - Fixed effects (FE): control for time-invariant unobservables
   - Random effects (RE): efficiency if α_i uncorrelated with X
   - Correlated random effects (CRE/Mundlak): includes group means

3. **Specification Tests**
   - Hausman test: FE vs RE
   - But prefer: economic reasoning over statistical tests
   - F-test for joint significance of entity FEs

4. **FE Estimation**
   ```
   Y_it = α_i + λ_t + β X_it + ε_it
   ```
   - Entity fixed effects (α_i)
   - Time fixed effects (λ_t)
   - Identify from within-entity variation

5. **Inference**
   - Cluster SEs at entity level (default)
   - If T large: also check HAC for serial correlation
   - Few clusters? Wild cluster bootstrap

6. **Serial Correlation**
   - Wooldridge test for AR(1) in FE
   - If present: cluster SEs (robust) or model explicitly

7. **Dynamic Panels** (if lagged Y on RHS)
   - Nickell bias if T small
   - Arellano-Bond (difference GMM)
   - Blundell-Bond (system GMM)
   - AR tests for serial correlation in errors

8. **Robustness**
   - RE and CRE for comparison
   - Alternative clustering levels
   - Time trends by entity (if policy timing varies)
   - Placebo outcomes
   - Leave-one-out (entity or time period)

## Output
- Summary statistics by entity and time
- Main estimates table (OLS, FE, RE)
- Hausman test results
- Serial correlation diagnostics
- Robustness table
- Clear identification discussion
