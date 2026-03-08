# PMhelper Edu — Manual UI Smoke Test Checklist

**Version:** 1.0  
**Date:** Phase 6  
**Purpose:** 20-item manual verification before release. Run against `python -m pmhelper.edu_main`.

---

## Pre-requisites

- Python 3.10+ with `tkinter`, `matplotlib`, `numpy` installed
- Demo files present in `src/pmhelper/demos_edu/`

---

## Checklist

| #   | Area            | Test                                                             | Pass |
| --- | --------------- | ---------------------------------------------------------------- | ---- |
| 1   | Launch          | App starts without errors; main window with tab bar visible      | ☐    |
| 2   | File → New      | File → New Project creates empty project; title bar shows "New"  | ☐    |
| 3   | File → Open     | File → Open loads a `.pmproj` file; data appears in tabs         | ☐    |
| 4   | File → Save     | File → Save writes to disk; dirty flag clears; title bar updates | ☐    |
| 5   | File → SaveAs   | File → Save As prompts for path; saves correctly                 | ☐    |
| 6   | Load Demo UG    | File → Load Demo → UG loads Office Renovation; 8 tasks visible   | ☐    |
| 7   | Load Demo PG    | File → Load Demo → PG loads Software Dev; 12 tasks visible       | ☐    |
| 8   | Mode Toggle     | Mode → UG hides Probability & RCPS tabs; PG shows them           | ☐    |
| 9   | Input Tab       | Task table populates; add/edit/delete rows works                 | ☐    |
| 10  | Input Tab       | Period table populates; add/edit/delete rows works               | ☐    |
| 11  | EVM Tab KPIs    | KPI cards show CPI, SPI, CV, SV, EAC, TCPI with RAG colours      | ☐    |
| 12  | EVM Tab Curve   | S-Curve chart renders PV, EV, AC lines with shaded region        | ☐    |
| 13  | EVM Walkthrough | Click a KPI card → walkthrough panel shows formula/subs/result   | ☐    |
| 14  | Risk Tab        | Risk register table shows risks; CRUD (add/edit/delete) works    | ☐    |
| 15  | Risk Matrix     | Heat map renders 5×5 grid with numbered risk circles             | ☐    |
| 16  | Gantt Tab       | Gantt chart renders task bars; Set/Reset Baseline works          | ☐    |
| 17  | Gantt Tracking  | Check "Tracking" toggle → shows baseline vs current bars         | ☐    |
| 18  | Probability     | Run MC (N=1000) → histogram + percentile lines appear            | ☐    |
| 19  | Dashboard       | Dashboard shows KPI strip, mini S-curve, risk summary            | ☐    |
| 20  | Export Charts   | File → Export All Charts → folder created with PNG files         | ☐    |

---

## Unsaved-Changes Guard

| #   | Test                                                  | Pass |
| --- | ----------------------------------------------------- | ---- |
| 21  | Modify data → close window → prompted "Save changes?" | ☐    |
| 22  | Answer "No" → window closes without saving            | ☐    |
| 23  | Answer "Cancel" → window stays open                   | ☐    |
| 24  | Answer "Yes" → file saved, then window closes         | ☐    |

---

## Mode-Specific Behaviour

| #   | Test                                                               | Pass |
| --- | ------------------------------------------------------------------ | ---- |
| 25  | In UG mode: EAC₃ and TCPI hidden on KPI cards                      | ☐    |
| 26  | In UG mode: Probability and RCPS tabs hidden                       | ☐    |
| 27  | In PG mode: All KPI cards visible; Probability + RCPS tabs visible | ☐    |
| 28  | Switch UG → PG → tabs appear; PG → UG → tabs hide                  | ☐    |

---

## Edge Cases (Manual)

| #   | Test                                                               | Pass |
| --- | ------------------------------------------------------------------ | ---- |
| 29  | Empty project → EVM tab shows "No data" or 0-value cards, no crash | ☐    |
| 30  | Delete all risks → Risk tab shows empty table, no crash            | ☐    |

---

**Total items:** 30  
**Tester:** ******\_\_\_******  
**Date tested:** ******\_\_\_******  
**Result:** \_\_\_ / 30 passed
