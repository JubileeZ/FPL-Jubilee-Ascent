import asyncio
import httpx
from app.clients.fpl_api import (
    fetch_bootstrap_static,
    fetch_element_gameweek_live,
    fetch_gameweek_fixtures,
    fetch_element_summary,
    RAW_CACHE_DIR,
)


async def main() -> None:
    print("Starting FPL public API integration test...")
    print(f"Raw cache directory: {RAW_CACHE_DIR}")

    # Default test IDs, will override dynamically if bootstrap is fetched
    test_gw = 1
    test_player = 1

    async with httpx.AsyncClient() as client:
        try:
            print("1. Fetching bootstrap static...")
            bootstrap = await fetch_bootstrap_static(client)
            print(f"   Success! Keys in bootstrap: {list(bootstrap.keys())}")

            events = bootstrap.get("events", [])
            players = bootstrap.get("elements", [])

            if events:
                current_gw = next((e["id"] for e in events if e.get("is_current")), 1)
                test_gw = current_gw
            if players:
                test_player = players[0]["id"]

            print(f"2. Fetching element gameweek live for gameweek {test_gw}...")
            live = await fetch_element_gameweek_live(client, test_gw)
            print(f"   Success! Elements live keys: {list(live.keys())}")

            print(f"3. Fetching gameweek fixtures for gameweek {test_gw}...")
            fixtures = await fetch_gameweek_fixtures(client, test_gw)
            print(f"   Success! Number of fixtures: {len(fixtures)}")

            print(f"4. Fetching element summary for player {test_player}...")
            summary = await fetch_element_summary(client, test_player)
            print(f"   Success! Summary keys: {list(summary.keys())}")

            print("\nVERIFYING CACHED FILES:")
            expected_files = [
                "bootstrap_static.json",
                f"event_{test_gw}_live.json",
                f"fixtures_gw_{test_gw}.json",
                f"element_summary_{test_player}.json",
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
                print("\nALL PUBLIC DATA INGESTION TESTS PASSED AND CACHED!")
            else:
                print("\nSOME CACHED FILES ARE MISSING.")

        except Exception as e:
            print(f"\nFAILURE during public data ingestion: {e}")


if __name__ == "__main__":
    asyncio.run(main())
