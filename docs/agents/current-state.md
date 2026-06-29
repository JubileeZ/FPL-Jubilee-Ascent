# Current Implementation State

Read if no prior context. `ROADMAP.md` shows target; this file shows what exists today.

**Active phase:** Phase 1 — Repo Infrastructure & Foundations.

---

## What exists

<!-- AGENT: Document implemented areas/directories at a high level.
     (Keep this map high-level; list directories/modules, NOT individual files to save tokens).
     Table format:
     | Area | Path | Notes |
     |------|------|-------|
     | Config | `config/` | Basic loaders and env vars |
-->

| Area | Path | Notes |
|------|------|-------|
| Project Scaffold | `AGENTS.md`, `ROADMAP.md`, `CONTEXT.md` | Configuration, roadmap, vocabulary |
| Dependencies | `pyproject.toml`, `.venv/` | Package configuration via uv |
| API Clients | `clients/fpl_api.py`, `clients/fpl_auth.py` | Inbound request handlers and JWT Playwright/tiered login |
| Data Dictionary | `docs/data_dictionary.md` | Mapping from raw API fields to flat files |

---

## What does NOT exist yet (do not assume)

<!-- AGENT: Document planned items not on disk yet. Prevents assuming files exist.
     | Item | Planned phase | Notes |
     |------|---------------|-------|
     | DB models | 2 | SQLAlchemy models and connection |
-->

| Item | Planned phase | Notes |
|------|---------------|-------|
| CLI Commands | 2-4 | Scripts for refreshing, snapshotting, modeling, backtesting, solving |
| Custom Models | 3 | ML and rolling average baseline models conforming to contract |
| Features & Projections | 3 | Data converters for FeatureContract and ProjectionContract |
| Backtesting engine | 3 | Simulation loop and metrics generator |
| Vendored Solver | 4 | Port of open-fpl-solver modules |

---

## Safe commands today

<!-- AGENT: Provide exact working commands runnable safely right now. -->

```bash
uv run ruff check .        # Lint code (after writing scripts)
uv run pytest              # Run pytest
```

---

## Agent pitfalls

<!-- AGENT: Document temporary/phase pitfalls (unbuilt components, mocked APIs). Permanent traps go in AGENTS.md.
     1. Avoid importing X without Y.
     2. Ask human before migrations.
-->

- <!-- AGENT: fill in or remove -->

---

## Doc map

| Question | Read |
|----------|------|
| Glossary | `CONTEXT.md` |
| Phases & checklist | `ROADMAP.md` |
| Agent rules | `AGENTS.md` |
| How to update progress | `docs/agents/progress.md` |
