# FPL-Jubilee-Ascent Roadmap

---

## Phase 1: Foundation
**Goal:** Repo boots, FPL data flows in, nothing breaks.

### Tasks
- Monorepo scaffold (`backend/`, `frontend/`, `tools/`, `data/raw/`)
- FPL API client in `backend/app/clients/` (public data + authenticated User Squad)
- Raw data models: Pydantic schemas for Player, Fixture, User Squad
- PostgreSQL setup + SQLAlchemy connection
- `.env.example`, `AGENTS.md`, `CLAUDE.md` committed
- Lint + test pipeline passing (`ruff`, `pytest`)

### ✅ Milestone Output
**CLI command that prints your current User Squad to the terminal.**

```bash
uv run python -m app.cli squad --gw 36
```

```
GW36 Squad — Jubilee
─────────────────────────────────────────
GKP  Raya          Arsenal       £6.0m
DEF  Alexander-Arnold  Liverpool  £7.2m
...
Budget remaining: £0.4m
```

The user can see their live User Squad pulled from the FPL API with real prices and positions.

---

## Phase 2: Projection Engine
**Goal:** Produce a `final_xp` per player per gameweek from a configurable model.

### Tasks
- Feature engineering pipeline (`backend/app/services/feature_engineer.py`)
- Configurable model interface: plug in statistical baseline or ML model (XGBoost / scikit-learn)
- Output: `PlayerProjection` Pydantic objects with `raw_xp` per GW
- Parquet cache for historical data (`data/cache/`)
- Unit tests with mocked FPL data (no real network calls)

### ✅ Milestone Output
**CLI command that prints a ranked xP projection table for the next gameweek.**

```bash
uv run python -m app.cli project --gw 36 --model statistical
```

```
GW36 xP Projections
─────────────────────────────────────────────────
Rank  Player              Team       Pos   xP
 1    Salah               Liverpool  MID   8.4
 2    Haaland             Man City   FWD   7.9
 3    Alexander-Arnold    Liverpool  DEF   6.1
...
Model: statistical | Generated: 2025-04-01 09:12
```

The user can see ranked per-player projections before any solver or LLM runs.

---

## Phase 3: MILP Solver
**Goal:** Optimal 15-man squad and transfer plan from projections.

### Tasks
- PuLP solver in `backend/app/services/solver.py`
- Constraints: 15-man squad, £100m budget, position limits (2 GKP / 5 DEF / 5 MID / 3 FWD), max 3 per club, transfer count
- Objective: maximize `Σ final_xp` across selected squad
- Output: optimal squad JSON + transfer plan
- Tested against known fixture/projection fixtures

### ✅ Milestone Output
**CLI command that prints the optimal squad and recommended transfers.**

```bash
uv run python -m app.cli optimize --gw 36 --transfers 1
```

```
Optimal Squad — GW36 (stat model, 1 free transfer)
─────────────────────────────────────────────────
GKP  Raya          Arsenal       £6.0m   xP: 4.8
DEF  Alexander-Arnold  Liverpool  £7.2m  xP: 6.1
...
Total xP: 68.4  |  Cost: £99.6m

Recommended Transfer
  OUT: Isak (£8.1m)  →  IN: Haaland (£14.2m)
  xP gain: +2.3 pts  |  Cost: -£6.1m
```

The user can see a solver-generated squad and a concrete transfer recommendation they can act on immediately.

---

## Phase 4: LLM Tool Layer
**Goal:** LLM factors blend into projections before the solver runs.

### Tasks
- MCP server scaffold in `tools/llm_tool/`
- Defined contract: `{ player_id, minutes_factor, availability_flag, confidence, reason }`
- Blender service: `raw_xp * minutes_factor * availability_flag` with `llm_weight` config
- `llm_weight=0.0` short-circuits tool call entirely
- Schema validation before blender receives LLM output
- Integration: both stat-only and LLM-augmented projections produced and compared

### ✅ Milestone Output
**CLI command showing stat vs LLM-augmented projections side by side, with reasons.**

```bash
uv run python -m app.cli optimize --gw 36 --transfers 1 --llm
```

```
Optimal Squad — GW36 (LLM-augmented, 1 free transfer)
─────────────────────────────────────────────────────────────────────
Player              Stat xP  LLM xP  Δ      Reason
Salah               8.4      8.4     —
Haaland             7.9      5.1    -2.8    Rotation risk: rested in last 2 cup games
Alexander-Arnold    6.1      6.1     —
...

Recommended Transfer
  OUT: Haaland (£14.2m)  →  IN: Watkins (£8.3m)
  LLM xP gain: +1.4 pts  |  Confidence: medium
```

The user can see exactly how and why LLM context changed the recommendation vs the stat-only output.

---

## Phase 5: Frontend
**Goal:** Full browser UI over the entire pipeline.

### Tasks
- Auth: FPL credential input form
- Squad view: current 15-man squad with xP per player and score component breakdown
- Player dashboard: performance history charts per player
- xP scatter plot: explorable, stat vs LLM projection comparison
- Mode toggle: statistical-only vs LLM-augmented
- Transfer recommendation panel

### ✅ Milestone Output
**Full browser app accessible at `http://localhost:3000`.**

The user can:
- Log in with their FPL credentials
- See their current squad with live prices and xP projections
- Explore any player's form, fixtures, and projected minutes
- Toggle between stat-only and LLM-augmented recommendations
- View the recommended transfer with a side-by-side xP comparison

---

## Phase 6: Hardening
**Goal:** Production-ready, robust to failures.

### Tasks
- Redis cache for FPL API rate-limit protection
- Graceful fallback to stat-only mode if LLM tool call fails
- End-to-end test: credential in → optimal squad JSON out
- Docker Compose setup for full stack (backend + frontend + PostgreSQL + Redis)
- Error states visible in UI (LLM unavailable, FPL API down, solver infeasible)

### ✅ Milestone Output
**`docker compose up` boots the full stack from scratch with no manual steps.**

```bash
docker compose up
# → http://localhost:3000 — full app running
# → http://localhost:8000/docs — FastAPI swagger UI
```

The user can hand the repo to any machine and get a running instance with a single command.

---

## Summary

| Phase | Tangible Output |
|-------|----------------|
| 1. Foundation | CLI prints live User Squad |
| 2. Projections | CLI prints ranked xP table |
| 3. MILP Solver | CLI prints optimal squad + transfer |
| 4. LLM Layer | CLI shows stat vs LLM diff with reasons |
| 5. Frontend | Browser app at `localhost:3000` |
| 6. Hardening | `docker compose up` boots full stack |
