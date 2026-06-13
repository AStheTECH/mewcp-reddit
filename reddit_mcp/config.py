import logging

REDDIT_API_BASE = "https://api.redditapis.com"
REDDIT_API_NAMESPACE = "/api/reddit"

ENDPOINTS = {
    # Listings and Search
    "subreddit_posts": "/posts",
    "search_posts": "/search",
    "top_posts": "/sub/{name}/top",
    # Posts
    "byID": "/post/{post_id}",
    "comments": "/comments",
    # Users
    "user_profile": "/user/{username}",
    "user_comments": "/user/{username}/comments",
    # Search by Type
    "search_communities": "/search/communities",
    # Auth
    "reddit_api_login": "/login",
    # Write
    "comment": "/v2/comment",
    "vote": "/vote",
    # DM
    "send_dm": "/dm",
    "list_dm_threads": "/dm/threads",
    "fetch_messages": "/dm/messages",
    # Profile
    "update_bio": "/profile/description",
    "set_display_name": "/profile/display-name",
    "upload_avatar": "/profile/avatar",
    # Account
    "my_account": "/account/me",
    "payment_history": "/account/payments"
}

DEFAULT_LIMIT = 10
MAX_LIMIT = 100
DEFAULT_TIMEOUT = 30


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )
