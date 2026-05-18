# Instagram 401 Blocking Guide

## The Problem

Instagram actively detects and blocks automated scraping attempts. When you try to fetch a post without authentication or after multiple requests, you'll see:

```
ConnectionException: 401 Unauthorized - "Please wait a few minutes before you try again."
```

## Why This Happens

1. **No authentication** — Requests without login credentials are easily identified as bots
2. **Rate-limiting** — Multiple requests from the same IP trigger blocking
3. **IP-based detection** — Instagram flags suspicious IPs
4. **API changes** — Instagram frequently updates their anti-scraping measures

## Solutions (in order of reliability)

### 1. **Use Instagram Credentials** ⭐ (Most Reliable)

Authenticate with a valid Instagram account:

```python
from recipe_scraper import get_recipe_from_url

recipe = get_recipe_from_url(
    "https://www.instagram.com/p/CynRiw7OWi8/",
    instagram_username="your_username",
    instagram_password="your_password"
)
```

From CLI:
```bash
recipe-scraper "https://www.instagram.com/p/CynRiw7OWi8/" \
    --username your_username \
    --password your_password
```

**Important:** Use a real Instagram account (not a fake one). Instagram may ask for 2FA verification.

### 2. **Wait and Retry**

Instagram's rate-limiting cooldown typically lasts:
- **15-60 minutes** for the initial block
- **Up to 24 hours** for aggressive repeated attempts

```python
import time
time.sleep(600)  # Wait 10 minutes
recipe = get_recipe_from_url(url)
```

### 3. **Use a VPN or Different Network**

If your IP is blocked, switch networks:
```bash
# On Mac/Linux
brew install wireguard-go
# ... configure VPN ...
recipe-scraper "https://www.instagram.com/p/CynRiw7OWi8/"
```

### 4. **Use Recipe Websites Instead** ⭐ (Recommended)

Recipe websites don't have Instagram's blocking restrictions:

```python
# No authentication needed, no blocking, faster extraction
recipe = get_recipe_from_url("https://cooking.nytimes.com/recipes/...")
recipe = get_recipe_from_url("https://www.seriouseats.com/recipes/...")
recipe = get_recipe_from_url("https://www.allrecipes.com/recipe/...")
```

## How to Avoid Getting Blocked

If you're frequently fetching Instagram posts:

1. **Always use authentication** when possible
2. **Add delays between requests**:
   ```python
   import time
   for url in urls:
       recipe = get_recipe_from_url(url, instagram_username="user", instagram_password="pass")
       time.sleep(5)  # 5 seconds between requests
   ```

3. **Use recipe websites** instead of Instagram
4. **Rotate accounts** if processing large batches
5. **Monitor for 401 errors** and back off immediately

## Error Messages Reference

| Error | Cause | Solution |
|-------|-------|----------|
| `401 Unauthorized` | Rate-limited or IP blocked | Wait 15+ min, use credentials, try VPN |
| `429 Too Many Requests` | Too many requests too fast | Add delays between requests |
| `Post not found` | Post doesn't exist or is private | Check URL, use private account credentials |
| `Bad credentials` | Invalid username/password | Check Instagram login credentials |
| `QueryReturnedNotFoundException` | Post was deleted or is very old | Try different post |

## Instagram Credentials Best Practices

✅ **DO:**
- Use your own account
- Store credentials in environment variables or `.env` file
- Use distinct passwords for Instagram and other services
- Keep credentials private

❌ **DON'T:**
- Hardcode credentials in source code
- Use fake/bot accounts (get blocked immediately)
- Share credentials publicly
- Use credentials for hundreds of requests (looks like abuse)

## Example with Environment Variables

```python
import os
from recipe_scraper import get_recipe_from_url

username = os.getenv("INSTAGRAM_USERNAME")
password = os.getenv("INSTAGRAM_PASSWORD")

recipe = get_recipe_from_url(
    "https://www.instagram.com/p/CynRiw7OWi8/",
    instagram_username=username,
    instagram_password=password
)
```

Run with:
```bash
INSTAGRAM_USERNAME=myuser INSTAGRAM_PASSWORD=mypass recipe-scraper <url>
```

## When to Give Up on Instagram

If you're blocked repeatedly, it's time to:

1. **Switch to recipe websites** — They're faster, more reliable, no blocking
2. **Save recipes locally** — Copy/paste captions into text files
3. **Use the browser** — Just view posts manually if needed

Instagram is not a reliable source for automated recipe extraction due to aggressive anti-scraping measures.

## Frequently Asked Questions

**Q: Why doesn't using credentials always work?**
A: Instagram's session management is complex. Credentials help but don't guarantee access if your IP or account has a history of abuse.

**Q: Can I use a bot account?**
A: No — Instagram immediately blocks new/bot accounts. Use a real account with a history.

**Q: How long does a 401 block last?**
A: Usually 15 minutes to 1 hour. Repeated violations can extend it to 24+ hours.

**Q: Is there a way to bypass Instagram's blocking?**
A: Not reliably. Instagram is actively maintained anti-scraping measures. Focus on legitimate sources (websites with recipes) instead.

**Q: Should I report this as a bug?**
A: No — this is Instagram's intended behavior to prevent scraping. The module handles errors correctly.
