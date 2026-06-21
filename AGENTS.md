# FPL Jubilee Ascent
# Read by all AI agents (Claude, Gemini, Cursor, Copilot, etc.) working in this repo.
---

## Project Identity

FPL analytics and optimization engine for a single user. Ingests live FPL API data, engineers predictive features, generates per-player per-gameweek xP projections via configurable statistical or ML models, and solves for the optimal 15-man squad and transfer plan using MILP. Optionally augments projections with LLM-sourced factors (rotation risk, injury context) before solving.

**Stack:** Python 3.12 · uv · FastAPI · Next.js 14 · PostgreSQL · SQLAlchemy · PuLP · pandas · scikit-learn

**Monorepo:** yes

---

## Key Commands

| Command | What it does |
|---------|-------------|
| `uv sync` | Install backend deps |
| `cd frontend && npm install` | Install frontend deps |
| `uv run ruff check .` | Lint (backend) |
| `cd frontend && npm run lint` | Lint (frontend) |
| `uv run pytest` | Test (backend) |
| `cd frontend && npm run test` | Test (frontend) |
| `uv run uvicorn app.main:app --reload` | Run backend dev server |
| `cd frontend && npm run dev` | Run frontend dev server |

**Pre-commit gate:** agents must run test and lint commands and confirm both pass before proposing any commit.

---

## Repo Structure

```
backend/
  app/
    api/          # FastAPI route handlers
    models/       # Pydantic schemas and ORM models
    services/     # business logic (projection, blending, MILP)
    clients/      # all external API calls (FPL API, LLM tool)
    db/           # migrations and connection setup
  tests/          # mirrors app/ structure
frontend/
  src/
    app/          # Next.js App Router pages
    components/   # UI components (squad view, charts, dashboard)
    lib/          # API client, utils
tools/
  llm_tool/       # MCP server or CLI script for LLM factor generation
data/
  cache/          # Parquet files for historical FPL data (gitignored)
docs/             # ADRs and architecture notes
.env.example      # copy to .env, never commit .env
```

---

## Off-Limits: Never Touch Without Explicit Instruction

- `.env` and any file containing secrets or credentials
- Database migrations — always flag, never auto-apply or auto-run
- Production configuration files
- Any file marked `# DO NOT EDIT` or `# GENERATED`
- `data/cache/` — never overwrite or delete Parquet files autonomously; treat as append-only
- `tools/llm_tool/` — never modify LLM tool contract (input/output schema) without explicit instruction
- `backend/app/db/migrations/` — flag all migration changes, never auto-apply
- `VENDOR.lock` — never modify; pin is intentional

---

## Safety Rules

**Universal (keep always):**
- Never commit secrets, tokens, or credentials to any file.
- Destructive operations (delete, overwrite, truncate, drop) require an inline comment:
  `# DESTRUCTIVE: <reason this is safe to proceed>`
- Never add a new top-level dependency without flagging it explicitly in your response.
- Prefer reversible actions. When an irreversible action is required, state it clearly before executing.

**Project-specific:**
- All external API calls must go through `backend/app/clients/` — never inline.
- Never mutate raw FPL API response data — always write to a new transformed output.
- Tests must not make real network calls — use fixtures or mocks.
- LLM tool output must always be validated against the defined contract schema before being passed to the blender.
- `llm_weight` must never be hardcoded — always read from config or env.

---

## Code Conventions

- Type hints required on all public functions and class attributes.
- All service functions return Pydantic models, not raw dicts or bare values.
- No bare `except:` — always catch specific exception types.
- Projection blending logic lives exclusively in `backend/app/services/` — never in route handlers.
- LLM factor schema defined in `backend/app/models/` — treat as the single source of truth.

---

## Known Footguns

- `uv run` is required — do not call `python` directly, the venv won't activate.
- LLM tool must be called before the MILP solver — calling it after produces no effect on squad selection.
- `llm_weight=0.0` disables LLM blending but the tool may still be invoked — check the flag before calling the tool.
- Never use `sed -i` for file edits — use `.tmp` + `mv` atomic write pattern for BSD/GNU cross-platform compatibility.

---

## MCP / Tool Access

- `tools/llm_tool/` MCP server active — use for LLM factor generation only, not general reasoning.
- FPL API client available via `backend/app/clients/` — read-only, no write endpoints exist.
- No internet access in test environment — all external calls must use fixtures.

---

## Agent Behavior Overrides

- PuLP, pandas, XGBoost, scikit-learn, and Next.js are pre-approved dependencies; do not flag them as new.

---

## Agent skills

### Issue tracker

Issues and PRDs are tracked via GitHub Issues in this repository using the `gh` CLI. Pull requests are not treated as a request surface. See `docs/agents/issue-tracker.md`.

### Triage labels

The default label mapping (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`) is used. See `docs/agents/triage-labels.md`.

### Domain docs

The repository uses a single-context layout with one global `CONTEXT.md` and `docs/adr/` at the repository root. See `docs/agents/domain.md`.
