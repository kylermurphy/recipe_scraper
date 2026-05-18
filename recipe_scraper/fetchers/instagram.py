"""Fetch recipe captions from Instagram posts."""

import re

import instaloader

from ..utils import get_logger

logger = get_logger("fetchers.instagram")


def fetch_instagram_caption(
    post_url: str, username: str = None, password: str = None
) -> str:
    """
    Fetch the caption of an Instagram post via instaloader.

    ⚠️  NOTE: Instagram actively blocks scraping. For reliable access:
       1. Use valid Instagram credentials (username + password)
       2. Add delays between requests
       3. Handle rate-limit errors gracefully

    Parameters
    ----------
    post_url : str
        Full URL, e.g. "https://www.instagram.com/p/ABC123/"
    username : str, optional
        Instagram username. STRONGLY RECOMMENDED to avoid rate-limiting.
        Required for private posts.
    password : str, optional
        Only used if username is also provided.

    Returns
    -------
    str
        The raw caption text.

    Raises
    ------
    ValueError
        If no shortcode is found in the URL, or the post has no caption.
    instaloader.exceptions.InstaloaderException
        If Instagram refuses the request (rate-limited, blocked, etc.).
        This is common when fetching without login credentials.
    """
    match = re.search(r"/p/([A-Za-z0-9_-]+)", post_url)
    if not match:
        raise ValueError(
            f"No Instagram shortcode found in URL: {post_url}\n"
            "Expected: https://www.instagram.com/p/SHORTCODE/"
        )
    shortcode = match.group(1)

    logger.debug(f"Fetching Instagram post: {shortcode}")

    if not username:
        logger.warning(
            "No Instagram credentials provided. Instagram may block this request. "
            "Use --username and --password to improve reliability."
        )

    loader = instaloader.Instaloader(
        download_pictures=False,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    )

    if username and password:
        logger.debug(f"Logging in as {username}...")
        try:
            loader.login(username, password)
        except instaloader.exceptions.BadCredentialsException:
            raise ValueError(f"Invalid Instagram credentials for user {username}")
        except instaloader.exceptions.InstaloaderException as exc:
            raise ValueError(f"Failed to login to Instagram: {exc}")

    try:
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        caption = post.caption

        if not caption:
            raise ValueError(f"Post {shortcode} has no caption text.")

        logger.info(f"Fetched Instagram post: {shortcode} ({len(caption)} chars)")
        return caption

    except instaloader.exceptions.QueryReturnedNotFoundException:
        raise ValueError(
            f"Instagram post not found: {shortcode}\n"
            "The post may be deleted, private, or the URL may be incorrect."
        )
    except instaloader.exceptions.ConnectionException as exc:
        error_msg = str(exc)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise ValueError(
                f"Instagram blocked the request (401 Unauthorized).\n"
                f"This typically means:\n"
                f"  - You're being rate-limited (try again in a few minutes)\n"
                f"  - Instagram detected automated access\n"
                f"  - Your IP/session is temporarily blocked\n\n"
                f"Solutions:\n"
                f"  1. Wait a few minutes and try again\n"
                f"  2. Use valid Instagram credentials: --username <user> --password <pass>\n"
                f"  3. Use a VPN or different network\n"
                f"  4. Check if the post is public"
            ) from exc
        elif "429" in error_msg or "Too Many Requests" in error_msg:
            raise ValueError(
                f"Instagram rate-limited the request (429 Too Many Requests).\n"
                f"Wait a few minutes before trying again."
            ) from exc
        else:
            raise ValueError(
                f"Instagram connection error: {error_msg}\n"
                f"Try again later or use credentials: --username <user> --password <pass>"
            ) from exc
    except Exception as exc:
        raise ValueError(f"Error fetching Instagram post: {exc}") from exc
