 What is Risk Engine ?
  The Risk Engine answers one question: can we trust this company's financial performance?


Before InnovaTech spends ₹180 Cr acquiring a company, the most important thing to verify is whether the financial numbers are stable, honest, and sustainable. A company can look attractive on paper but be hiding deteriorating fundamentals underneath. The Risk Engine is designed to catch exactly that.

It produces a single number between 0 and 100 for every company. Higher score means higher risk. This is the opposite direction from Synergy and Feasibility — those are higher is better. Risk is higher is worse. That is why in the final formula it gets inverted: 0.40 × (100 - risk_score).


Why Risk carries the highest weight (40%)
InnovaTech has a moderate risk appetite — stated explicitly in the hackathon brief. They are a mid-cap company with ₹95 Cr cash reserves. One bad acquisition could genuinely damage their balance sheet and derail their entire transformation programme.

Synergy and feasibility are both important but they are recoverable mistakes. If you overestimate synergies, you work harder post-acquisition to find them. If the deal is slightly expensive, you restructure the payment. But if you acquire a company with fundamentally unreliable earnings — one that was hiding losses, had a one-quarter profit spike that never repeated, or was in structural decline — there is no recovery. You have bought a problem.
Risk is the quality gate. Everything else comes after it.

The 6 Signals and Why These Specific Ones
The Risk Engine uses 6 signals. Each was chosen because it is available in dataset AND it measures a genuinely distinct dimension of financial risk.
 They are not redundant each one catches something the others cannot.
Signal 1 — Quarterly Profit Variance — 30 points
Column: qtr_profit_var
What it measures: How much did this company's profit swing in the most recent quarter compared to the previous one?
Why it's the biggest signal: This is the most immediate, real-time indicator of earnings instability. If a company's quarterly profit jumped 200% or crashed 80%, something unusual is happening. Either the business is genuinely volatile — dependent on large one-off contracts, seasonal, or cyclically exposed — or the reported numbers are being managed. Either way it is a red flag for an acquirer.
The logic:
Absolute variance > 100%  →  30 pts  extreme — profit more than doubled or nearly wiped out
Absolute variance > 50%   →  20 pts  severe — significant instability
Absolute variance > 25%   →  10 pts  elevated — some concern
Absolute variance > 10%   →   4 pts  mild — worth noting
Otherwise                 →   0 pts  stable — no flag
Why absolute value: A company whose profit jumps +150% is as hard to value as one whose profit falls -150%. Both are unpredictable. What you need for a successful acquisition is consistency — earnings you can model and forecast.

Signal 2 — 3 Year Profit Variance — 25 points
Column: profit_var_3yrs
What it measures: Has this company's overall profit grown or shrunk over the past 3 years?
Why it's the second biggest signal: While Signal 1 catches short-term volatility, Signal 2 catches long-term direction. A company can have perfectly stable quarterly earnings while its annual profits are slowly declining year over year. Signal 1 would give it a clean score. Signal 2 would flag it.
This is structural risk — the risk that the business model itself is deteriorating. Maybe competition is intensifying, maybe pricing power is weakening, maybe key clients are leaving. Whatever the reason, a company whose profits have declined over 3 years is heading in the wrong direction.
The logic:
Profit down more than 20% over 3 years  →  25 pts  serious structural decline
Profit down more than 10%               →  15 pts  moderate concern
Any profit decline at all               →   8 pts  mild flag
Profit flat or growing                  →   0 pts  no flag
Why only negative variance triggers risk: Growing profits are not a risk signal. You only add risk points when profits are falling. A company that grew profits 50% over 3 years gets 0 risk points on this signal — that is a good thing.

Signal 3 — EBITDA Variance over 3 Years — 20 points
Column: ebidt_var_3yrs
What it measures: Has the core operational profitability of this business strengthened or weakened over 3 years?
Why it's separate from profit variance: This is the most important distinction in the Risk Engine. Net profit can be manipulated through accounting choices — depreciation schedules, tax optimisation, interest structuring, one-off gains. EBITDA strips all of that out and shows you the raw cash-generating power of the core business operations.
A company can show growing net profit while its EBITDA is declining. This happens when:

They are reducing depreciation charges (an accounting choice, not real improvement)
They got a one-off tax benefit that won't repeat
They raised debt to make acquisitions that boosted reported profit but weakened operations

If EBITDA is declining while net profit is growing, the company is potentially window dressing its financials. This is a serious red flag for an acquirer doing pre-deal screening.
The logic:
EBITDA down more than 15% over 3 years  →  20 pts  core operations weakening seriously
EBITDA down more than 5%                →  12 pts  moderate erosion
Any EBITDA decline                      →   5 pts  mild flag
EBITDA flat or growing                  →   0 pts  no flag

Signal 4 — Operating Profit Margin — 15 points
Column: opm
What it measures: What percentage of revenue actually becomes operating profit?
Why this matters for risk: Low operating margin means the company is operating close to breakeven. A thin-margin business has almost no buffer against adversity. A small revenue decline, a cost increase, or a client loss can push it into operating losses instantly. For an acquirer, this means you are buying a fragile business — one bad quarter post-acquisition could make it a net drain on InnovaTech's resources.
The logic:
OPM negative (operating loss)  →  15 pts  fundamental problem
OPM < 3%                       →  10 pts  razor thin — extremely fragile
OPM < 7%                       →   5 pts  below average — some concern
OPM ≥ 7%                       →   0 pts  healthy operating margin
Why 7% as the healthy threshold: InnovaTech's own OPM is 12.8%. Any company operating below roughly half of InnovaTech's own margin is considered to have margin risk. 7% is the minimum that suggests a viable, sustainable business.

Signal 5 — Dividend Yield — 5 points
Column: div_yld
What it measures: How much dividend does the company pay relative to its stock price?
Why high dividend yield is a risk signal: This is counterintuitive. Normally a dividend sounds positive. But a very high dividend yield — above 8% — almost always means the stock price has fallen sharply, not that the company suddenly became more generous. Yield = Dividend / Stock Price. If the stock price crashes, the yield spikes. That stock crash happened for a reason.
An 8%+ dividend yield in the Indian IT/tech space is a strong indication that the market has lost confidence in the company. Combined with other risk signals, it supports a picture of financial distress.
The logic:
Dividend yield > 8%  →  5 pts  possible value trap — stock price has crashed
Otherwise            →  0 pts  normal
Why only 5 points: Dividend yield alone is weak evidence. A company with 9% yield might simply be a mature, cash-generative business that pays high dividends by policy. This signal only adds meaningful weight when it is combined with other negative signals — Signal 1 or 2 already adding points. It is a confirming signal, not a primary one.

Signal 6 — EPS Variance over 3 Years — 5 points
Column: eps_var_3yrs
What it measures: Has earnings per share grown or shrunk over 3 years?
Why EPS is different from profit: A company can grow total net profit while issuing so many new shares that each individual share is worth less. This happens through equity financing, ESOP grants, or acquisitions paid in stock. EPS accounts for share dilution — if EPS is falling while profit is growing, the company is creating value for the company but destroying it for each individual shareholder.
For InnovaTech, this matters because part of the deal structure involves an equity swap — issuing InnovaTech shares in exchange for the target. If the target has a history of EPS dilution, it suggests loose capital management that could continue post-acquisition.
The logic:
EPS down more than 20% over 3 years  →  5 pts  value destruction per share
Any EPS decline                      →  2 pts  mild flag
EPS flat or growing                  →  0 pts  no flag
Why only 5 points: Like dividend yield, EPS decline alone is not conclusive. Some high-growth companies deliberately dilute EPS by issuing shares to fund expansion — Amazon did this for years while creating enormous value. It only becomes a risk flag when combined with other signals pointing the same direction.

How the Total Score Works
The 6 signals add up to a maximum of 100 points:
Signal 1  Quarterly Profit Variance    30 pts
Signal 2  3 Year Profit Variance       25 pts
Signal 3  3 Year EBITDA Variance       20 pts
Signal 4  Operating Profit Margin      15 pts
Signal 5  Dividend Yield                5 pts
Signal 6  EPS 3 Year Variance           5 pts
─────────────────────────────────────────────
Total                                 100 pts
A company that triggers every signal at maximum gets 100 — extremely high risk. A company that triggers nothing gets 0 — very low risk.
Risk Labels:
0  – 20   Low Risk        (safe to proceed, focus on synergy and feasibility)
21 – 40   Moderate Risk   (some flags, investigate specific signals)
41 – 60   Elevated Risk   (significant concerns, needs due diligence)
61 – 100  High Risk       (avoid or deprioritise heavily)

How It Feeds Into the Final Score
In the Final Scoring formula:
Attractiveness = 0.40 × (100 - risk_score) + 0.35 × synergy + 0.25 × feasibility
A company with risk score 80 contributes only 0.40 × 20 = 8 to attractiveness from the risk component. A company with risk score 10 contributes 0.40 × 90 = 36. This 28-point swing is larger than what any single synergy or feasibility signal can produce — which is exactly the intention. Risk is the dominant filter.

What the Engine Outputs
For every company in the dataset, the Risk Engine produces:

risk_score — the 0 to 100 number
risk_label — Low / Moderate / Elevated / High Risk
risk_breakdown — dictionary showing exactly how many points each signal contributed
risk_reasons — 2 to 3 plain English sentences explaining the score, written for a CFO not a data scientist

The reasons are important for the dashboard and the deck. A judge should be able to look at the deep dive panel for any company and immediately understand why it scored the way it did without doing any mental arithmetic.