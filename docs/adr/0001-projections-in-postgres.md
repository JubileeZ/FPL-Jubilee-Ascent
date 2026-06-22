# Projection outputs stored in PostgreSQL

The project already runs PostgreSQL. Storing projection outputs (per-player, per-gameweek, per-model-version xP estimates) in a `projections` table rather than as flat files (Parquet/JSON in `data/`) keeps model version history queryable with plain SQL and avoids Parquet diffing in git.

## Considered Options

- **PostgreSQL table** — `(gameweek, player_id, model_version, raw_xp, final_xp, run_at)`. Chosen.
- **File per run** — `data/projections/gw36_statistical_v1.parquet`. Rejected: Parquet doesn't diff in git; comparison requires a bespoke script; adds a second storage layer with no benefit given Postgres is already present.
