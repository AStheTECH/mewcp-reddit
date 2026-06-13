import json
import logging
from typing import Any, Dict, List, Optional

import httpx
from fastmcp_credentials import get_credentials


from .config import (
    DEFAULT_LIMIT,
    DEFAULT_TIMEOUT,
    ENDPOINTS,
    MAX_LIMIT,
    REDDIT_API_BASE,
    REDDIT_API_NAMESPACE,
)

logger = logging.getLogger("reddit-mcp-server")


class RedditClient:
    """Client for Reddit API."""

    def __init__(self) -> None:
        """Initialize Reddit API Base URL"""
        self.base_url = REDDIT_API_BASE + REDDIT_API_NAMESPACE

    def _build_headers(self) -> Dict[str, str]:
        """Build request headers with Basic Auth."""
        # Reddit uses HTTP Basic Auth with API key
        api_key = get_credentials().fields["api_key"]

        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "x-www-form-urlencoded",
        }

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make an HTTP request to the Reddit API."""
        url = f"{self.base_url}{endpoint}"
        headers = self._build_headers()
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    data=data,
                    params=params,
                    timeout=DEFAULT_TIMEOUT,
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                error_body = e.response.text
                logger.error(
                    f"Reddit API error: {e.response.status_code} - {error_body}"
                )

                # Parse Reddit error response
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get("error", {}).get("message", str(e))
                except:
                    error_msg = error_body

                raise Exception(f"Reddit API error: {error_msg}")

    # =================== Listing and Search ===================

    async def fetch_posts_from_subreddit(
        self,
        subreddit: str,
        sort: Optional[str] = "new",
        t: Optional[str] = "all",
        limit: Optional[int] = 25,
        after: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get posts from a subreddit."""
        params = {
            "subreddit": subreddit,
            "sort": sort,
            "t": t,
            "limit": limit,
            "after": after,
        }
        return await self._request("GET", ENDPOINTS["subreddit_posts"], params=params)

    async def get_search_posts(
        self,
        q: str,
        subreddit: Optional[str],
        sort: Optional[str] = "relevance",
        t: Optional[str] = "all",
        nsfw: Optional[bool] = True,
        limit: Optional[int] = 25,
        after: Optional[str] = "t0",
    ) -> Dict[str, Any]:
        """Search Reddit posts globally"""
        params = {
            "subreddit": subreddit,
            "sort": sort,
            "t": t,
            "nsfw": nsfw,
            "limit": limit,
            "after": after,
        }
        return await self._request("GET", ENDPOINTS["search_posts"], params=params)

    async def get_top_posts(
        self,
        name: str,
        t: Optional[str] = "all",
        limit: Optional[int] = 25,
        after: Optional[str] = "t0",
    ) -> Dict[str, Any]:
        """Get the top posts in any subreddit for a timeframe"""
        params = {"t": t, "limit": limit, "after": after}
        return await self._request(
            "GET", ENDPOINTS["top_posts"].format(name=name), params=params
        )

    # =================== Posts ===================

    async def get_post_by_id(self, post_id: str) -> Dict[str, Any]:
        """Get a Reddit Post by ID"""
        return await self._request("GET", ENDPOINTS["byID"].format(post_id=post_id))

    async def get_post_comments(self, permalink: Optional[str]) -> Dict[str, Any]:
        """Get Reddit Post Comments by Permalink"""
        params = {"permalink": permalink}
        return await self._request("GET", ENDPOINTS["comments"], params=params)

    # =================== Users ===================

    async def get_user_profile(self, username: str) -> Dict[str, Any]:
        """Get a Reddit User Profile and Karma"""
        return await self._request(
            "GET", ENDPOINTS["user_profile"].format(username=username)
        )

    async def get_user_comments(
        self,
        username: str,
        sort: Optional[str] = "new",
        limit: Optional[int] = 25,
        after: Optional[str] = "",
    ) -> Dict[str, Any]:
        """Get a Reddit User's Recent Comments History"""
        params = {"sort": sort, "limit": limit, "after": after}
        return await self._request(
            "GET", ENDPOINTS["user_comments"].format(username=username), params=params
        )

    # =================== Search By Type ===================

    async def get_search_communities(
        self,
        q: str,
        nsfw: Optional[bool] = True,
        limit: Optional[int] = 25,
        after: Optional[str] = "",
    ) -> Dict[str, Any]:
        """Search Subreddits and Communities by Topic"""
        params = {"q": q, "nsfw": nsfw, "limit": limit, "after": after}
        return await self._request(
            "GET", ENDPOINTS["search_communities"], params=params
        )

    # =================== Auth ===================

    async def post_reddit_api_login(self, login_data: Dict[str, Any]) -> Dict[str, Any]:
        """Reddit API Login - Username and Password Authentication"""
        return await self._request(
            "POST", ENDPOINTS["reddit_api_login"], data=login_data
        )

    # =================== Write ===================

    async def post_comment(self, comment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Post Reddit Comments"""
        return await self._request("POST", ENDPOINTS["comment"], data=comment_data)

    async def post_vote(self, vote_data: Dict[str, Any]) -> Dict[str, Any]:
        """Upvote or Downvote Reddit Posts and Comments"""
        return await self._request("POST", ENDPOINTS["vote"], data=vote_data)

    # =================== DM ===================

    async def post_send_dm(self, dm_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send a Reddit Direct Message via HTTP"""
        return await self._request("POST", ENDPOINTS["send_dm"], data=dm_data)

    async def post_list_dm_threads(
        self, list_threads_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """List All Direct Message Threads & Inbox"""
        return await self._request(
            "POST", ENDPOINTS["list_dm_threads"], data=list_threads_data
        )

    async def post_fetch_messages(self, dm_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch a Direct Message Thread's Full History"""
        return await self._request("POST", ENDPOINTS["fetch_messages"], data=dm_data)

    # =================== Profile ===================

    async def post_update_bio(self, description: Dict[str, Any]) -> Dict[str, Any]:
        """Update a Reddit Account Bio"""
        return await self._request("POST", ENDPOINTS["update_bio"], data=description)

    async def post_set_display_name(
        self, display_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Set a Reddit Profile Display Name (Not Username)"""
        return await self._request(
            "POST", ENDPOINTS["set_display_name"], data=display_data
        )

    async def post_upload_avatar(self, image_data: Dict[str, Any]) -> Dict[str, Any]:
        """Upload a Reddit Profile Avatar or Banner Image"""
        return await self._request("POST", ENDPOINTS["upload_avatar"], data=image_data)

    # =================== Account ===================

    async def get_my_account(self) -> Dict[str, Any]:
        """Get Account Info, Balance, and Usage Summary"""
        return await self._request("GET", ENDPOINTS["my_account"])

    async def getpayment_history(self) -> Dict[str, Any]:
        """List Account Top-up and Payment History"""
        return await self._request("GET", ENDPOINTS["payment_history"])
