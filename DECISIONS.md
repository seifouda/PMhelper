# PMhelper Edu — Key Technical Decisions

| #   | Decision                 | Answer                                                 | Date       |
| --- | ------------------------ | ------------------------------------------------------ | ---------- |
| 1   | CPM vs EVM task model    | Separate classes. `EVMTask.cpm_task_id` optional link. | 2026-03-08 |
| 2   | Monte Carlo location     | New `core/monte_carlo_edu.py`                          | 2026-03-08 |
| 3   | Data model base class    | `@dataclass` with manual validation                    | 2026-03-08 |
| 4   | MC threading model       | `threading.Thread` + `queue.Queue`                     | 2026-03-08 |
| 5   | PV spreading default     | Uniform. Front/Back are PG-only features.              | 2026-03-08 |
| 6   | Shared state pattern     | Single `EduProjectState` passed to all tabs            | 2026-03-08 |
| 7   | Which EAC feeds VAC/TCPI | EAC₁ default. All 3 computed. User selects primary.    | 2026-03-08 |
| 8   | One FastAPI app, not two | `server/main.py` is the only app. `server/api/main.py` deleted. | 2026-07-15 |
| 9   | PERT three-point estimates | Required. No defaulting from `duration`.               | 2026-07-15 |
| 10  | API docs exposure        | Swagger at `/api/docs`, DEBUG-gated. Off in production. | 2026-07-15 |

## Notes on 8–10

**8 — One FastAPI app.** There were two `app` objects, both introduced by the same
squashed commit (`d6c50c7`); no doc or commit ever justified the split. Only
`server/main.py` was deployed (`Dockerfile`, `render.yaml`), so `projects`,
`analysis`, and `selection` were reachable only via an undocumented second
uvicorn command — while the server tests imported *that* app, and so tested
something Docker never ran. `api/main.py`'s request logging, global exception
handler, and `/api/version` were ported over; its `/debug/info` was dropped
because it read four `config` attributes that no longer exist and would
`AttributeError` whenever `DEBUG=True`.

> Two constraints worth remembering: new `include_router` calls **must** go above
> the SPA catch-all `@app.get("/{full_path:path}")`, or FastAPI's
> registration-order matching makes them silently return `index.html`. And
> `web.py`'s rate-limited endpoints resolve the limiter via `app.state.limiter`,
> which only `server/main.py` sets up.
>
> ⚠️ This put `/api/projects/*` CRUD and the DB layer on the public Render deploy
> for the first time. Accepted deliberately; worth a security pass.

**9 — PERT estimates required.** PERT derives `TE = (O + 4M + P)/6` and
`Var = ((P − O)/6)²` from the three-point estimates; without them there is no
PERT, only CPM. They had been optional, so a request validated, returned `202`,
then died in the background with `unsupported operand type(s) for *: 'int' and
'NoneType'` — a client error surfacing as a dead job. Now a `422` naming the
missing field.

Defaulting `O = M = P = duration` was considered and rejected: it makes every
variance `0`, σ `0`, and **P(on time) always `1.0`**. For a teaching tool that
silently presents a PERT model with no uncertainty at all — a confident-looking
answer that is exactly the wrong lesson. Failing loudly teaches the right one.

**10 — Docs gated.** Swagger/ReDoc live at `/api/docs` and `/api/redoc` and only
when `DEBUG` is on, so the API surface isn't publicly readable now that project
CRUD is exposed. The deleted app served them unconditionally at `/docs`;
`config.get_docs_url()` still pointed there and was a dead link.
