# Crawl42
 The answer to authenticated crawling and everything 🤖

- ✅ Logs in and handles different authentication methods (JWT, session cookies, CSRF tokens)
- ✅ Extracts JWT from localStorage, cookies, or network headers
- ✅ Captures all XHR/fetch API requests for endpoint discovery
- ✅ Extracts all internal links from the authenticated session
- ✅ Handles CSRF tokens if present
- ✅ Avoids bot detection (stealth mode, random delays)


## Install and Run


```
brew install chromium
xattr -cr /Applications/Chromium.app #Allow Chromium to Run via Terminal
python3 -m venv venv
source venv/bin/activate
pip install pyppeteer
python crawl42.py
```

## What This Script Does Automatically

1. **Handles Authentication:**
- Logs in using username and password.
- Detects and fills CSRF tokens automatically.
- Waits for authentication to complete.
2. **Extracts Authentication Data:**
- Retrieves JWT from local storage.
- Captures session cookies if JWT isn’t found.
- Intercepts API requests to detect token passing.
3. **Crawls Protected Pages:**
- Extracts all internal links from the dashboard.
- Captures all API endpoints accessed in background requests.
4. **Avoids Bot Detection:**
- Uses realistic User-Agent.
- Randomizes delays in form submissions to mimic human behavior.
- Stealth mode enabled with --disable-blink-features=AutomationControlled.

If the site blocks you try ```headless=True``` for stealth.