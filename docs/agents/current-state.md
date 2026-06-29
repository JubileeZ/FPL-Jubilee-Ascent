# Current Implementation State

Read if no prior context. `ROADMAP.md` shows target; this file shows what exists today.

**Active phase:** None — all planned infrastructure, modeling, backtesting, and solver phases are implemented.

---

## What exists

| Area | Path | Notes |
|------|------|-------|
| Project Scaffold | `AGENTS.md`, `ROADMAP.md`, `CONTEXT.md` | Configuration, roadmap, vocabulary |
| Dependencies | `pyproject.toml`, `.venv/` | Package configuration via uv |
| API Clients | `clients/fpl_api.py`, `clients/fpl_auth.py` | Inbound request handlers and JWT Playwright/tiered login |
| Data Dictionary | `docs/data_dictionary.md` | Mapping from raw API fields to flat files |
| CLI Commands | `commands/` | Scripts for refreshing, snapshotting, modeling, backtesting, solving |
| Custom Models | `models/` | Baseline linear rolling model conforming to contract |
| Features & Projections | `features/`, `projections/` | Data compilers and solver projection exporters |
| Backtesting Engine | `commands/backtest.py` | Engine for historical performance simulation |
| Vendored Solver | `solver/` | Port of open-fpl-solver modules |

---

## What does NOT exist yet (do not assume)

*All planned phases and components have been implemented.*

---

## Safe commands today

```bash
PYTHONPATH=. .venv/bin/pytest                     # Run pytest
.venv/bin/ruff check .                            # Lint code
PYTHONPATH=. .venv/bin/python -m commands.refresh_data   # Ingest current gameweek data
PYTHONPATH=. .venv/bin/python -m commands.run_model linear_baseline   # Generate projections
PYTHONPATH=. .venv/bin/python -m commands.solve --preseason --xmin_lb 0 # Optimize preseason transfers
PYTHONPATH=. .venv/bin/python -m commands.report                      # Print report
```

---

## Agent pitfalls

- In `commands/run_model.py` (L38) and `commands/solve.py` (L117), negating pandas Series with `not` is invalid and raises `ValueError`. Use bitwise `~` instead.
- In `commands/solve.py` (L50), if the user has wildcard or unlimited transfers, FPL API returns `None` for transfer limit. This crashes the script with a `TypeError`.
- In `commands/backtest.py` (L99), pandas Spearman correlation calculation requires `scipy` which is not listed in `pyproject.toml` dependencies.
- Playwright Chromium browser binary must be installed using `.venv/bin/playwright install chromium` to run `refresh_data` or `snapshot_season` commands.

---

## Doc map

| Question | Read |
|----------|------|
| Glossary | `CONTEXT.md` |
| Phases & checklist | `ROADMAP.md` |
| Agent rules | `AGENTS.md` |
| How to update progress | `docs/agents/progress.md` |
