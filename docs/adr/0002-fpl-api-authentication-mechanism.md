# ADR 0002: FPL API Authentication Mechanism

## Status
Accepted

## Context
Fantasy Premier League (FPL) provides public and authenticated API endpoints. The user squad and history endpoints require authentication. 

In older integrations or references, FPL authentication was commonly handled by sending the session token inside the `Cookie` header as `pl_profile=<token>`. However, during integration testing on 2026-06-23, it was confirmed that the live FPL API no longer accepts token authorization via cookies. Utilizing `Cookie: pl_profile=<token>` results in 401 Unauthorized or fails to authenticate the requester.

Instead, the live API expects the authentication token to be sent via the `x-api-authorization` header with a Bearer scheme: `"x-api-authorization": "Bearer <token>"`.

## Decision
All authenticated requests made by the FPL API client to the Fantasy Premier League API must use the header:
```json
{
  "x-api-authorization": "Bearer <token>"
}
```

We must never use or fall back to:
```json
{
  "Cookie": "pl_profile=<token>"
}
```

## Consequences
- The client implementation (`fpl_api.py`) will exclusively use the `x-api-authorization` header.
- Unit tests (`test_fpl_api.py`) must be aligned to assert this header instead of cookies.
- Future agents and developers will be directed to this ADR and project guidelines to prevent accidental reversal to the deprecated cookie approach.
