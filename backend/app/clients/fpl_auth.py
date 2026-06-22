import os
import base64
import json
import time
import logging
from pathlib import Path
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

# Walk up from this file's directory backend/app/clients/fpl_auth.py to project root
PROJECT_ROOT = Path(__file__).resolve().parents[3]
TOKEN_CACHE_PATH = PROJECT_ROOT / "data" / "session_token.json"


def is_jwt_expired(token: str) -> bool:
    """Check if the JWT token is expired or close to expiring (within a 5-minute window)."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return True
        payload_b64 = parts[1]
        # Pad payload if necessary for base64 decoding
        payload_b64 += "=" * (4 - len(payload_b64) % 4)
        payload_json = base64.b64decode(payload_b64).decode("utf-8")
        payload = json.loads(payload_json)
        exp = payload.get("exp", 0)
        # Check if expired (with a 5-minute safety buffer)
        return time.time() > (exp - 300)
    except Exception as e:
        logger.warning(f"Error checking token expiration: {e}")
        return True


async def async_login() -> str:
    """Automate login via Playwright to retrieve the pl_profile JWT token cookie."""
    email = os.getenv("FPL_EMAIL")
    password = os.getenv("FPL_PASSWORD")

    if not email or not password:
        raise ValueError("FPL_EMAIL and FPL_PASSWORD environment variables must be set.")

    logger.info("Initializing headless browser login...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Using a realistic User-Agent to avoid anti-bot checks
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        logger.info("Navigating to fantasy.premierleague.com...")
        await page.goto("https://fantasy.premierleague.com/")

        # Auto-accept cookies if prompt appears
        try:
            accept_btn = page.locator("#onetrust-accept-btn-handler")
            await accept_btn.wait_for(state="visible", timeout=5000)
            await accept_btn.click()
            logger.info("Cookies accepted.")
        except Exception:
            logger.info("No cookie banner detected or timeout.")

        # Locate and click 'Sign In' or 'Log in' link/button
        logger.info("Clicking sign in link...")
        sign_in_selectors = [
            'a:has-text("Sign in")',
            'a:has-text("Log in")',
            'a:has-text("Sign In")',
            'a:has-text("Log In")',
            'button:has-text("Sign in")',
            'button:has-text("Log in")',
            '#login'
        ]
        
        clicked = False
        for selector in sign_in_selectors:
            try:
                btn = page.locator(selector)
                if await btn.is_visible():
                    await btn.click()
                    clicked = True
                    logger.info(f"Clicked sign in link via: {selector}")
                    break
            except Exception:
                continue
                
        if not clicked:
            # Fallback to navigating directly to users.premierleague.com/accounts/login/ if we couldn't click it
            logger.warning("Could not locate login button dynamically, navigating to login URL directly...")
            await page.goto("https://users.premierleague.com/accounts/login/")

        # Wait for the login form input fields to be visible
        logger.info("Waiting for login form fields...")
        email_input = page.locator('input[name="login"]')
        await email_input.wait_for(state="visible", timeout=15000)

        logger.info("Filling credentials...")
        await email_input.fill(email)
        await page.locator('input[name="password"]').fill(password)

        logger.info("Submitting form...")
        await page.locator('button[type="submit"]').click()

        # Wait for redirect/network idle to ensure login flow completes
        await page.wait_for_load_state("networkidle")

        cookies = await context.cookies()
        pl_profile_cookie = None
        for cookie in cookies:
            if cookie["name"] == "pl_profile":
                pl_profile_cookie = cookie["value"]
                break

        await browser.close()

        if not pl_profile_cookie:
            raise RuntimeError("Failed to capture 'pl_profile' cookie during login flow.")

        logger.info("Successfully captured pl_profile session token.")
        return pl_profile_cookie


async def get_jwt_token(force_refresh: bool = False) -> str:
    """Get a valid FPL session token, retrieving from local cache or performing login if necessary."""
    if not force_refresh and TOKEN_CACHE_PATH.exists():
        try:
            with open(TOKEN_CACHE_PATH, "r") as f:
                data = json.load(f)
                token = data.get("token")
                if token and not is_jwt_expired(token):
                    logger.info("Using cached FPL session token.")
                    return token
        except Exception as e:
            logger.warning(f"Failed to read cached token: {e}")

    # Fetch new token
    token = await async_login()

    # Cache token
    try:
        TOKEN_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_CACHE_PATH, "w") as f:
            json.dump({"token": token, "cached_at": time.time()}, f)
        logger.info(f"Cached new FPL session token to {TOKEN_CACHE_PATH}")
    except Exception as e:
        logger.warning(f"Failed to cache token: {e}")

    return token
