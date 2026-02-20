<div align="center">

```
██████╗ ██╗███████╗██╗  ██╗███████╗███████╗██████╗  █████╗
██╔══██╗██║██╔════╝██║ ██╔╝██╔════╝██╔════╝██╔══██╗██╔══██╗
██████╔╝██║███████╗█████╔╝ █████╗  █████╗  ██████╔╝███████║
██╔══██╗██║╚════██║██╔═██╗ ██╔══╝  ██╔══╝  ██╔══██╗██╔══██║
██║  ██║██║███████║██║  ██╗██║     ███████╗██║  ██║██║  ██║
╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝
```

### **AI-Powered M&A Target Screening for InnovaTech Systems**
*Smarter acquisitions start before the banker's deck arrives.*

<br/>

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org)
[![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com)
[![License](https://img.shields.io/badge/License-MIT-F4B942?style=for-the-badge)](LICENSE)

<br/>

> Built for the **M&A AI Hackathon** · Round 2 Submission
> Acquirer: **InnovaTech Systems Ltd** · Budget: **₹180 Cr**

</div>

---

## 📌 What is RISKFERA?

Traditional M&A deal sourcing is broken. It relies on banker networks, manual filtering, and gut feel — and it never answers the two questions that matter most before a deal is signed:

> *"Can we trust this company's financial performance?"*
> *"Is this company actually aligned with our strategic goals?"*

**RISKFERA AI** fixes this. It's an intelligent screening system that runs a universe of acquisition targets through three quantitative engines — Risk, Synergy, and Feasibility — and outputs a ranked shortlist with plain-English reasoning, before due diligence even begins.

Built specifically for **InnovaTech Systems Ltd**, a mid-cap Indian IT firm transitioning to a product-led, AI-enabled, recurring revenue model with a ₹180 Cr acquisition budget and a mandate for deals that close in 6 months.

---

## 🏗️ System Architecture

```
dataset.xlsx  (Multi-sector NSE companies)
      │
      ▼
 data_loader.py ──────────────────────► cleaned_targets.csv
      │
      ├──── 🔴 Risk Engine ────────────► Earnings Quality Score  (0–100)
      │         Quarterly Profit Variance
      │         3-Year Profit & EBITDA Trend
      │         Operating Margin Health
      │         EPS Momentum
      │
      ├──── 🟢 Synergy Engine ─────────► Strategic Fit Score     (0–100)
      │         ROCE vs InnovaTech Benchmark
      │         OPM Alignment
      │         Revenue Growth (3yr)
      │         Sector Strategic Fit
      │         EPS Momentum
      │
      └──── 🔵 Feasibility Engine ─────► Deal Viability Score    (0–100)
                Market Cap vs ₹180Cr Budget
                P/E vs InnovaTech 24.5x
                Equity Swap Dilution
                Integration Complexity
                      │
                      ▼
            ┌─────────────────────────────┐
            │  ATTRACTIVENESS SCORE       │
            │                             │
            │  0.40 × (100 − Risk)        │
            │  0.35 × Synergy             │
            │  0.25 × Feasibility         │
            └─────────────────────────────┘
                      │
                      ▼
            Ranked Shortlist + Streamlit Dashboard
```

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🔴 **Risk Engine** | Flags earnings manipulation, profit instability, and margin deterioration using 6 financial signals derived from available dataset columns |
| 🟢 **Synergy Engine** | Scores strategic alignment against InnovaTech's real FY2025 benchmarks — ROCE 22.1%, OPM 12.8%, revenue CAGR 20.5% |
| 🔵 **Feasibility Engine** | Hard-checks the ₹180 Cr budget constraint, equity swap dilution (<5% target), P/E accretiveness, and 6-month integration complexity |
| 📊 **Live Dashboard** | Streamlit app with real-time re-ranking when acquisition budget slider changes |
| 🎯 **Deal Structure Output** | Auto-calculates Cash / Equity Swap / Earn-Out split for every company (60/40 minimum non-cash constraint enforced) |
| 💬 **Plain-English Reasons** | Every ranking comes with 3 human-readable bullet points — built for CFOs, not data scientists |
| ♻️ **Config-Driven** | Swap `config.py` with any acquirer's real financials → entire model re-calibrates instantly |

---

## 🚀 Quickstart

### 1. Clone the repo

```bash
git clone https://github.com/your-team/riskfera-ai.git
cd riskfera-ai
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your dataset

Place the provided `dataset.xlsx` file in the `data/` folder:

```
data/
└── dataset.xlsx   ← put it here
```

### 4. Clean and process the data

```bash
python data_loader.py
```

This will:
- Standardize all column names
- Compute derived metrics (annualized revenue, profit margin)
- Generate `data/cleaned_targets.csv`
- Print a `data/column_map.txt` showing original → cleaned column name mappings

> ⚠️ **Check `data/column_map.txt` after this step.** If your dataset uses different column names, update the `COL_*` constants at the top of each engine file to match.

### 5. Run the scoring model

```bash
python scoring/final_score.py
```

This scores every company across all three engines and prints the **Top 5 Acquisition Targets** to the terminal. Output saved to:
- `output/ranked_targets.csv` — full ranked list
- `output/top5_targets.csv` — top 5 shortlist

### 6. Launch the dashboard

```bash
streamlit run dashboard/app.py
```

Opens at `http://localhost:8501`

---

## 📁 Project Structure

```
riskfera-ai/
│
├── 📄 config.py                    # InnovaTech profile & all acquisition constraints
├── 📄 data_loader.py               # Cleans dataset.xlsx → cleaned_targets.csv
├── 📄 requirements.txt
├── 📄 README.md
│
├── 📂 data/
│   ├── dataset.xlsx                # Original dataset (do not modify)
│   ├── cleaned_targets.csv         # Generated by data_loader.py
│   └── column_map.txt              # Generated: original → clean column names
│
├── 📂 engines/
│   ├── risk_engine.py              # Engine 1 — Earnings quality & financial stability
│   ├── synergy_engine.py           # Engine 2 — Strategic fit with InnovaTech
│   └── feasibility_engine.py       # Engine 3 — Deal viability within constraints
│
├── 📂 scoring/
│   └── final_score.py              # Combines engines → Attractiveness Score → ranking
│
├── 📂 output/
│   ├── ranked_targets.csv          # Full ranked output (generated)
│   └── top5_targets.csv            # Top 5 shortlist (generated)
│
├── 📂 dashboard/
│   └── app.py                      # Streamlit dashboard
│
└── 📂 deck/
    ├── RISKFERA_Deck.pptx          # Final submission deck
    └── RISKFERA_Deck.pdf           # PDF backup
```

---

## ⚙️ Configuration

All acquirer parameters live in **`config.py`**. This is the single source of truth — no other file hardcodes numbers.

```python
# config.py — InnovaTech Systems FY2025 (real hackathon brief data)

INNOVATECH = {
    "revenue_cr":           610,     # FY2025
    "net_profit_cr":        78,
    "operating_margin_pct": 12.8,
    "roce_pct":             22.1,
    "market_cap_cr":        1911,    # = 78 × 24.5x P/E
    "current_pe":           24.5,
    ...
}

ACQUISITION_CONSTRAINTS = {
    "max_deal_value_cr":    180,     # Hard ceiling
    "min_noncash_pct":      0.40,    # Min 40% equity swap or earn-out
    "max_cash_outflow_cr":  108,     # = 180 × 0.60
    "max_integration_months": 6,
    "synergy_realization_months": 12,
    ...
}
```

**To re-run for a different acquirer:** Update `INNOVATECH` and `ACQUISITION_CONSTRAINTS` in `config.py`, then re-run `python scoring/final_score.py`.

---

## 🔴 Engine 1 — Risk Engine

**Question:** *Can we trust what this company is reporting?*

Detects earnings instability, structural decline, and financial stress using signals available in the dataset:

| Signal | Column | Max Points | Threshold |
|--------|--------|-----------|-----------|
| Quarterly Profit Variance | `quarterly_profit_variance_pct` | 30 | >50% = max risk |
| 3-Year Profit Trend | `profit_variance_3_years_pct` | 25 | <-20% = max risk |
| 3-Year EBITDA Trend | `ebidt_variance_3_years_pct` | 20 | <-15% = max risk |
| Operating Margin | `operating_profit_margin_pct` | 15 | <0% = max risk |
| Dividend Yield (distress proxy) | `dividend_yield_pct` | 5 | >8% = value trap flag |
| EPS 3-Year Trend | `eps_variance_3_years_pct` | 5 | <-20% = max risk |

Score 0–100. **Higher = riskier.** Applied as `(100 - risk_score)` in the final formula.

```bash
# Test the engine independently
python engines/risk_engine.py
# Expected output: Low~10  Medium~40  High~80+
```

---

## 🟢 Engine 2 — Synergy Engine

**Question:** *Does this company move InnovaTech toward its strategic goals?*

Calibrated against InnovaTech's real FY2025 metrics:

| Signal | Weight | InnovaTech Benchmark |
|--------|--------|---------------------|
| ROCE | 25% | 22.1% (FY2025) |
| Operating Profit Margin | 25% | 12.8% (FY2025) |
| 3-Year Revenue Growth | 20% | ~20.5% CAGR |
| Sector Strategic Fit | 20% | IT/SaaS > Fintech > Telecom > Energy |
| EPS 3-Year Momentum | 10% | ~30% (FY2025 proxy) |

Score 0–100. **Higher = better fit.**

```bash
python engines/synergy_engine.py
# Expected output: High~75+  Medium~50  Low~25
```

---

## 🔵 Engine 3 — Feasibility Engine

**Question:** *Can InnovaTech realistically acquire this company within its constraints?*

Hard constraints baked in from the hackathon brief:

| Signal | Weight | Constraint |
|--------|--------|-----------|
| Market Cap vs ₹180 Cr Budget | 40 pts | Deal = MCap × 1.25 premium |
| P/E vs InnovaTech 24.5x | 25 pts | Buying below 24.5x = EPS accretive |
| Equity Swap Dilution | 20 pts | Target < 5% dilution of ₹1,911 Cr MCap |
| Integration Complexity (3yr return) | 15 pts | Fast-growing firms = harder 6-month integration |

Score 0–100. **Higher = more acquirable.**

```bash
python engines/feasibility_engine.py
# Expected output: Easy~75+  Tight~50  Infeasible~20
```

---

## 📊 Dashboard

The Streamlit dashboard provides four interactive views:

**1. Ranked Table**
Full colour-coded leaderboard. Green/Amber/Red scoring. Updates live when filters change.

**2. Scenario Controls (Sidebar)**
- Acquisition budget slider (₹50–300 Cr) → re-ranks all companies in real time
- Minimum ROCE filter
- Sector checkboxes

**3. Company Deep Dive**
Click any company to see:
- Score breakdown (Risk / Synergy / Feasibility)
- Radar chart (3-axis visual)
- Key financial metrics
- 3 plain-English reasons for the ranking
- Indicative deal structure (Cash / Equity / Dilution %)

**4. Universe Overview**
- Top 5 grouped bar chart comparison
- Score distribution histogram across all targets

```bash
streamlit run dashboard/app.py
```

---

## 📐 Scoring Formula

```
Attractiveness Score =  0.40 × (100 − Risk Score)
                      + 0.35 × Synergy Score
                      + 0.25 × Feasibility Score
```

**Why these weights?**

| Weight | Engine | Rationale |
|--------|--------|-----------|
| 40% | Risk (inverted) | InnovaTech has moderate risk appetite. One bad acquisition derails the transformation programme. Quality gate is the highest priority. |
| 35% | Synergy | The entire acquisition thesis is strategic acceleration — synergy drives post-merger value. |
| 25% | Feasibility | Hard constraint, not a preference. A synergistic target at the edge of budget is still worth flagging for creative structuring. |

---

## 🧪 Running the Test Suite

Each engine includes a self-test that runs on dummy data — no real dataset needed.

```bash
# Test all three engines
python engines/risk_engine.py
python engines/synergy_engine.py
python engines/feasibility_engine.py

# Run the full pipeline end-to-end
python data_loader.py && python scoring/final_score.py
```

Expected test outputs:

```
RISK ENGINE — SELF TEST
──────────────────────────────────────────────────
Low Risk:    12/100  🟢 Low Risk
Medium Risk: 43/100  🟡 Moderate Risk
High Risk:   83/100  🔴 High Risk
✅ Expected: Low~10  Medium~40  High~80+

SYNERGY ENGINE — SELF TEST
──────────────────────────────────────────────────
High Synergy:  78.5/100  🟢 High Synergy
Med Synergy:   51.2/100  🟡 Moderate Synergy
Low Synergy:   24.8/100  🔴 Misaligned
✅ Expected: High~75+  Medium~50  Low~25

FEASIBILITY ENGINE — SELF TEST
──────────────────────────────────────────────────
Easy deal:   80/100  🟢 Highly Feasible
Tight deal:  52/100  🟡 Feasible with Structuring
Infeasible:  18/100  🔴 Not Feasible
✅ Expected: Easy~75+  Tight~50  Infeasible~20
```

---

## 🔧 Troubleshooting

**`KeyError` in any engine**
```bash
cat data/column_map.txt   # Check exact cleaned column names
```
Then update the `COL_*` constants at the top of the relevant engine file.

**`FileNotFoundError: ranked_targets.csv`**
```bash
python data_loader.py       # Must run first
python scoring/final_score.py
```

**`ModuleNotFoundError` in `app.py`**
```python
# Already handled in app.py — but if issues persist:
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
```

**`NaN` values in final scores**
The data loader fills NaNs with column medians. If NaNs persist, check that `data_loader.py` ran successfully and `cleaned_targets.csv` has no blank rows.

**Streamlit port conflict**
```bash
streamlit run dashboard/app.py --server.port 8502
```

---

## 📋 Acquisition Constraints Enforced

All constraints from the hackathon brief are hardcoded in `config.py` and enforced by the Feasibility Engine:

| Constraint | Value | Where Enforced |
|------------|-------|---------------|
| Max acquisition budget | ₹180 Cr | Feasibility Engine Signal 1 |
| Min non-cash payment | 40% of deal value | `get_deal_structure()` output |
| Max cash outflow | ₹108 Cr (= 180 × 60%) | Deal structure calculator |
| Max integration timeline | 6 months | PMI plan in deck |
| Founder retention | 2 years | Deal structure clause |
| Synergy realization | Within 12 months | Deck Slide 9 |

---

## 🗺️ Hackathon Milestones

The project was built using 18 parallel milestones — both team members picked milestones independently and worked simultaneously:

```
M1  Project Setup          ✅   M10 Dashboard Radar        ✅
M2  Data Loader            ✅   M11 Dashboard Top5 Chart   ✅
M3  Risk Engine            ✅   M12 Deck Slides 1–4        ✅
M4  Synergy Engine         ✅   M13 Deck Slides 5–7        ✅
M5  Feasibility Engine     ✅   M14 Deck Slides 8–10       ✅
M6  config.py              ✅   M15 Deck Slides 11–12      ✅
M7  Final Scoring          ✅   M16 Deck Slides 13–15      ✅
M8  Dashboard Table        ✅   M17 Deck Final Polish      ✅
M9  Dashboard Deep Dive    ✅   M18 README + Submit        ✅
```

---

## 👥 Team

Built in 5 effective days for the M&A AI Hackathon.

| | Role |
|-|------|
| **Person A** | Data pipeline · Synergy Engine · Scoring · Deck |
| **Person B** | Risk Engine · Feasibility Engine · Dashboard · Pitch |

---

## ⚠️ Limitations

- Dataset provides quarterly data only; annual figures are approximated as `quarterly × 4`
- Sector classification relies on dataset tagging — nuanced hybrid business models may be mis-scored
- Qualitative factors (management quality, IP strength, culture) are outside current scope
- The Risk Engine flags statistical patterns — it does not infer fraud or legal misconduct
- Isolation Forest anomaly detection is available as an optional enhancement (not enabled by default)

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**RISKFERA AI** · Built for InnovaTech Systems M&A Hackathon

*"We don't find the best company in the market.*
*We find the best company for InnovaTech."*

</div>
