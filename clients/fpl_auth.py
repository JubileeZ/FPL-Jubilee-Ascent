import os
import base64
import json
import time
import logging
from pathlib import Path
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

# Walk up from this file's directory clients/fpl_auth.py to project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]
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
    """Automate login via Playwright to retrieve the x-api-authorization JWT token."""
    email = os.getenv("FPL_EMAIL")
    password = os.getenv("FPL_PASSWORD")

    if not email or not password:
        raise ValueError("FPL_EMAIL and FPL_PASSWORD environment variables must be set.")

    headless_env = os.getenv("FPL_HEADLESS", "true").lower() in ("true", "1", "yes")
    logger.info(f"Initializing browser login (headless={headless_env})...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless_env)
        # Using a realistic User-Agent and desktop viewport to avoid mobile layout collapse and anti-bot checks
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
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
        email_input = None
        email_selectors = ['input[name="username"]', '#username', 'input[name="login"]', 'input[type="email"]', '#login', '#email', 'input[name="email"]']
        
        # Try to wait for any of the common selectors to appear
        for selector in email_selectors:
            try:
                locator = page.locator(selector)
                # Wait with a short timeout per selector to check presence
                await locator.wait_for(state="visible", timeout=3000)
                email_input = locator
                logger.info(f"Found email input field using: {selector}")
                break
            except Exception:
                continue

        if not email_input:
            # Fallback to waiting for the primary selector to log diagnostic info on failure
            try:
                email_input = page.locator('input[name="login"]')
                await email_input.wait_for(state="visible", timeout=5000)
            except Exception as e:
                logger.error(f"Failed to find email input field. Timeout error: {e}")
                try:
                    title = await page.title()
                    logger.error(f"Current page title: {title}")
                    url = page.url
                    logger.error(f"Current URL: {url}")
                except Exception:
                    pass
                try:
                    inputs = await page.locator("input").all()
                    logger.error(f"Found {len(inputs)} input elements on the page:")
                    for idx, inp in enumerate(inputs):
                        html = await inp.evaluate("el => el.outerHTML")
                        logger.error(f"  Input {idx}: {html}")
                except Exception as ex:
                    logger.error(f"Failed to inspect input elements: {ex}")
                raise

        logger.info("Filling credentials...")
        await email_input.fill(email)

        # Locate and fill password
        password_input = None
        password_selectors = ['input[name="password"]', 'input[type="password"]', '#password']
        for selector in password_selectors:
            try:
                locator = page.locator(selector)
                if await locator.is_visible():
                    password_input = locator
                    break
            except Exception:
                continue
        
        if not password_input:
            password_input = page.locator('input[name="password"]')
        await password_input.fill(password)

        # Locate and click submit
        logger.info("Submitting form...")
        submit_btn = None
        submit_selectors = ['#btnSignIn', 'button:has-text("Sign in"):not(:has-text("with"))', 'button:has-text("Sign In"):not(:has-text("with"))', 'button:has-text("Log in")']
        for selector in submit_selectors:
            try:
                locator = page.locator(selector).first
                if await locator.is_visible():
                    submit_btn = locator
                    break
            except Exception:
                continue
        
        if not submit_btn:
            submit_btn = page.locator('button[type="submit"]').first
        await submit_btn.click()

        logger.info("Waiting for login redirect to complete...")
        try:
            await page.wait_for_url("https://fantasy.premierleague.com/", timeout=15000)
            logger.info("Redirect completed successfully.")
        except Exception as e:
            logger.warning(f"wait_for_url timeout or error: {e}")

        # Setup request interception to catch the auth token
        logger.info("Setting up request interception for API authorization header...")
        found_auth = None
        
        async def handle_request(request):
            nonlocal found_auth
            if "/api/" in request.url:
                headers = await request.all_headers()
                auth_headers = {k:v for k,v in headers.items() if 'auth' in k.lower() or 'bearer' in v.lower() or 'token' in k.lower()}
                if auth_headers and 'x-api-authorization' in auth_headers:
                    logger.info("x-api-authorization header captured!")
                    found_auth = auth_headers['x-api-authorization']
        
        page.on("request", handle_request)
        
        logger.info("Navigating to /transfers to trigger authenticated API calls...")
        await page.goto("https://fantasy.premierleague.com/transfers")
        
        # Wait up to 15 seconds for an API call with the token
        for _ in range(15):
            if found_auth:
                break
            await page.wait_for_timeout(1000)

        await browser.close()

        if not found_auth:
            raise RuntimeError("Failed to capture 'x-api-authorization' bearer token during login flow.")

        # Extract the token from "Bearer <token>"
        token = found_auth.replace("Bearer ", "").strip()
        logger.info("Successfully captured session token.")
        return token


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
