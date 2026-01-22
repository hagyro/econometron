# Instrumental Variables Analysis

Conduct a rigorous instrumental variables analysis.

## Input Required
- Research question: causal effect of X on Y
- Proposed instrument(s) Z
- Theoretical justification for exclusion restriction
- Data structure and sample size
- Control variables

## Analysis Steps

1. **Instrument Validity Assessment**
   - Relevance: Does Z predict X?
   - Exclusion: Does Z affect Y only through X?
   - Independence: Is Z as-good-as-random?
   - Document the theoretical argument for each

2. **First Stage**
   - Estimate: X = π₀ + π₁Z + γW + ε
   - Report F-statistic (robust to heteroskedasticity)
   - If F < 10: weak instrument concern
   - Multiple instruments: report effective F (Montiel Olea-Pflueger)

3. **Reduced Form**
   - Estimate: Y = α₀ + α₁Z + δW + ν
   - Sign and significance check
   - Wald estimand = α₁/π₁

4. **2SLS Estimation**
   - Estimate LATE (Local Average Treatment Effect)
   - Interpret: effect on compliers
   - Report with appropriate SEs (robust/cluster)

5. **Weak Instrument Robust Inference**
   - Anderson-Rubin confidence sets
   - tF confidence sets
   - Conditional likelihood ratio test

6. **Overidentification** (if multiple instruments)
   - Sargan-Hansen J-test
   - Caution: weak power, rejects if any instrument invalid

7. **Robustness**
   - Subset of instruments
   - Alternative control sets
   - Sensitivity to exclusion restriction violations (Conley et al.)
   - Placebo outcomes

## Output
- First stage table with F-statistic
- 2SLS estimates with weak-IV robust CIs
- LATE interpretation (who are compliers?)
- Robustness table
