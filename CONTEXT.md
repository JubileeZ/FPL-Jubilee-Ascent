# FPL Jubilee Ascent

FPL analytics and optimization engine for a single user. Ingests live FPL API data, engineers predictive features, generates per-player per-gameweek xP projections, and solves for the optimal 15-man squad and transfer plan.

## Language

**User Squad**:
The user's specific 15-player Fantasy Premier League squad.
_Avoid_: Manager team, FPL team, team

**Club**:
A real-world Premier League club (e.g., Arsenal, Liverpool). Maps to `team` in the FPL API.
_Avoid_: Team (in domain model)

**Player**:
A Premier League footballer available for selection. Maps to `element` in the FPL API.
_Avoid_: Element, asset

**Raw Cache**:
Raw JSON responses from the FPL API stored in `data/raw/`. A rate-limit shield and offline fallback, not a source of truth. Gitignored.
_Avoid_: Cache, historical data

**Projection**:
A per-player per-gameweek expected points estimate produced by a model. Stored in PostgreSQL with `model_version` and `run_at` so outputs across model versions can be compared.
_Avoid_: xP output, prediction, score
