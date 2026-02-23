SECTOR_FIT_MAP = {
    'it - software':    100,   # Core — directly aligns with InnovaTech's AI/product goals
    'it - services':    100,   # Core — same transformation direction
    'fintech':           80,   # High — IT as strong enabler, recurring revenue potential
    'telecom - services':60,   # Medium — software + infrastructure overlap
    'telecom - equipments':45, # Lower — hardware focus, less synergy
    'finance':           40,   # Adjacent — possible but weak tech synergy
    'power':             25,   # Weakest — energy sector, IT is peripheral
}
```

**Why:** InnovaTech's stated goal is to strengthen its AI and software product portfolio. A target in IT-Software or IT-Services is directly aligned with that. A Power company might use some IT but it's not a technology transformation play. The sector score is a 0–100 number that feeds into the synergy score weighted at 20%.

---

### `p_e` — Price to Earnings Ratio
**Used in:** Feasibility Engine (Signal 2 — P/E attractiveness, 25 points)
**Also used in:** Valuation slide in the deck

**How it's used:**
```
InnovaTech's own P/E = 24.5x

If target P/E < 24.5x  →  buying cheaper than InnovaTech is valued
                        →  acquisition is EPS accretive
                        →  shareholders of InnovaTech benefit

If target P/E > 24.5x  →  buying more expensive than InnovaTech trades
                        →  acquisition is EPS dilutive unless synergies offset
```

**Scoring:**
```
P/E ≤ 0 or missing   →  10 pts  (can't assess, partial credit)
P/E < 15             →  25 pts  (undervalued — very attractive entry)
P/E < 24.5           →  18 pts  (below InnovaTech's own multiple — accretive)
P/E < 35             →   8 pts  (slightly expensive)
P/E ≥ 35             →   0 pts  (overvalued — dilutive acquisition)
```

**Why 24.5 as the threshold:** This is InnovaTech's own P/E from the brief. It's the single most important valuation benchmark. If InnovaTech acquires a company at a lower P/E than it trades at, every rupee of the target's earnings is worth more to InnovaTech's shareholders than it costs to buy. This is the definition of an accretive deal.

**81 companies have missing P/E** — these are typically loss-making companies where P/E is undefined. The engine gives them partial credit rather than penalizing them fully.

---

### `mar_cap_rscr` — Market Capitalisation (Rs. Crore)
**Used in:** Feasibility Engine (Signal 1 — Budget check, 40 points)
**Also used in:** Deal structure calculation, valuation slide

**This is the most important feasibility signal.** The entire ₹180 Cr acquisition constraint depends on this column.

**How it's used:**
```
Implied Deal Value = Market Cap × 1.25
(25% acquisition premium is standard for Indian IT M&A)

If Implied Deal Value ≤ ₹126 Cr (70% of budget)  →  40 pts  comfortable
If Implied Deal Value ≤ ₹180 Cr                   →  25 pts  fits with structuring
If Implied Deal Value ≤ ₹216 Cr (120% of budget)  →  10 pts  stretch, earn-out needed
Above ₹216 Cr                                      →   0 pts  hard fail
```

**Why 25% premium:** In Indian IT M&A, acquirers typically pay 20–35% above the current market price to get shareholders to agree to sell. 25% is the conservative midpoint. You're not paying exactly market cap — you're paying market cap plus a control premium.

**Your data:** Market cap ranges from ₹2.58 Cr to ₹12,19,675 Cr. 142 companies fall within the ₹180 Cr budget. The giants like TCS and Infosys are automatically eliminated by this signal.

---

### `div_yld` — Dividend Yield (%)
**Used in:** Risk Engine (Signal 5 — Distress proxy, 5 points)

**How it's used:**
```
Dividend Yield > 8%          →  5 pts risk added
                                 (suspiciously high = possible value trap —
                                  stock price has fallen sharply, pushing
                                  yield up artificially)

Dividend Yield = 0 AND OPM < 5%  →  3 pts risk added
                                      (no dividend + thin margins = possible
                                       cash burn or financial stress)

Otherwise                    →  0 pts risk added
```

**Why it's a distress signal:** A normally healthy company pays 1–3% dividend yield. When yield jumps above 8%, it usually means the stock price has crashed — not that the company suddenly became more generous. That stock price crash happened for a reason. Combined with thin operating margins, it suggests a company under financial pressure.

**It's only 5 points** because dividend yield alone is weak evidence. It needs to be combined with other signals before you act on it. That's why it's the smallest weight in the Risk Engine.

---

### `np_qtr_rscr` — Net Profit, Quarterly (Rs. Crore)
**Used in:** Derived column calculation in M2
**Indirectly used in:** Valuation (via `annual_profit_est`)

**Direct formula:**
```
annual_profit_est = np_qtr_rscr × 4
```

**Why:** This is the raw quarterly profit figure. Every valuation method needs annual profit. P/E valuation in the deck is:
```
Equity Value = annual_profit_est × P/E Multiple
             = (np_qtr_rscr × 4) × Multiple
```

You use this in Slide 11 (Valuation Band) to calculate the Conservative / Base / Bull case values for your chosen target.

---

### `qtr_profit_var` — Quarterly Profit Variance (%)
**Used in:** Risk Engine (Signal 1 — Earnings instability, 30 points — highest weight)

**How it's used:**
```
This is the percentage change in profit from the previous quarter.

|Variance| > 50%   →  30 pts risk  (extreme swing — earnings wildly unpredictable)
|Variance| > 25%   →  15 pts risk  (significant volatility)
|Variance| > 10%   →   5 pts risk  (mild fluctuation)
Otherwise          →   0 pts risk  (stable)
```

**Why absolute value:** A company whose profit jumped +60% one quarter is just as risky from a predictability standpoint as one whose profit fell -60%. Both suggest the business is volatile and hard to value. What you want for an acquisition target is consistency — steady, predictable earnings that you can build a valuation model around.

**Why this carries the highest weight (30 points):** This is the most direct measure of earnings reliability available in your dataset. InnovaTech has moderate risk appetite — they cannot afford to acquire a company whose earnings swing wildly quarter to quarter, because that makes post-acquisition integration and synergy planning extremely difficult.

---

### `sales_qtr_rscr` — Sales, Quarterly (Rs. Crore)
**Used in:** Derived column calculation in M2
**Indirectly used in:** Valuation (via `annual_revenue_est`)

**Direct formula:**
```
annual_revenue_est = sales_qtr_rscr × 4
```

**Why:** Same reason as profit — valuations need annual revenue. EV/Sales multiple method in the deck is:
```
EV = annual_revenue_est × Revenue Multiple
   = (sales_qtr_rscr × 4) × Multiple (2x / 3x / 4x)
```

Also used in the summary to compare target's scale against InnovaTech's ₹610 Cr annual revenue.

---

### `qtr_sales_var` — Quarterly Sales Variance (%)
**Used in:** Not directly in engine scoring
**But useful for:** Sanity checking. If a company has high quarterly profit variance but low sales variance, profits are moving independently of revenue — which is a red flag suggesting cost manipulation or one-off items inflating profits.

You can optionally add this as a bonus risk signal if you want to strengthen the Risk Engine. For now it's in the dataset as context.

---

### `roce` — Return on Capital Employed (%)
**Used in:** Synergy Engine (Signal 1 — ROCE alignment, 25% weight — highest weight)

**Formula:**
```
ROCE Score = min(100, (target ROCE / InnovaTech ROCE) × 100)
           = min(100, (target ROCE / 22.1) × 100)
```

**Examples:**
```
Target ROCE = 22.1%  →  Score = 100  (matches InnovaTech exactly)
Target ROCE = 11.0%  →  Score =  50  (half InnovaTech's efficiency)
Target ROCE = 33.0%  →  Score = 100  (capped at 100, better than benchmark)
Target ROCE =  5.0%  →  Score =  23  (very low capital efficiency)
```

**Why ROCE is the most important synergy signal:** InnovaTech's strategic goal is to shift to a high-margin, capital-efficient, product-led business. ROCE directly measures capital efficiency — how much profit the company generates per rupee of capital employed. A target with high ROCE is already operating the kind of lean, efficient business model InnovaTech wants to build. A target with low ROCE would drag down InnovaTech's overall capital efficiency post-acquisition.

InnovaTech's own ROCE improved from 18.2% (FY23) to 22.1% (FY25) — this upward trend is the benchmark. Any acquisition should maintain or improve this trajectory.

---

### `opm` — Operating Profit Margin (%)
**Used in:** Both Risk Engine (Signal 4, 15 points) AND Synergy Engine (Signal 2, 25% weight)

**This is the only column used in two different engines.**

**In Risk Engine — measuring financial stress:**
```
OPM < 0%   →  15 pts risk  (operating at a loss — fundamental problem)
OPM < 3%   →  10 pts risk  (razor thin — one bad quarter wipes out profit)
OPM < 7%   →   5 pts risk  (below average — some concern)
OPM ≥ 7%   →   0 pts risk  (healthy)
```

**In Synergy Engine — measuring margin alignment:**
```
OPM Score = min(100, (target OPM / InnovaTech OPM) × 100)
          = min(100, (target OPM / 12.8) × 100)
```

**Why it appears in both:** OPM tells two different stories depending on context. In the Risk Engine, very low OPM is a danger signal — the company is barely profitable at the operating level. In the Synergy Engine, OPM above InnovaTech's own 12.8% means the target actually improves InnovaTech's group margins post-acquisition, which is strategically valuable.

---

### `sales_var_3yrs` — Sales Variance over 3 Years (%)
**Used in:** Synergy Engine (Signal 3 — Revenue growth momentum, 20% weight)

**Formula:**
```
Growth Score = min(100, max(0, (sales_var_3yrs / 20.0) × 100))
```

**Why 20% as the benchmark:** InnovaTech's own revenue CAGR from FY23 to FY25 is 20.5%. The idea is that an acquisition target should be growing at least as fast as InnovaTech itself. A target growing at 20%+ scores 100. A target growing at 10% scores 50. A target with declining revenue scores 0.

**Why revenue growth matters for synergy:** InnovaTech's goal is to accelerate growth through acquisition. If the target is already growing fast, it brings momentum into the combined entity. If it's shrinking, InnovaTech is buying a declining business that will drag down the combined revenue growth rate — the opposite of the acquisition thesis.

---

### `profit_var_3yrs` — Profit Variance over 3 Years (%)
**Used in:** Risk Engine (Signal 2 — Long term profit trend, 25 points)

**Formula:**
```
pv3 < -20%   →  25 pts risk  (profits down more than 20% over 3 years — serious structural decline)
pv3 < -10%   →  15 pts risk  (moderate decline)
pv3 <   0%   →   8 pts risk  (any decline is a mild flag)
pv3 ≥   0%   →   0 pts risk  (stable or growing — no flag)
```

**Why this is different from quarterly profit variance:** Quarterly variance measures short-term volatility. 3-year variance measures long-term direction. A company can have stable quarterly earnings while profits are slowly declining year over year — the quarterly signal won't catch this but the 3-year signal will. You need both to get a complete picture of earnings quality.

**84 companies have this missing** — the median fill handles these but they get flagged as `data_limited`.

---

### `3yrs_return` — 3 Year Stock Return (%)
**Used in:** Feasibility Engine (Signal 4 — Integration complexity proxy, 15 points)

**Formula:**
```
3yr return < 30%   →  15 pts feasibility  (stable company — integration manageable in 6 months)
3yr return < 60%   →   8 pts feasibility  (moderate growth — integration doable)
3yr return ≥ 60%   →   3 pts feasibility  (high velocity company — risky to integrate quickly)
```

**Why stock return proxies integration complexity:** A company whose stock has tripled in 3 years is in a high-growth phase. Its team is scaling fast, its processes are changing rapidly, its culture is probably chaotic. Integrating such a company within InnovaTech's 6-month mandate is genuinely harder than integrating a stable, steady-growth company. This is an indirect signal but a reasonable proxy given the data available.

**98 companies have this missing** — the most missing column in your dataset.

---

### `roe_3yr` — 3 Year Return on Equity (%)
**Used in:** Not directly in engine scoring
**But useful for:** Deck slide 10 (Financial Assessment) when comparing InnovaTech vs. target. ROE measures how efficiently a company uses shareholder equity to generate profit. High ROE combined with high ROCE is a strong signal of a well-run business.

You can mention it in the target's financial profile in the deck even though it doesn't feed into the score.

---

### `ebidt_var_3yrs` — EBITDA Variance over 3 Years (%)
**Used in:** Risk Engine (Signal 3 — EBITDA consistency, 20 points)

**Formula:**
```
ebidt3 < -15%   →  20 pts risk  (EBITDA down 15%+ over 3 years — core operations weakening)
ebidt3 <  -5%   →  12 pts risk  (moderate erosion)
ebidt3 <   0%   →   5 pts risk  (any decline — mild flag)
ebidt3 ≥   0%   →   0 pts risk  (EBITDA growing — no flag)
```

**Why EBITDA specifically:** EBITDA (Earnings Before Interest, Tax, Depreciation, Amortisation) is the best proxy for cash generated by the core business operations. Unlike net profit, it removes financing decisions (interest), tax structures (tax), and accounting choices (depreciation). If EBITDA is declining over 3 years, the core business is genuinely getting weaker — not just affected by how the company is financed or how the accountants handle depreciation.

**Why this is separate from profit variance:** A company can have growing net profit but declining EBITDA if it's benefiting from tax breaks or reducing depreciation. Using both signals together catches situations where the headline profit looks good but the underlying operational performance is deteriorating.

---

### `eps_var_3yrs` — EPS Variance over 3 Years (%)
**Used in:** Risk Engine (Signal 6 — EPS trend, 5 points) AND Synergy Engine (Signal 5 — EPS momentum, 10% weight)

**In Risk Engine — detecting value destruction:**
```
eps3 < -20%  →  5 pts risk  (EPS down 20%+ over 3 years)
eps3 <   0%  →  2 pts risk  (any EPS decline)
eps3 ≥   0%  →  0 pts risk  (EPS growing or stable)
```

**In Synergy Engine — measuring earnings momentum:**
```
EPS Score = min(100, max(0, (eps_var_3yrs / 20) × 100))
```

**Why EPS matters beyond just profit:** EPS (Earnings Per Share) accounts for share dilution. A company can grow total profit while issuing so many new shares that each share is worth less. Declining EPS over 3 years means the company is either losing money or diluting shareholders — neither is good for InnovaTech's acquisition thesis.

**Why it appears in both engines:** Similar to OPM — declining EPS is a risk flag, but growing EPS is a synergy positive. A company with strong EPS growth is creating per-share value momentum that InnovaTech's shareholders benefit from post-acquisition.

---

## Summary Table — Every Column, Every Engine
```
COLUMN               RISK ENGINE    SYNERGY ENGINE    FEASIBILITY ENGINE    DECK/OTHER
───────────────────────────────────────────────────────────────────────────────────────
sno                  -              -                 -                     -
name                 -              -                 -                     Display only
sector               -              Signal 4 (20%)    -                     Deck context
p_e                  -              -                 Signal 2 (25pts)      Valuation slide
mar_cap_rscr         -              -                 Signal 1 (40pts)      Deal structure
div_yld              Signal 5 (5pts)-                 -                     -
np_qtr_rscr          -              -                 -                     annual_profit_est
qtr_profit_var       Signal 1 (30pts)-                -                     -
sales_qtr_rscr       -              -                 -                     annual_revenue_est
qtr_sales_var        -              -                 -                     Context only
roce                 -              Signal 1 (25%)    -                     Deck slide 10
opm                  Signal 4 (15pts)Signal 2 (25%)   -                     Deck slide 10
sales_var_3yrs       -              Signal 3 (20%)    -                     -
profit_var_3yrs      Signal 2 (25pts)-                -                     -
3yrs_return          -              -                 Signal 4 (15pts)      -
roe_3yr              -              -                 -                     Deck slide 10
ebidt_var_3yrs       Signal 3 (20pts)-                -                     -
eps_var_3yrs         Signal 6 (5pts)Signal 5 (10%)    -                     -
───────────────────────────────────────────────────────────────────────────────────────
annual_revenue_est   -              -                 -                     Valuation slide
annual_profit_est    -              -                 -                     Valuation slide
profit_margin_est    -              -                 -                     Deck slide 10
data_limited         -              -                 -                     Dashboard badge
