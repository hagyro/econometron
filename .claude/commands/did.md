# Difference-in-Differences Analysis

Conduct a rigorous difference-in-differences analysis.

## Input Required
- Research question and hypothesis
- Treatment definition and timing
- Unit of observation
- Data structure (panel dimensions)
- Outcome variable(s)
- Control variables

## Analysis Steps

1. **Pre-Analysis**
   - Define treatment and control groups precisely
   - Identify treatment timing for each unit
   - Check for anticipation effects

2. **Parallel Trends**
   - Estimate event study specification
   - Test for pre-treatment differential trends
   - Visualize with confidence intervals

3. **Main Estimation**
   - Two-way fixed effects (if homogeneous effects)
   - Callaway-Sant'Anna or Sun-Abraham (if staggered)
   - Report ATT with appropriate SEs

4. **Inference**
   - Cluster at treatment level (or higher)
   - Wild cluster bootstrap if few clusters
   - Report effective number of clusters

5. **Robustness**
   - Alternative control groups
   - Placebo treatments (pre-period)
   - Placebo outcomes (unaffected by treatment)
   - Covariate balance checks
   - Sensitivity to parallel trends violations (Rambachan-Roth)

6. **Heterogeneity** (if relevant)
   - By treatment timing (early vs late adopters)
   - By unit characteristics
   - Dynamic effects over time

## Output
- Event study figure with 95% CIs
- Main estimates table
- Robustness table
- Clear interpretation of ATT
