# Feasibility Engine Guide
## RISKFERA AI — M5 Documentation

> **One-line purpose:** Answers the question — *can InnovaTech realistically acquire this company within its stated constraints?*

---

## Table of Contents

1. [What the Engine Does](#what-the-engine-does)
2. [Acquisition Constraints](#acquisition-constraints)
3. [Score Interpretation](#score-interpretation)
4. [The 4 Signals](#the-4-signals)
   - [Signal 1 — Budget Fit](#signal-1--budget-fit-max-40-pts)
   - [Signal 2 — P/E Valuation](#signal-2--pe-valuation-max-25-pts)
   - [Signal 3 — Equity Dilution](#signal-3--equity-dilution-max-20-pts)
   - [Signal 4 — Integration Complexity](#signal-4--integration-complexity-max-15-pts)
5. [Deal Structure Calculator](#deal-structure-calculator)
6. [Column Reference](#column-reference)
7. [Function Reference](#function-reference)
8. [How It Fits Into the Final Score](#how-it-fits-into-the-final-score)
9. [Running the Engine](#running-the-engine)
10. [Example Outputs](#example-outputs)
11. [Common Questions](#common-questions)

---

## What the Engine Does

The Feasibility Engine is the third and final scoring engine in the RISKFERA AI pipeline. It runs after the Risk Engine (M3) and Synergy Engine (M4) and evaluates whether a deal can actually close — regardless of how strategically attractive the target may be.

A company can score perfectly on Risk and Synergy but still be infeasible if:
- Its market cap makes the deal too expensive
- Its P/E ratio means buying it dilutes InnovaTech's earnings per share
- The equity swap required to fund the deal dilutes existing shareholders too heavily
- The business is growing so fast it cannot realistically be integrated in 6 months

The Feasibility Engine catches all four of these scenarios.

---

## Acquisition Constraints

Every parameter in the engine is derived from the hackathon brief. These are hard constraints — not preferences.

| Constraint | Value | Source |
|-----------|-------|--------|
| Maximum deal value | Rs. 180 Cr | Hackathon brief |
| Maximum cash outflow | Rs. 108 Cr | 60% of Rs. 180 Cr |
| Minimum non-cash payment | 40% of deal value | Hackathon brief |
| Acquisition premium assumed | 25% above market cap | Standard Indian IT M&A |
| InnovaTech market cap | Rs. 1,911 Cr | Brief (78 Cr profit × 24.5x P/E) |
| InnovaTech P/E | 24.5x | Brief (FY2025) |
| Maximum equity dilution target | 5% | Derived from shareholder impact |
| Integration timeline | 6 months | Hackathon brief |

**Why 25% acquisition premium?**
In Indian IT M&A, acquirers typically pay 20–35% above the current market price to convince target shareholders to sell. 25% is the conservative midpoint. This means the implied deal value for any company is:

```
Deal Value = Market Cap × 1.25
```

---

## Score Interpretation

The feasibility score runs from 0 to 100. Higher is better — higher means more acquirable.

| Score Range | Label | Meaning |
|------------|-------|---------|
| 70 – 100 | Highly Feasible | Deal fits comfortably within all constraints. Standard structure works. |
| 50 – 69 | Feasible with Structuring | Deal works but needs careful cash/equity split or minor earn-out. |
| 30 – 49 | Stretch Target | Exceeds budget or has dilution concerns. Requires creative deal structuring. |
| 0 – 29 | Not Feasible | Cannot be acquired within InnovaTech's current financial constraints. |

---

## The 4 Signals

Total maximum = 100 points. Higher points = more feasible.

```
Signal 1   Budget Fit          max 40 pts   (most important — hard constraint)
Signal 2   P/E Valuation       max 25 pts
Signal 3   Equity Dilution     max 20 pts
Signal 4   Integration         max 15 pts
─────────────────────────────────────────
Total                          max 100 pts
```

---

### Signal 1 — Budget Fit (max 40 pts)

**Column used:** `mar_cap_rscr`

**What it checks:**
Whether the implied deal value fits within InnovaTech's Rs. 180 Cr hard ceiling.

```
Implied Deal Value = mar_cap_rscr × 1.25
```

**Scoring:**

| Condition | Points | Interpretation |
|-----------|--------|---------------|
| Deal ≤ Rs. 126 Cr (70% of budget) | 40 | Comfortable — significant headroom |
| Deal ≤ Rs. 180 Cr (within budget) | 28 | Fits — manageable with standard structuring |
| Deal ≤ Rs. 216 Cr (up to 20% over) | 12 | Stretch — earn-out deferral needed |
| Deal > Rs. 216 Cr | 0 | Hard fail — not achievable within constraints |

**Why 40 points (highest weight)?**
Budget fit is a binary hard constraint. No amount of strategic synergy justifies a deal that exceeds InnovaTech's financial capacity. It carries the highest weight because it is the ultimate gate — a company fails feasibility primarily by failing this signal.

**Why 70% as the "comfortable" threshold?**
At Rs. 126 Cr deal value, InnovaTech retains Rs. 54 Cr headroom. This is enough to absorb a valuation renegotiation, due diligence discoveries, or market price movement during the deal period. Comfort is not just about fitting the number — it is about having room to manoeuvre.

**Real dataset context:**
- 142 companies fall within the Rs. 180 Cr budget (35% of the 400-company universe)
- 6 companies fall in the stretch zone (Rs. 180–216 Cr)
- 252 companies are too large — eliminated immediately by this signal

---

### Signal 2 — P/E Valuation (max 25 pts)

**Column used:** `p_e`

**What it checks:**
Whether buying this company at its current valuation is EPS accretive or dilutive for InnovaTech's shareholders.

**The core logic:**
InnovaTech trades at 24.5x P/E. If InnovaTech acquires a company at a lower P/E, each rupee of the target's earnings costs InnovaTech less than its own earnings are valued by the market. This is EPS accretive — good for shareholders. The inverse is true for higher P/E targets.

**Scoring:**

| P/E Range | Points | Interpretation |
|-----------|--------|---------------|
| P/E < 10x | 25 | Deep value — highly accretive entry point |
| P/E < 24.5x (below InnovaTech) | 20 | Accretive — buying cheaper than InnovaTech trades |
| P/E 24.5x – 35x | 10 | Mildly dilutive — synergies needed to justify |
| P/E 35x – 50x | 4 | Significantly dilutive — strong synergy case required |
| P/E > 50x | 0 | Highly dilutive — very difficult to justify financially |
| P/E missing / negative | 8 | Partial credit — likely loss-making, cannot assess |

**Why partial credit for missing P/E?**
A missing P/E almost always means the company is currently loss-making — P/E is undefined when earnings are negative. Giving zero would unfairly penalise high-growth companies in early profit stage. Giving full credit would be dishonest. 8 points (partial) reflects genuine uncertainty.

**Real dataset context:**
- Median P/E in dataset: 27.8x (slightly above InnovaTech's 24.5x)
- 144 companies have P/E below 24.5x (accretive for InnovaTech)
- 81 companies had originally missing P/E (filled with median by data loader)

---

### Signal 3 — Equity Dilution (max 20 pts)

**Column used:** `mar_cap_rscr` (derived calculation)

**What it checks:**
How much would InnovaTech's existing shareholders be diluted by the equity component of the deal?

**The calculation:**
```
Deal Value      = MCap × 1.25
Cash Component  = min(Deal × 60%, Rs. 108 Cr)
Equity Swap     = Deal - Cash Component
Dilution %      = (Equity Swap / InnovaTech MCap) × 100
                = (Equity Swap / Rs. 1,911 Cr) × 100
```

The 40% minimum non-cash requirement from the brief means every deal must issue some InnovaTech shares. The question is how many.

**Scoring:**

| Dilution | Points | Interpretation |
|----------|--------|---------------|
| < 1.0% | 20 | Negligible — shareholders barely affected |
| 1.0% – 2.5% | 16 | Low and acceptable |
| 2.5% – 5.0% | 10 | Moderate — within target threshold |
| > 5.0% | 3 | Above threshold — may face shareholder resistance |

**Why 5% as the threshold?**
Institutional investors in Indian listed companies typically require board approval and sometimes shareholder vote for equity issuance above 5% of outstanding shares. Staying below 5% keeps the deal clean from a governance perspective and avoids the risk of shareholder rejection.

**Real dataset context:**
Sample dilution calculations from actual feasible companies:

| Company | MCap (Cr) | Deal (Cr) | Equity Swap (Cr) | Dilution % |
|---------|-----------|-----------|-------------------|-----------|
| Globtier Infotec | 41.5 | 51.9 | 20.7 | 1.08% |
| Logiciel Solutions | 41.9 | 52.4 | 20.9 | 1.10% |
| ROX Hi-Tech | 86.4 | 108.0 | 43.2 | 2.26% |
| Elnet Technolog | 137.3 | 171.6 | 68.6 | 3.59% |
| Prodocs Solution | 143.8 | 179.8 | 71.9 | 3.76% |

All feasible companies (deal ≤ Rs. 180 Cr) produce dilution below 5% — the constraint is naturally satisfied within the budget ceiling.

---

### Signal 4 — Integration Complexity (max 15 pts)

**Columns used:** `3yrs_return`, `opm`

**What it checks:**
Can InnovaTech realistically integrate this company within the 6-month mandate?

**Why stock return proxies integration complexity:**
A company whose stock has returned 100%+ over 3 years is in a high-growth phase. Its team is scaling rapidly, its processes are being built on the fly, its culture is probably fast-moving and chaotic. These companies are exciting but genuinely harder to integrate quickly. The 6-month timeline is aggressive for a high-velocity target.

A stable, steady-growth company has established processes, a settled team, and predictable operations — easier to absorb within the mandate.

**Scoring (base from 3yr return):**

| 3yr Return | Base Points | Interpretation |
|------------|-------------|---------------|
| Negative (stock declining) | 8 | Possible distress — different kind of complexity |
| < 30% | 15 | Stable — integration manageable in 6 months |
| 30% – 60% | 10 | Moderate velocity — feasible with careful planning |
| 60% – 100% | 5 | High velocity — 6-month timeline is challenging |
| > 100% | 2 | Very high velocity — timeline is very aggressive |

**OPM penalty (applied on top of base):**

| OPM | Penalty | Reason |
|-----|---------|--------|
| Negative | -3 pts | Loss-making companies need operational fixes post-acquisition |
| < 5% | -2 pts | Thin margins require margin improvement work |
| ≥ 5% | 0 pts | No additional complexity |

**Final signal score = max(0, base - penalty)**

**Why this is the smallest signal (15 pts)?**
Integration complexity is the most subjective of the four signals. The 3yr return proxy is an indirect measure — a company could have high returns for many good reasons that don't imply chaos. It deserves weight but not so much that it overrides the harder financial constraints.

---

## Deal Structure Calculator

The `get_deal_structure()` function goes beyond scoring — it calculates the actual deal structure for every company.

**Standard structure (deal ≤ Rs. 180 Cr):**
```
Cash Component  = min(Deal × 60%, Rs. 108 Cr)
Equity Swap     = Deal - Cash Component
Earn-Out        = 0
Non-Cash %      = Equity / Deal × 100  (always ≥ 40%)
```

**Stretch structure (deal Rs. 180–216 Cr):**
```
Cash Component  = Rs. 108 Cr (hard ceiling)
Earn-Out        = (Deal - Rs. 180 Cr) × 50%
Equity Swap     = Deal - Cash - Earn-Out
Non-Cash %      = (Equity + Earn-Out) / Deal × 100
```

**Output dictionary:**

```python
{
    'deal_value_cr':  float,   # Total deal value in Rs. Cr
    'cash_cr':        float,   # Cash component
    'equity_cr':      float,   # Equity swap component (InnovaTech shares issued)
    'earnout_cr':     float,   # Earn-out deferred payment (0 for standard deals)
    'dilution_pct':   float,   # InnovaTech shareholder dilution %
    'cash_pct':       float,   # Cash as % of total deal
    'noncash_pct':    float,   # Non-cash as % of total (always >= 40%)
    'feasible':       bool,    # Whether deal fits within Rs. 180 Cr
    'note':           str      # Plain English description of structure type
}
```

**Example — Globtier Infotec:**
```
MCap:          Rs. 41.5 Cr
Deal Value:    Rs. 51.9 Cr   (41.5 × 1.25)
Cash:          Rs. 31.1 Cr   (60%)
Equity Swap:   Rs. 20.8 Cr   (40%)
Earn-Out:      Rs. 0 Cr
Non-Cash:      40%            (meets minimum requirement)
Dilution:      1.08%          (well below 5% threshold)
Feasible:      Yes
```

This output feeds directly into **Deck Slide 12** (Deal Structure).

---

## Column Reference

| Column | Cleaned Name | Used In | Notes |
|--------|-------------|---------|-------|
| Market Cap | `mar_cap_rscr` | S1, S3, Deal Structure | Core constraint column |
| P/E Ratio | `p_e` | S2 | 81 originally missing — median filled |
| 3yr Stock Return | `3yrs_return` | S4 | 98 originally missing — median filled |
| Operating Margin | `opm` | S4 penalty | Used for integration complexity adjustment |
| Sector | `sector` | Not scored | Used by Synergy Engine, not Feasibility |

All column names come from `data/column_map.txt` generated by `data_loader.py`.

---

## Function Reference

| Function | Input | Output | Used By |
|----------|-------|--------|---------|
| `compute_feasibility_score(row)` | dict or Series | float 0–100 | M7 scoring pipeline |
| `get_feasibility_label(score)` | float | str | Dashboard, deck |
| `get_feasibility_reasons(row)` | dict or Series | list of str | Dashboard deep dive |
| `get_feasibility_breakdown(row)` | dict or Series | dict | Dashboard deep dive |
| `get_deal_structure(row)` | dict or Series | dict | Dashboard, deck Slide 12 |

**Importing in M7:**
```python
from engines.feasibility_engine import (
    compute_feasibility_score,
    get_feasibility_label,
    get_feasibility_reasons,
    get_feasibility_breakdown,
    get_deal_structure
)
```

**Scoring a full DataFrame:**
```python
df['feasibility_score'] = df.apply(compute_feasibility_score, axis=1)
df['feasibility_label'] = df['feasibility_score'].apply(get_feasibility_label)
```

**Getting deal structure for top target:**
```python
row = df.iloc[0].to_dict()
deal = get_deal_structure(row)
print(f"Deal: Rs.{deal['deal_value_cr']}Cr")
print(f"Cash: Rs.{deal['cash_cr']}Cr ({deal['cash_pct']}%)")
print(f"Equity: Rs.{deal['equity_cr']}Cr")
print(f"Dilution: {deal['dilution_pct']}%")
```

---

## How It Fits Into the Final Score

The Feasibility Engine contributes **25%** to the final Attractiveness Score:

```
Attractiveness = 0.40 × (100 - Risk Score)
               + 0.35 × Synergy Score
               + 0.25 × Feasibility Score
```

**Why 25% (lowest weight)?**

Feasibility is a hard constraint, not a preference. A company either fits the budget or it does not. The scoring within the feasible range (0–100) reflects how cleanly the deal can be structured, but the main work of feasibility is binary — pass the budget gate or fail.

Risk (40%) and Synergy (35%) have higher weights because they involve genuine degrees of quality. Two feasible companies at Rs. 50 Cr and Rs. 150 Cr are both feasible — the Rs. 150 Cr one scores slightly lower on feasibility but both can be acquired. The bigger question is which one is financially safer and more strategically aligned.

**Score contribution range:**
- Best feasibility score (100) contributes: 0.25 × 100 = **25 points** to attractiveness
- Worst feasibility score (0) contributes: 0.25 × 0 = **0 points** to attractiveness
- Maximum swing: **25 points** (versus 40 points for risk, 35 for synergy)

---

## Running the Engine

**Standalone (self-test + real data):**
```bash
python engines/feasibility_engine.py
```

**What you see:**
1. Self-test on 4 dummy companies (Easy / Tight / Stretch / Not Feasible) with PASS/FAIL
2. Full signal breakdown with visual bar for each test case
3. Deal structure output for each test case
4. Real dataset scoring — distribution across 4 feasibility categories
5. Top 10 most feasible IT companies with scores, market caps, and P/E ratios

**Expected self-test results:**
```
Easy Deal       : score 70+   Highly Feasible            [PASS]
Tight Deal      : score 50-69 Feasible with Structuring  [PASS]
Stretch Target  : score 30-49 Stretch Target             [PASS]
Not Feasible    : score 0-29  Not Feasible               [PASS]
```

**Expected real data results:**
```
Highly Feasible          (70+)  : ~45 companies
Feasible with Structuring(50-69): ~50 companies
Stretch Target           (30-49): ~200 companies
Not Feasible             (0-29) : ~105 companies
```

---

## Example Outputs

### Globtier Infotec — Best Case (Highly Feasible)

```
Score      : 87.0/100  -  Highly Feasible

Signal Breakdown:
  Budget Fit      (max 40)    40 pts  |########################################|
  P/E Valuation  (max 25)    20 pts  |####################.................... |
  Equity Dilution (max 20)   16 pts  |################................        |
  Integration     (max 15)   15 pts  |###############                         |
  Total                       91 pts

Deal Structure:
  Deal Value     : Rs. 51.9 Cr
  Cash Component : Rs. 31.1 Cr  (60%)
  Equity Swap    : Rs. 20.8 Cr
  Non-Cash Total : 40%  (minimum required: 40%)
  Dilution       : 1.08%  (target: below 5%)
  Feasible       : Yes

Reasons:
  - Deal value Rs.51.9Cr is well within the Rs.180Cr budget - comfortable headroom.
  - P/E of 18.0x is below InnovaTech's 24.5x - acquisition is EPS accretive.
  - Equity swap of Rs.20.8Cr causes only 1.08% dilution - negligible impact.
  - 3yr stock return of 12.0% - stable company, integration manageable within 6 months.
```

### LargeCorp — Worst Case (Not Feasible)

```
Score      : 0.0/100  -  Not Feasible

Signal Breakdown:
  Budget Fit      (max 40)     0 pts  |........................................|
  P/E Valuation  (max 25)      4 pts  |####....................................|
  Equity Dilution (max 20)     3 pts  |###.....................................|
  Integration     (max 15)     2 pts  |##......................................|
  Total                         9 pts

Deal Structure:
  Deal Value     : Rs. 6,250 Cr
  Note           : Not feasible within Rs.180Cr budget - shown for reference only

Reasons:
  - Deal value Rs.6250.0Cr significantly exceeds Rs.180Cr budget - not feasible.
  - 3yr stock return of 120.0% - very high velocity, 6-month timeline is very aggressive.
  - Equity swap causes dilution above 5% threshold - may face shareholder resistance.
  - P/E of 35.0x significantly above InnovaTech's 24.5x - dilutive acquisition.
```

---

## Common Questions

**Q: Why does a company with Rs. 0 market cap get 0 points on Signal 1?**
Data quality issue — the row has missing or zero market cap data. The engine returns 0 for budget fit and flags it in the reason string. These companies are usually also flagged as `data_limited` by the data loader.

**Q: Can a company score 100 on feasibility?**
Theoretically yes — a company with very low market cap (deal well under Rs. 126 Cr), P/E below 10x, negligible dilution, and stable stock return could score close to 100. In practice, such a company would also raise questions about why it is so cheaply valued — which the Risk Engine would investigate.

**Q: What if the non-cash percentage comes out below 40%?**
This cannot happen in the engine. The cash component is always `min(deal × 60%, Rs. 108 Cr)`. For any deal under Rs. 180 Cr, this formula automatically produces a 40% non-cash floor. The constraint is structurally enforced, not just checked.

**Q: Why does Signal 4 give 8 points for declining stock (negative 3yr return)?**
A declining stock indicates a company that may be in distress or going through restructuring. This is a different kind of integration complexity from a high-growth company — it is not necessarily harder to integrate, but it comes with its own operational risks. 8 points reflects genuine uncertainty rather than assuming it is easy (15 pts) or very hard (2 pts).

**Q: How does the earn-out work in the stretch structure?**
For deals in the Rs. 180–216 Cr range, the engine defers 50% of the excess above Rs. 180 Cr as an earn-out tied to performance milestones. This keeps the upfront outlay within budget while giving the target's founders a path to receive the full valuation if they hit agreed targets post-acquisition. Slide 12 in the deck details the specific earn-out milestones for the chosen target.

---

*RISKFERA AI — Feasibility Engine (M5) — Built for InnovaTech Systems M&A Hackathon*
