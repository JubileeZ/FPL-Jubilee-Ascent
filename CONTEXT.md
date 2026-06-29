# FPL-Jubilee-Ascent

FPL analytics and optimization engine for a single user. Ingests live FPL API data, engineers predictive features, generates per-player per-gameweek expected points (xP) projections, and solves for the optimal squad and transfer plan.

## Language

**User Squad**:
The user's specific 15-player Fantasy Premier League squad. Keyed by `entry_id`.
_Avoid_: Manager team, FPL team, team, manager_id

**Club**:
A real-world Premier League club (e.g. Arsenal, Liverpool). Keyed by `team_id` or `club_id`. Maps to `team` in the FPL API.
_Avoid_: Team (in domain model context)

**Position**:
A player's general pitch role (Goalkeeper, Defender, Midfielder, Forward). Maps to `element_type` in the FPL API.
_Avoid_: position (used as lineup index)

**Lineup Index**:
The squad slot/lineup position within the User Squad (integer 1 to 15, e.g. starting GK is 1, bench GK is 12). Maps to `position` in the FPL `/my-team/` endpoint picks.
_Avoid_: position_id, player position

**Player**:
A Premier League footballer available for selection. Maps to `element` in the FPL API.
_Avoid_: Element, asset

**Raw Cache**:
Raw JSON responses from the FPL API stored in `data/raw/`. Used as a rate-limit shield.
_Avoid_: Cache, historical data

**Projection**:
A per-player per-gameweek expected points (xP) and expected minutes (xMins) estimate produced by a model.
_Avoid_: xP output, prediction, score

**Feature Contract**:
The strictly defined schema of engineered inputs passed to any projection model.
_Avoid_: Raw features, model inputs

**Model Adapter**:
A standardized interface that wraps any projection model, accepting a Feature Contract and outputting projections.
_Avoid_: Core model, custom model logic

**Planning Horizon**:
The configurable lookahead window (3-8 gameweeks) used by the MILP solver to optimize transfer strategy and team selection.
_Avoid_: Optimization length, gameweek plan
