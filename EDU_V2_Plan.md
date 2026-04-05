# PMhelper Edu — V2 Implementation Plan

> **Scope:** Desktop app refinements, web app shipping, new analysis features, educational enhancements
> **Approach:** 1 developer + AI agent assistance
> **Date:** April 5, 2026
> **Last Status Update:** April 5, 2026
> **Predecessor:** [EDU_V1_Plan.md](EDU_V1_Plan.md) — code-complete as of March 25, 2026
> **Branch:** TBD (will branch from `feat/web-v1` or `production` after merge)

---

## V2 Vision

V1 delivered a complete desktop PM teaching tool (20 phases, 797+ tests) and an Angular web front-end (28/28 tests, production build ready). V2 focuses on three tracks:

1. **Ship Track** — Merge the web app, deploy to Render, complete the release pipeline
2. **Desktop Track** — Address accumulated adjustments, validation improvements, and manual QA
3. **Feature Track** — New analysis capabilities and educational enhancements

---

## Phase 0 — V1 Carry-Forward & QA (Week 1)

> **Goal:** Complete all deferred V1 items before starting new work.
> **Priority:** P0 — nothing else starts until this is done.

| # | Task | What to Do | Effort | Status |
|---|------|------------|--------|--------|
| 0.1 | Merge PR #3 (`feat/web-v1` → `production`) | Resolve any conflicts, ensure CI green, merge | 0.5 day | ⬜ |
| 0.2 | Set `RENDER_DEPLOY_HOOK_URL` GitHub secret | Render dashboard → Deploy Hook URL → GitHub Secrets | 15 min | ⬜ |
| 0.3 | Update `render.yaml` branch to `production` | Commit to production after merge | 15 min | ⬜ |
| 0.4 | Verify live deploy on Render | Hit `/health`, test PG guard, load sample data | 0.5 day | ⬜ |
| 0.5 | Run 30-item UI smoke test (desktop) | Execute `UI_SMOKE_TEST_CHECKLIST_EDU.md` | 0.5 day | ⬜ |
| 0.6 | PyInstaller `--onedir` build + test | Build on clean machine, test launch without Python | 0.5 day | ⬜ |
| 0.7 | Test interactive network viewer (600 tasks) | Load large demo, open in browser, verify zoom/pan | 0.25 day | ⬜ |
| 0.8 | Update CHANGELOG.md | Add `[1.0.0-web]` entry for web features | 0.25 day | ⬜ |
| 0.9 | Tag `v1.0.0-web` + GitHub Release | Annotated tag, release notes | 0.25 day | ⬜ |
| 0.10 | Document rollback plan in README | "To roll back: revert merge on production" | 15 min | ⬜ |

---

## Phase 1 — Desktop App Adjustments (Weeks 2–3)

> **Goal:** Address usability issues, validation gaps, and UX polish in the desktop Tkinter app.
> **Priority:** P1 — user has stated "a lot of adjustments in the app."
> **Note:** Specific tasks TBD — user will provide the adjustment list. Placeholder structure below.

| # | Task | What to Do | Effort | Status |
|---|------|------------|--------|--------|
| 1.1 | _User-defined adjustment 1_ | TBD | TBD | ⬜ |
| 1.2 | _User-defined adjustment 2_ | TBD | TBD | ⬜ |
| 1.3 | _User-defined adjustment 3_ | TBD | TBD | ⬜ |
| 1.4 | _User-defined adjustment 4_ | TBD | TBD | ⬜ |
| 1.5 | _User-defined adjustment 5_ | TBD | TBD | ⬜ |

### Known Desktop Issues (from V1 review)

These can be scheduled into Phase 1 once the user provides their adjustment list:

- Charter tab template selection dialog not fully implemented (`charter_tab.py:172`)
- API return type inconsistency (some functions return dicts, others tuples)
- Database health check stub (`main.py:142`)
- `calculations.py:58` placeholder logic

---

## Phase 2 — Web Hardening (Weeks 3–4)

> **Goal:** Security, performance, and test coverage for the Angular web app.
> **Carried from:** V1 Phase 19.16–19.20

| # | Task | What to Do | Priority | Status |
|---|------|------------|----------|--------|
| 2.1 | Add CSP `Report-Only` header | Middleware in `main.py`; surface violations without breaking fonts | P2 | ⬜ |
| 2.2 | Align `PersistenceService` signal coverage | Persist all 16 signals (match `ProjectIOService`) or document the gap | P2 | ⬜ |
| 2.3 | Add Angular budgets to `angular.json` | `maximumWarning: 500kb`, `maximumError: 1mb` for initial bundle | P3 | ⬜ |
| 2.4 | True E2E Cypress user-flow spec | Add activities → Analyze → verify Network nodes → verify Gantt bars | P3 | ⬜ |
| 2.5 | Lighthouse CI gate in GitHub Actions | Performance budget assertions in CI | P3 | ⬜ |
| 2.6 | Cross-browser testing | Verify Chrome, Firefox, Safari, Edge | P2 | ⬜ |
| 2.7 | Responsive design audit | Test on 1366×768, tablets, mobile viewports | P2 | ⬜ |

---

## Phase 3 — EVM Web Features (Weeks 4–6)

> **Goal:** Bring the full EVM calculation engine to the web UI.
> **Status:** Python engine exists (V1 Phase 2); Angular components are stubs.

| # | Task | What to Do | Effort | Status |
|---|------|------------|--------|--------|
| 3.1 | Period-by-period PV/EV/AC data entry | Weekly/monthly selector, editable grid, Compute PV button | 2 days | ⬜ |
| 3.2 | EVM KPI cards (all 13 KPIs) | CV, SV, CPI, SPI, PC, PS, CR, EAC₁/₂/₃, VAC, TCPI with RAG badges | 2 days | ⬜ |
| 3.3 | Earned Value S-Curve chart | D3.js: PV/EV/AC cumulative lines, overrun shading | 1.5 days | ⬜ |
| 3.4 | Cumulative SPI/CPI trend chart | D3.js: period-over-period trend lines | 1 day | ⬜ |
| 3.5 | Step-by-step EVM walkthrough | KaTeX formula rendering, substitution, interpretation | 1.5 days | ⬜ |
| 3.6 | Earned Schedule (ES) + SV(t) | New calculation + chart | 2 days | ⬜ |

---

## Phase 4 — Risk Analysis Web Features (Weeks 6–7)

> **Goal:** Full risk register and analysis in the web app.

| # | Task | What to Do | Effort | Status |
|---|------|------------|--------|--------|
| 4.1 | Risk register CRUD | Add/edit/delete risks, category, probability, impact, exposure | 1.5 days | ⬜ |
| 4.2 | 5×5 Risk heat map (D3.js) | Interactive, click-to-detail, colour-coded | 1.5 days | ⬜ |
| 4.3 | Aggregate risk exposure + contingency | Total RE, flagging, contingency reserve calc | 0.5 day | ⬜ |
| 4.4 | Risk-adjusted EAC formula | Integrate risk exposure into EAC forecasting | 1 day | ⬜ |
| 4.5 | Risk probability distribution chart | Histogram from Monte Carlo risk outcomes | 1 day | ⬜ |

---

## Phase 5 — Report Generation (Weeks 7–8)

> **Goal:** Exportable project performance reports from both desktop and web.

| # | Task | What to Do | Effort | Status |
|---|------|------------|--------|--------|
| 5.1 | Printable PDF report (desktop) | All KPIs + key charts + risk summary in one document | 2 days | ⬜ |
| 5.2 | Web-based PDF export | Browser-side PDF generation with charts rendered to canvas | 2 days | ⬜ |
| 5.3 | Excel report template | Configurable report layout: KPI sheet, chart sheet, raw data sheet | 1.5 days | ⬜ |
| 5.4 | PowerPoint export | Summary slide deck with charts and KPI cards | 2 days | ⬜ |

---

## Phase 6 — Advanced Analysis Features (Weeks 8–10)

> **Goal:** New analytical capabilities for PG-level students.

| # | Task | What to Do | Effort | Status |
|---|------|------------|--------|--------|
| 6.1 | Sensitivity analysis | Parameter impact assessment on project KPIs | 2 days | ⬜ |
| 6.2 | Probabilistic critical path | Distribution of which tasks appear on critical path (from MC data) | 1.5 days | ⬜ |
| 6.3 | NPV / ROI calculations | Project financial viability metrics | 1 day | ⬜ |
| 6.4 | Cost-time trade-off curve | Crashing optimization frontier visualisation | 1.5 days | ⬜ |
| 6.5 | Monte Carlo P50/P90 finish date chart | Percentile chart refinement from MC results | 1 day | ⬜ |

---

## Phase 7 — Educational Enhancements (Weeks 10–12)

> **Goal:** Strengthen the learning experience.

| # | Task | What to Do | Effort | Status |
|---|------|------------|--------|--------|
| 7.1 | Glossary / knowledge base | Searchable PM term definitions, linked from tooltips | 2 days | ⬜ |
| 7.2 | Worked solutions for Risk + SWOT | Extend Phase 11 step generator to new analysis types | 1.5 days | ⬜ |
| 7.3 | Interactive tutorial mode | Guided walkthrough for first-time users | 2 days | ⬜ |
| 7.4 | Practice calculator | Standalone formula calculator for students to practice EVM KPIs | 1.5 days | ⬜ |
| 7.5 | Additional demo datasets | Industry-specific scenarios (construction, IT, healthcare) | 1 day | ⬜ |

---

## Phase 8 — Infrastructure & Quality (Ongoing)

> **Goal:** Code quality, performance, and maintainability improvements.

| # | Task | What to Do | Priority | Status |
|---|------|------------|----------|--------|
| 8.1 | Code signing certificate for `.exe` | OV cert from Sectigo/DigiCert (~$70/yr) | P2 | ⬜ |
| 8.2 | Performance benchmarking suite | Automated timing for large project operations | P3 | ⬜ |
| 8.3 | API return type standardisation | All engine functions return typed dataclasses | P3 | ⬜ |
| 8.4 | Async Monte Carlo (web) | Replace threading with async/await for web backend | P2 | ⬜ |
| 8.5 | Database health check endpoint | Implement stub at `main.py:142` | P3 | ⬜ |

---

## V2 Roadmap (from CHANGELOG.md)

These are longer-term goals tracked for context but not scheduled into specific phases yet:

| Feature | Target | Status |
|---------|--------|--------|
| Portfolio Management (multi-project dashboard) | V2.1+ | ⬜ Planning |
| Collaborative Features (multi-user editing) | V2.2+ | ⬜ Planning |
| Predictive ML (duration estimation from history) | V3 | ⬜ Research |
| Mobile Applications (iOS/Android) | V3 | ⬜ Research |

---

## Key Decisions Log (V2)

| # | Decision | Answer | Reasoning |
|---|----------|--------|-----------|
| 1 | Start from `feat/web-v1` or `production`? | TBD — depends on PR #3 merge | If merged, branch from `production`; if not, continue on `feat/web-v1` |
| 2 | Desktop adjustments scope? | TBD — awaiting user input | User has "a lot of adjustments" to specify |
| 3 | Web auth for V2? | No | Single-user educational tool; defer auth to V2.1+ with multi-user |

---

## Definition of Done (V2 Release)

- [ ] All V1 deferred items completed (Phase 0)
- [ ] Desktop adjustments from user list implemented and tested
- [ ] Web app deployed and live on Render
- [ ] CSP headers enabled (at least Report-Only)
- [ ] 30-item UI smoke test passed (desktop)
- [ ] Cross-browser testing passed (web)
- [ ] PyInstaller bundle tested on clean machine
- [ ] All new features have unit tests
- [ ] CHANGELOG.md updated
- [ ] GitHub Release tagged
