import asyncio
import os
from app.clients.fpl_auth import get_jwt_token, TOKEN_CACHE_PATH


async def main() -> None:
    print("Starting FPL authentication integration test...")
    email = os.getenv("FPL_EMAIL")
    password = os.getenv("FPL_PASSWORD")

    if not email or not password:
        print("ERROR: FPL_EMAIL and FPL_PASSWORD must be set in your .env file.")
        print("Please check your .env file or export these variables.")
        return

    print(f"Using email: {email}")
    print(f"Token cache path: {TOKEN_CACHE_PATH}")

    if TOKEN_CACHE_PATH.exists():
        print(f"Removing existing cached token at {TOKEN_CACHE_PATH} to force login...")
        TOKEN_CACHE_PATH.unlink()

    try:
        print("Executing Playwright login...")
        token = await get_jwt_token()
        print("\nSUCCESS!")
        print(f"Captured token (JWT): {token[:15]}...{token[-15:]}")
        print(f"Token length: {len(token)} characters.")

        print("\nVerifying caching...")
        if TOKEN_CACHE_PATH.exists():
            print("Token cache file created successfully.")
            # Run again to ensure it reads from cache
            token2 = await get_jwt_token()
            if token == token2:
                print("Cache verification passed: get_jwt_token retrieved the cached token directly.")
            else:
                print("Cache verification failed: got different tokens on reload.")
        else:
            print("ERROR: Cache file was not created.")

    except Exception as e:
        print(f"\nFAILURE: {e}")


if __name__ == "__main__":
    asyncio.run(main())
