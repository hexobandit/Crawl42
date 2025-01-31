import asyncio
import random
from pyppeteer import launch
from urllib.parse import urljoin, urlparse

BASE_URL = "https://logmonitor.eu/"

async def login_and_crawl():
    browser = await launch(
        executablePath="/Applications/Chromium.app/Contents/MacOS/Chromium",
        headless=False, 
        args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-gpu",
            "--disable-software-rasterizer",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
            "--disable-background-networking",
            "--disable-sync",
            "--disable-default-apps",
            "--disable-component-update",
            "--disable-domain-reliability",
            "--disable-breakpad",
            "--disable-client-side-phishing-detection",
            "--disable-hang-monitor",
            "--disable-popup-blocking",
            "--disable-prompt-on-repost",
            "--disable-renderer-backgrounding",
            "--disable-web-security",
            "--disable-notifications"
        ],
        dumpio=True
    )
    page = await browser.newPage()

    # Enable stealth mode to reduce bot detection
    await page.setUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

    # Storage for collected data
    captured_endpoints = set()
    captured_cookies = {}
    jwt_token = None

    # Function to intercept network requests
    async def intercept_request(request):
        nonlocal jwt_token
        url = request.url

        # Capture API endpoints
        if url.startswith(BASE_URL) and url not in captured_endpoints:
            captured_endpoints.add(url)

        # Capture JWT from headers
        auth_header = request.headers.get("authorization", "")
        if auth_header and "Bearer" in auth_header:
            jwt_token = auth_header.split("Bearer ")[1]

        await request.continue_()

    await page.setRequestInterception(True)
    page.on('request', lambda req: asyncio.ensure_future(intercept_request(req)))

    # Visit login page
    await page.goto(f"{BASE_URL}/login", waitUntil="networkidle2")

    # Check if a CSRF token is required
    csrf_token = await page.evaluate("""
        () => {
            let csrfElement = document.querySelector('[name=csrf_token]');
            return csrfElement ? csrfElement.value : null;
        }
    """)
    if csrf_token:
        print(f"🔹 CSRF Token Found: {csrf_token}")

    # Fill login form
    await page.type("#username", "USER")
    await page.type("#password", "PWD")

    if csrf_token:
        await page.evaluate(f"document.querySelector('[name=csrf_token]').value = '{csrf_token}';")

    await asyncio.sleep(random.uniform(2, 4))  # Randomized delay to avoid detection
    
    # Click login button
    await page.click("#login-button")
    # Wait for navigation to complete (max 15 sec)
    await page.waitForNavigation(waitUntil="networkidle2", timeout=15000)

    # Wait for authentication
    await page.waitForNavigation(waitUntil="networkidle2")

    # Extract JWT from localStorage
    jwt_token = await page.evaluate("localStorage.getItem('jwt_token');") or jwt_token

    # Extract session cookies
    cookies = await page.cookies()
    for cookie in cookies:
        captured_cookies[cookie['name']] = cookie['value']

    print("\n✅ Authentication Data:")
    print(f"🔐 JWT Token: {jwt_token}" if jwt_token else "❌ No JWT found.")
    print(f"🍪 Captured Cookies: {captured_cookies}")

    # Visit a protected page and extract all links
    await page.goto(f"{BASE_URL}/dashboard", waitUntil="networkidle2")

    # Extract all links on the current page
    links = await page.evaluate("""
        () => Array.from(document.querySelectorAll('a'))
                  .map(a => a.href)
    """)

    # Normalize and filter links
    unique_links = {urljoin(BASE_URL, url) for url in links if url.startswith("/") or BASE_URL in url}

    print("\n🔗 Extracted Links:")
    for link in unique_links:
        print(link)

    print("\n📡 Captured API Endpoints:")
    for endpoint in captured_endpoints:
        print(endpoint)

    await browser.close()

# Run the function
asyncio.run(login_and_crawl())