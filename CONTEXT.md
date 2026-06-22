# FPL Jubilee Ascent

FPL analytics and optimization engine for a single user. Ingests live FPL API data, engineers predictive features, generates per-player per-gameweek xP projections, and solves for the optimal 15-man squad and transfer plan.

## Language

**User Squad**:
The user's specific 15-player Fantasy Premier League squad. Keyed by `entry_id` (e.g., `6025459`).
_Avoid_: Manager team, FPL team, team, manager_id

**Club**:
A real-world Premier League club (e.g., Arsenal, Liverpool). Keyed by `team_id` (or `club_id`). Maps to `team` in the FPL API.
_Avoid_: Team (in domain model)

**Position**:
A player's general pitch role (Goalkeeper, Defender, Midfielder, Forward). Maps to `element_type` in the FPL API. Stored as `position_id` in relational tables.
_Avoid_: position (used as lineup index)

**Lineup Index**:
The squad slot/lineup position within the User Squad (integer 1 to 15, e.g. starting GK is 1, bench GK is 12). Maps to `position` in the FPL `/my-team/` endpoint picks.
_Avoid_: position_id, player position

**Player**:
A Premier League footballer available for selection. Maps to `element` in the FPL API.
_Avoid_: Element, asset

**Raw Cache**:
Raw JSON responses from the FPL API stored in `data/raw/`. A rate-limit shield and offline fallback, not a source of truth. Gitignored.
_Avoid_: Cache, historical data

**Projection**:
A per-player per-gameweek expected points estimate produced by a model. Stored in PostgreSQL with `model_version` and `run_at` so outputs across model versions can be compared.
_Avoid_: xP output, prediction, score

**FPL Authentication Token**:
The JWT session token extracted via Playwright SSO login and cached locally in `data/session_token.json`. Sent to authenticated endpoints in the `"x-api-authorization": "Bearer <token>"` header.
_Avoid_: Cookie auth, pl_profile cookie, raw cookie session

**Feature Contract**:
The strictly defined schema of engineered inputs passed to any projection model.
_Avoid_: Raw features, model inputs

**Model Adapter**:
A standardized interface that wraps any projection model, accepting a Feature Contract and outputting projections (e.g. expected minutes, performance metrics per minute).
_Avoid_: Core model, custom model logic

**LLM Blending**:
The weighted combining of minutes component projections from the Model Adapter and LLM factor outputs using a configurable `LLM_WEIGHT` parameter.
_Avoid_: Combined prediction, direct LLM score

**Point Calculator**:
A system module that calculates final expected points (xP) by combining blended minutes with predicted performance metrics.
_Avoid_: Formula, point generator

**Planning Horizon**:
The configurable lookahead window (3-8 gameweeks) used by the MILP solver to optimize transfer strategy and team selection.
_Avoid_: Optimization length, gameweek plan


