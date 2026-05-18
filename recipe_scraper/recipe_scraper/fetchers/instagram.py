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

    Parameters
    ----------
    post_url : str
        Full URL, e.g. "https://www.instagram.com/p/ABC123/"
    username : str, optional
        Instagram username. Avoids rate-limiting; required for private posts.
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
        If Instagram refuses the request (private, rate-limited, etc.).
    """
    match = re.search(r"/p/([A-Za-z0-9_-]+)", post_url)
    if not match:
        raise ValueError(
            f"No Instagram shortcode found in URL: {post_url}\n"
            "Expected: https://www.instagram.com/p/SHORTCODE/"
        )
    shortcode = match.group(1)

    logger.debug(f"Fetching Instagram post: {shortcode}")
    loader = instaloader.Instaloader(download_pictures=False)

    if username and password:
        logger.debug(f"Logging in as {username}...")
        loader.login(username, password)

    post = instaloader.Post.from_shortcode(loader.context, shortcode)
    caption = post.caption

    if not caption:
        raise ValueError(f"Post {shortcode} has no caption text.")

    logger.info(f"Fetched Instagram post: {shortcode} ({len(caption)} chars)")
    return caption
