# Regression Discontinuity Design

Conduct a rigorous regression discontinuity analysis.

## Input Required
- Research question: effect of treatment at cutoff
- Running variable definition
- Cutoff value
- Sharp or fuzzy design
- Data structure and sample size

## Analysis Steps

1. **Design Validation**
   - McCrary density test: manipulation at cutoff?
   - Visualize running variable distribution
   - If manipulation: reconsider design

2. **Covariate Balance**
   - Test covariate smoothness at cutoff
   - RD estimates for pre-determined variables
   - Visualization of covariates around cutoff

3. **Bandwidth Selection**
   - MSE-optimal bandwidth (rdrobust)
   - CER-optimal bandwidth for coverage
   - Report both for robustness

4. **Main Estimation** (Sharp RD)
   - Local polynomial regression
   - Order: typically p=1 (local linear)
   - Bias correction with robust SEs
   - Use rdrobust package

5. **Fuzzy RD** (if applicable)
   - First stage at cutoff
   - 2SLS with local polynomial
   - Interpret as LATE for compliers

6. **Visualization**
   - Scatter plot with fitted polynomials
   - Optimal bin selection (rdplot)
   - Clear discontinuity at cutoff

7. **Robustness**
   - Alternative bandwidths (0.5×, 0.75×, 1.5×, 2×)
   - Alternative polynomial orders (p=0, p=2)
   - Donut RD (exclude observations near cutoff)
   - Placebo cutoffs (away from true cutoff)
   - Covariates as controls (shouldn't change much)

8. **Sensitivity Analysis**
   - Local randomization framework
   - Falsification with predetermined outcomes

## Output
- RD plot with optimal bins
- Main estimates table (multiple specifications)
- Covariate balance table
- Robustness to bandwidth choices
- Clear LATE interpretation
