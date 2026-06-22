# Database migrations using Alembic

To manage PostgreSQL schema changes, the project uses Alembic migrations outputting to `backend/app/db/migrations/`, rather than automatic startup synchronization (e.g., SQLAlchemy's `create_all()`).

## Context and Decision

Automatic schema synchronization on startup is simple but dangerous in production or multi-developer settings because it obscures schema history, risks accidental data loss, and makes rollback/version-tracking impossible. Explicitly tracked migrations ensure database states are deterministic.

## Considered Options

- **Alembic Migrations** — Explicit migration scripts tracked under `backend/app/db/migrations/`. Chosen.
  - *Pros*: Full history, reversible transitions, safe for production, no automatic modification.
  - *Cons*: Minor developer friction to generate and apply migrations.
- **SQLAlchemy `create_all()` on startup** — Automatic table synchronization. Rejected.
  - *Pros*: Zero friction.
  - *Cons*: Cannot handle schema changes (only creates missing tables), risks silent data truncation/drift, and violates the "explicitly tracked and never auto-applied" safety rule of the project.
