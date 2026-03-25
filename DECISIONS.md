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
