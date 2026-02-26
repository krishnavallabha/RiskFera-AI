COL_ROCE      = 'roce'
COL_OPM       = 'opm'
COL_SALES_3YR = 'sales_var_3yrs'
COL_EPS_3YR   = 'eps_var_3yrs'
COL_SECTOR    = 'sector'
```


---

## The Complete Logic — How Each Score is Calculated

---

### Signal 1 — ROCE Score

**What you have in your data:** `roce` column — a percentage number like `22.1` or `8.5` or `31.0`

**What you need to produce:** a score between 0 and 100

**The math:**
```
roce_score = (target's ROCE / InnovaTech's ROCE) × 100
           = (target's ROCE / 22.1) × 100

BUT cap it at 100 — no score above 100 is allowed
AND floor it at 0 — no negative scores
```

**Walk through examples:**
```
Target ROCE = 22.1  →  (22.1 / 22.1) × 100 = 100   Perfect match
Target ROCE = 11.0  →  (11.0 / 22.1) × 100 = 49.8  Half as efficient
Target ROCE = 44.2  →  (44.2 / 22.1) × 100 = 200   → capped to 100
Target ROCE = 0     →  (0 / 22.1) × 100    = 0     Zero efficiency
```

**In plain English:** How close is this company to InnovaTech's own efficiency? If it matches or beats InnovaTech, full marks. If it's half as efficient, half marks.

---

### Signal 2 — OPM Score

**What you have:** `opm` column — a percentage like `12.8` or `3.0` or `18.5`

**Same logic as ROCE, different benchmark:**
```
opm_score = (target's OPM / InnovaTech's OPM) × 100
          = (target's OPM / 12.8) × 100

Cap at 100, floor at 0
```

**Examples:**
```
Target OPM = 12.8  →  100   Exactly matches InnovaTech
Target OPM = 6.4   →  50    Half InnovaTech's margins
Target OPM = 25.6  →  200   → capped to 100
Target OPM = 2.0   →  15.6  Very thin margins, low score
Target OPM = -5.0  →  0     Operating at a loss, floored to 0
```

---

### Signal 3 — Sales Growth Score

**What you have:** `sales_var_3yrs` column — a percentage like `25.0` or `-8.0` or `45.0`

**The benchmark is 20%** — InnovaTech's own 3-year revenue growth
```
growth_score = (target's 3yr sales growth / 20.0) × 100

Cap at 100, floor at 0
```

**Examples:**
```
sales_var_3yrs = 20   →  (20/20) × 100 = 100   Matches InnovaTech's growth
sales_var_3yrs = 10   →  (10/20) × 100 = 50    Growing, but half InnovaTech's pace
sales_var_3yrs = 40   →  (40/20) × 100 = 200   → capped to 100
sales_var_3yrs = 0    →  0                      No growth at all
sales_var_3yrs = -15  →  negative → floored to 0   Shrinking company
```

**Key difference from ROCE/OPM:** A company with NEGATIVE sales growth gets 0, not a negative score. The floor matters here because shrinking companies all get the same 0 — you're not trying to rank how badly they're shrinking, just that they fail this signal.

---

### Signal 4 — Sector Score

**What you have:** `sector` column — a text value like `"IT - Software"` or `"Finance"` or `"Power"`

**This one is NOT a formula.** It's a lookup table:
```
"it - software"       →  100
"it - services"       →  100
"fintech"             →   80
"telecom - services"  →   60
"telecom - equipments"→   45
"finance"             →   40
"power"               →   25
anything else         →   30  (default — unknown sector)
```

**The tricky part:** Your data might have `"IT - Software"` with capital letters and spaces. The code converts everything to lowercase before looking it up. So `"IT - Software"` becomes `"it - software"` before the lookup.

**Important:** Check what your actual sector values look like in the dataset. Run `df['sector'].unique()` to see all unique values. If your data has `"IT Services"` instead of `"IT - Services"`, the lookup will fail and return the default 30. You may need to add extra entries to the map.

---

### Signal 5 — EPS Score

**What you have:** `eps_var_3yrs` column — a percentage like `22.0` or `-15.0` or `8.0`

**The benchmark is 20** — a "good" EPS growth rate
```
eps_score = (target's eps_var_3yrs / 20) × 100

Cap at 100, floor at 0
```

**Examples:**
```
eps_var_3yrs = 20   →  100   Strong EPS growth
eps_var_3yrs = 10   →  50    Moderate growth
eps_var_3yrs = -5   →  0     EPS declining, floored to 0
eps_var_3yrs = 50   →  250   → capped to 100
```

---

## Combining Everything — The Final Score

After you have all 5 sub-scores (each 0-100), the final score is a weighted average:
```
final_score = (roce_score   × 0.25)
            + (opm_score    × 0.25)
            + (growth_score × 0.20)
            + (sector_score × 0.20)
            + (eps_score    × 0.10)
```

The weights add up to 1.0 (100%), so the result is automatically between 0 and 100.

---

## The Label Logic

After getting the final score, convert it to a human-readable label:
```
score >= 75  →  "🟢 High Synergy"
score >= 55  →  "🟡 Moderate Synergy"
score >= 35  →  "🟠 Low Synergy"
score < 35   →  "🔴 Misaligned"
```

---

## The Reasons Logic

This is the part that explains WHY a company got its score. It checks each signal and generates a human-readable sentence:
```
For ROCE:
  if target ROCE >= 22.1  →  "✅ ROCE 25.0% meets InnovaTech's 22.1% benchmark"
  if target ROCE < 22.1   →  "⚠️ ROCE 8.0% below InnovaTech's 22.1% benchmark"

For OPM:
  if target OPM >= 12.8   →  "✅ Margin 15.0% aligned with InnovaTech's 12.8% profile"
  if target OPM < 12.8    →  "⚠️ Margin 5.0% below InnovaTech — may dilute group margins"

For Sales Growth:
  if sales_var_3yrs >= 15  →  "✅ 3-year revenue growth of 25% — strong momentum"
  if sales_var_3yrs < 0    →  "⚠️ Revenue declined 8% over 3 years"
  (between 0-15 — no reason generated, it's neither good nor bad enough)

For Sector:
  if sector_score >= 80    →  "✅ Sector 'IT Software' is core to InnovaTech's goals"
  if sector_score < 50     →  "ℹ️ Sector 'Power' is adjacent — synergy requires effort"
```

---

## The Complete Flow Visualized
```
One row of your dataset (one company)
           │
           ▼
    Read 5 columns:
    roce, opm, sales_var_3yrs, eps_var_3yrs, sector
           │
           ▼
    Convert each to a 0-100 score:
    roce_score, opm_score, growth_score, sector_score, eps_score
           │
           ▼
    Weighted average:
    final_score = (25% × roce) + (25% × opm) + (20% × growth)
                + (20% × sector) + (10% × eps)
           │
           ▼
    Label:  🟢 / 🟡 / 🟠 / 🔴
           │
           ▼
    Reasons: List of ✅ / ⚠️ / ℹ️ sentences explaining why
```

---

## Your Exact Coding Checklist

When you sit down to code, do it in this order:

**Step 1** — Fix the 5 column name constants at the top of the file

**Step 2** — Code `compute_synergy_score()`:
- Read roce, opm, sales_var_3yrs, eps_var_3yrs, sector from the row using `_n()`
- Calculate each of the 5 sub-scores using the formulas above
- Combine with weights
- Return the rounded result

**Step 3** — Code `get_synergy_label()`:
- Simple if/elif chain on the score
- Return the right emoji string

**Step 4** — Code `get_synergy_reasons()`:
- Read the same 5 values again
- Check each condition
- Append the right sentence to a reasons list
- Return the list

**Step 5** — Run the self-test at the bottom and check the 3 test cases give expected scores

---

## One Thing That Will Confuse You — The `_n()` Helper

Your dataset has missing values (NaN — "Not a Number"). If you try to do math on NaN, Python crashes. The `_n()` function is just a safety wrapper:
```
_n(row, 'roce')  
→ tries to read row['roce']
→ if it's missing or NaN → returns 0.0 instead of crashing