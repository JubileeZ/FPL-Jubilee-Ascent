# PRD: Phase 1 — Foundation

## Problem Statement

The user wants an automated way to query their active Fantasy Premier League (FPL) squad, inspect player and fixture information, and establish a data pipeline foundation for running predictive analytics, without having to manually log in to the FPL website or parse raw JSON APIs every time.

## Solution

A command-line interface (CLI) tool that automatically logs in to FPL using Playwright to handle SSO redirects, discovers the User Squad, pulls all current Player, Club, and Fixture data from the FPL API, persists it to a local PostgreSQL database, and prints a formatted view of the active User Squad.

## User Stories

1. As a developer, I want to boot a local PostgreSQL instance with a single command, so that I have a consistent database environment.
2. As a user, I want the system to handle FPL's SSO login flow automatically, so that I don't have to manually grab cookies or log in myself.
3. As a developer, I want to fall back to a pre-captured session cookie/token in my environment variables, so that I can bypass browser-based SSO during testing or local automation.
4. As a user, I want the system to auto-discover my FPL Manager ID from my active session, so that I do not need to look up or hardcode my numeric ID.
5. As a developer, I want the system to save all raw JSON responses from the FPL API to a local Raw Cache before parsing them, so that I do not get rate-limited by FPL during development and can run operations offline.
6. As a user, I want the system to ingest and sync all ~600 Players, Clubs, and Fixtures from the FPL API into the database, so that all Premier League data is local and queryable.
7. As a user, I want to run a simple CLI command `squad --gw <number>` to print a clear list of my 15-player User Squad by position, showing prices and remaining budget, so that I can quickly verify my current team configuration.
8. As a developer, I want the database connection and raw ingest functions to be fully unit-tested with mocked HTTP responses and a mocked auth client, so that the code is robust and testable without making external network calls.

## Implementation Decisions

- **Database & Persistence**:
  - A local PostgreSQL database managed via a minimal Docker Compose service containing just the database.
  - SQLAlchemy ORM models defined for Clubs, Players, Fixtures, UserSquads, and UserSquadPlayers.
  - DB initialization logic exposed to verify connection health.
- **Authentication & SSO**:
  - Playwright SSO interceptor automating navigation of the FPL login page (`https://users.premierleague.com/accounts/login/`) to bypass SSO and securely capture the session token/cookie.
  - Manager ID auto-discovery by hitting the FPL `/api/me/` endpoint with the captured token and caching it to config.
- **Data Ingestion & Sync**:
  - HTTP client using HTTPX and wrapped with tenacity retry logic.
  - Raw JSON API responses saved directly to `data/raw/` before any parsing.
  - Sync service parsing FPL bootstrap-static and picks data, mapping api entities (like `element` to Player, `team` to Club) and storing them in the PostgreSQL database.
- **CLI Commands**:
  - Command line utility exposing:
    - `db ping`: Verify DB connection health.
    - `sync`: Perform full ingestion of clubs, players, fixtures, and User Squad data.
    - `squad --gw <number>`: Read User Squad details from the DB and print a formatted squad view.

## Testing Decisions

- **Seam-based Integration Testing**:
  - We only test external behavior: CLI commands produce the correct printed outputs, and sync services store the correct entities in the database when given valid API responses.
  - Playwright auth client interface mocked to inject a dummy token/cookie during testing.
  - HTTPX client mocked using pytest fixtures that return static mock JSON responses mimicking FPL endpoints.
  - Database transactions in tests rolled back after each test run to keep tests isolated.

## Out of Scope

- Generating expected points (xP) or running the optimization solver (Phases 2-4).
- Building the browser frontend UI (Phase 5).
- Setting up the FastAPI server/endpoints (Phase 5).

## Further Notes

- Built using Python 3.12 and managed via `uv`.
- Pre-commit tests and lint pipeline run via `pytest` and `ruff`.
