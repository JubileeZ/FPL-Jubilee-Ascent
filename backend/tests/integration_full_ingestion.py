import asyncio
import os
import httpx
from app.clients.fpl_auth import get_jwt_token
from app.clients.fpl_api import (
    fetch_bootstrap_static,
    fetch_user_details,
    fetch_user_team,
    fetch_entry_summary,
    fetch_entry_history,
    fetch_entry_transfers,
    fetch_gameweek_picks,
    RAW_CACHE_DIR,
)


async def main() -> None:
    print("Starting FPL Full Ingestion Integration Test...")
    email = os.getenv("FPL_EMAIL")
    password = os.getenv("FPL_PASSWORD")

    if not email or not password:
        print("ERROR: FPL_EMAIL and FPL_PASSWORD must be set in your .env file.")
        print("Please check your .env file or export these variables.")
        return

    print(f"Using email: {email}")
    print(f"Raw cache directory: {RAW_CACHE_DIR}")

    async with httpx.AsyncClient() as client:
        try:
            print("\n1. Running FPL authentication...")
            token = await get_jwt_token()
            print(f"   Success! Token captured (length {len(token)}).")

            print("\n2. Fetching user profile details (me)...")
            me = await fetch_user_details(client, token)
            print(f"   Success! User data keys: {list(me.keys())}")

            player = me.get("player", {})
            entry_id = player.get("entry") if player else None

            if not entry_id:
                print("   WARNING: Could not find 'player.entry' in profile response.")
                entry_id = me.get("entry")

            if not entry_id:
                raise ValueError(f"Failed to find entry ID in profile payload: {me}")

            print(f"   Success! Found user entry ID: {entry_id}")

            print("\n3. Fetching user team squad (my-team)...")
            team = await fetch_user_team(client, entry_id, token)
            print(f"   Success! Team keys: {list(team.keys())}")

            print("\n4. Fetching entry summary...")
            summary = await fetch_entry_summary(client, entry_id, token)
            print(f"   Success! Summary keys: {list(summary.keys())}")

            print("\n5. Fetching entry history...")
            history = await fetch_entry_history(client, entry_id, token)
            print(f"   Success! History keys: {list(history.keys())}")

            print("\n6. Fetching entry transfers...")
            transfers = await fetch_entry_transfers(client, entry_id, token)
            print(f"   Success! Fetched {len(transfers)} transfers.")

            print("\n7. Fetching bootstrap static to resolve current gameweek...")
            bootstrap = await fetch_bootstrap_static(client)
            events = bootstrap.get("events", [])
            current_gw = next((e["id"] for e in events if e.get("is_current")), 1)

            print(f"\n8. Fetching gameweek picks for gameweek {current_gw}...")
            picks = await fetch_gameweek_picks(client, entry_id, current_gw, token)
            print(f"   Success! Picks keys: {list(picks.keys())}")

            print("\nVERIFYING CACHED FILES:")
            expected_files = [
                "me.json",
                f"my_team_{entry_id}.json",
                f"entry_{entry_id}.json",
                f"entry_{entry_id}_history.json",
                f"entry_{entry_id}_transfers.json",
                f"entry_{entry_id}_picks_gw_{current_gw}.json",
                "bootstrap_static.json",
            ]

            all_exist = True
            for filename in expected_files:
                path = RAW_CACHE_DIR / filename
                if path.exists():
                    print(f"  [OK] Found cache file: {filename} (Size: {path.stat().st_size} bytes)")
                else:
                    print(f"  [MISSING] Cache file: {filename}")
                    all_exist = False

            if all_exist:
                print("\nALL AUTHENTICATED INGESTION TESTS PASSED AND CACHED!")
            else:
                print("\nSOME CACHED FILES ARE MISSING.")

        except Exception as e:
            print(f"\nFAILURE during authenticated ingestion: {e}")


if __name__ == "__main__":
    asyncio.run(main())
