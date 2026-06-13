import json
import logging

from fastmcp import FastMCP
from pydantic import Field

from .service import RedditClient

logger = logging.getLogger("reddit-mcp-server")


def register_tools(mcp: FastMCP) -> None:
    """Register all Reddit MCP Tools"""

    # ========= Listing and Search Tools ==========

    @mcp.tool(
        name="reddit_fetch_posts_from_subreddit",
        description="Fetch posts from any subreddit via a simple HTTP GET. Supports all Reddit sort tabs — New, Hot, Top, Rising, Controversial, Best — plus timeframe, cursor.",
    )
    async def reddit_fetch_posts_from_subreddit(
        subreddit: str = Field(..., description="Subreddit name"),
        sort: str = Field(
            "new",
            description="Sort Key (new (default) | hot | top | rising | controversial | best)",
        ),
        t: str = Field(
            "all",
            description="Timeframe for sort=top/controversial: hour | day | week | month | year | all",
        ),
        limit: int = Field(
            25, description="Number of posts to return, 1-100 (default 25)"
        ),
        after: str = Field("", description="Pagination cursor (e.g. t3_xxx)"),
    ) -> str:
        """Fetch posts from any subreddit via a simple HTTP GET. Supports all Reddit sort tabs — New, Hot, Top, Rising, Controversial, Best — plus timeframe, cursor."""
        try:
            client = RedditClient()

            result = await client.fetch_posts_from_subreddit(
                subreddit=subreddit, sort=sort, t=t, limit=limit, after=after
            )

            output = {
                "success": True,
                "posts": result.get("posts"),
            }

            logger.info(f"Fetched post from subreddit {subreddit}")
            return json.dumps(output, indent=2)
        except Exception as e:
            logger.error(f"Failed to get subreddit posts: {e}", exc_info=True)
            return json.dumps({"success": False, "error": str(e)})


    @mcp.tool(
        name="reddit_get_search_posts",
        description="Search Reddit posts globally or restrict to a subreddit — mirrors the Posts tab on reddit.com search. Supports sort, timeframe, NSFW filter, and pagination.",
    )
    async def reddit_get_search_posts(
        q: str = Field(..., description="Search query"),
        subreddit: str = Field(..., description="Restrict to a subreddit"),
        sort: str = Field(..., description="relevance | new | hot | top | comments"),
        t: str = Field(..., description="hour | day | week | month | year | all"),
        limit: int = Field(
            ..., description="Number of posts to return, 1-100 (default 25)"
        ),
        nsfw: bool = Field(..., description="true to include NSFW (Safe Search off)"),
        after: str = Field(..., description="Pagination cursor"),
    ) -> str:
        """Search Reddit Posts Globally or by Subreddit"""
        try:
            client = RedditClient()
            result = await client.get_search_posts(
                q=q,
                subreddit=subreddit,
                sort=sort,
                t=t,
                limit=limit,
                nsfw=nsfw,
                after=after,
            )
            posts = result.get("posts") or []
            output = {
                "success": True,
                "posts": posts,
                "count": len(posts),
                "after": result.get("after"),
            }

            logger.info(f"Searched Posts, found {output['count']} results")
            return json.dumps(output, indent=2)
        except Exception as e:
            logger.error(f"Failed to search posts: {e}", exc_info=True)
            return json.dumps({"success": False, "error": str(e)})

    @mcp.tool(
        name="get_top_posts_in_subreddit",
        description="Get the top posts in any subreddit for a timeframe — day, week, month, year, or all-time. Alias for /api/reddit/posts with sort=top, with cursor pagination."
    )
    async def reddit_get_top_posts(name: str = Field(..., description="Subreddit name"), t: str = Field(..., description="day | week (default) | month | year | all"), limit: int = Field(..., description="Number of posts to return, 1-100 (default 25)"), after: str = Field(..., description="Pagination cursor")) -> str:
        try:
            client = RedditClient()
            result = await client.get_top_posts(name = name, t = t, limit = limit, after = after)
            posts = result.get("posts") or []
            output = {
                "success": True,
                "posts": posts,
                "count": len(posts),
                "after": result.get("after")
            }

            logger.info(f"Got top posts from subreddit: {name}, got {output['count']} results")
            return json.dumps(output, indent=2)
        except Exception as e:
            logger.error(f"Failed to get top posts: {e}", exc_info=True)
            return json.dumps({"success": False, "error": str(e)})

    # # ========= Posts Tools ==========

    @mcp.tool(
        name="get_post_by_id",
        description="Fetch a single Reddit post by post id — all content, metadata, author info, vote counts, and crosspost origin in one HTTP GET call."
    )
    async def reddit_get_post_by_id(post_id: str = Field(..., description="Reddit post id (e.g. 1sgjld3)")):
        try:
            client = RedditClient()
            result = await client.get_post_by_id(post_id=post_id)
            post = result.get("post")
            output = {
                "success": True,
                "post": result.get("post")
            }

            logger.info(f"got the post from subreddit: {post}")
            return json.dumps(output, indent=2)
        except Exception as e:
            logger.error(f"Failed to get the post: {e}", exc_info=True)
            return json.dumps({"success": False, "error": str(e)})

    @mcp.tool(
        name="get_post_comments",
        description="Fetch the full comment tree for a Reddit post by permalink — every top-level comment, nested reply, upvotes, and author metadata in one HTTP GET call."
    )
    async def reddit_get_post_comments(permalink: str = Field(..., description="Post permalink (e.g. /r/X/comments/abc/title/)")) -> str:
        try:
            client = RedditClient()
            result = await client.get_post_comments(permalink=permalink)

            post = result.get("post")
            comments = result.get("comments") or []
            after = result.get("after")

            output = {
                "success": True,
                "post": post,
                "comments": comments,
                "count_comments": len(comments),
                "after": after
            }

            logger.info(f"got the comments for the post {output['post']} with {output['count_comments']} comments")
            return json.dumps(output, indent = 2)
        except Exception as e:
            logger.error(f"Failed to get the comments: {e}", exc_info=True)
            return json.dumps({"success": False, "error": str(e)})


    # # ========= Users Tools ==========

    @mcp.tool(
        name="get_user_profile",
        description="Fetch a Reddit user's full profile by username — karma sub-buckets, account creation date, employee/gold/verified flags, profile icon, banner, bio, and profile-sub metadata."
    )
    async def reddit_get_user_profile(username: str = Field(..., description="Reddit username (no u/ prefix)")):
        try:
            client = RedditClient()
            result = await client.get_user_profile(username=username)

            output = {
                "success": True,
                "data": result,
            }

            logger.info(f"Got the user profile, based on username, {output.get("data")}")
            return json.dumps(output, indent = 2)
        except Exception as e:
            logger.error(f"Failed to get user profile: {e}", exc_info=True)
            return json.dumps({"success": False, "error": str(e)})

    @mcp.tool(
        name="get_user_comments",
        description="Fetch a Reddit user's recent comments by username — sorted by new, top, or controversial. Includes comment body, upvotes, subreddit, and cursor pagination."
    )
    async def reddit_get_user_comments(username: str = Field(..., description="Reddit username"), sort: str = Field(..., description="new (default) | top | controversial"), limit: int = Field(..., description="Number of comments to return, 1-100 (default 25)"), after: str = Field(..., description="Pagination cursor")) -> str:
        try:
            client = RedditClient()
            result = await client.get_user_comments(username=username, sort=sort, limit=limit, after=after)

            comments = result.get("comments") or []

            output = {
                "success": True,
                "comments": comments,
                "after": result.get("after"),
                "count": len(comments)
            }

            logger.info(f"Got {len(comments)} comments, based on username {username}")
            return json.dumps(output, indent = 2)
        except Exception as e:
            logger.error(f"Failed to get user comments: {e}", exc_info=True)
            return json.dumps({"success": False, "error": str(e)})

    # # ========= Search by Type Tools ==========

    @mcp.tool(
        name = "reddit_search_communities",
        description="Search subreddits by name or topic — the Communities tab on reddit.com. Verified to match Reddit's UI rank order for SFW and NSFW queries, with pagination."
    )
    async def reddit_get_search_communities(q: str = Field(..., description="Search query"), nsfw: bool = Field(..., description="true to include NSFW communities"), limit: int = Field(..., description="Number of communities to return, 1-100 (default 25)"), after: str = Field(..., description="Pagination cursor")) -> str:
        try:
            client = RedditClient()
            result = await client.get_search_communities(q = q, nsfw = nsfw, limit = limit, after = after)

            communities = result.get("communities") or []

            output = {
                "success": True,
                "communities": communities,
                "after": result.get("after"),
                "count": len(communities)
            }

            logger.info(f"Got {len(communities)} communities")
            return json.dumps(output, indent = 2)

        except Exception as e:
            logger.error(f"Failed to get communities: {e}", exc_info=True)
            return json.dumps({"success": False, "error": str(e)})

    # # ========= Auth Tools ==========

    @mcp.tool(
        name="reddit_api_login",
        description="Reddit API login endpoint - authenticate to Reddit with username and password and get the full set of session cookies for /comment, /vote, and /dm calls."
    )
    async def reddit_post_login(username: str = Field(..., description="Reddit username or email"), password: str = Field(..., description="Account password"), totp_secret: str = Field(..., description="Base32 TOTP secret for accounts with 2FA enabled. The 6-digit code is generated server-side. Omit if 2FA is off."), method: str = Field(..., description="http (default) or browser. Use browser for the most compatible write-session cookies, especially when you plan to call /vote.")) -> str:
        try:
            client = RedditClient()
            login_data = {
                "username": username,
                "password": password,
                "totp_secret": totp_secret,
                "method": method
            }
            result = await client.post_reddit_api_login(login_data=login_data)

            output = result
            logger.info(f"Got login details {output}")
            return json.dumps(output, indent = 2)
        except Exception as e:
            logger.error(f"Failed to get login details: {e}", exc_info=True)
            return json.dumps({"success": False, "error": str(e)})

    # # ========= Profile Tools ==========

    @mcp.tool(
        name="reddit_update_bio",
        description="Update the logged-in Reddit account's profile bio (publicDescription) via HTTP — plain text up to 200 characters, Needs reddit_session cookie, from reddit_api_login tool"
    )
    async def reddit_post_update_bio(description: str = Field(..., description="New bio — plain text, ≤ 200 chars"), reddit_session: str = Field(..., description="Session cookie from /api/reddit/login"), csrf_token: str = Field(..., description="Anti-CSRF cookie"), loid: str = Field(..., description="Account loid cookie (recommended)"), token_v2: str = Field(..., description="token_v2 cookie"), edgebucket: str = Field(..., description="edgetbucket cookie"), csv: str = Field(..., description="csv cookie"), session_tracker: str = Field(..., description="session_tracker cookie"), proxy: object = Field(..., description="Sticky IP for this account — match the proxy you used for /api/reddit/login"), max_attempts: int = Field(..., description="Retry budget (default 3)")) -> str:
        try:
            client=RedditClient()
            description_data = {
                "description": description,
                "reddit_session": reddit_session,
                "csrf_token": csrf_token,
                "loid": loid,
                "token_v2": token_v2,
                "edgebucket": edgebucket,
                "csv": csv,
                "session_tracker": session_tracker,
                "proxy": proxy,
                "max_attempts": max_attempts
            }
            result = await client.post_update_bio(description=description_data)

            logger.info(f"Got the details for profile: {result}")
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"Failed to get bio: {e}", exc_info=True)
            return json.dumps({"success": False, "error": str(e)})

    # ========= Account Tools ==========
    @mcp.tool(
        name="get_my_account",
        description="Get your account info, remaining credit balance, total credits used, and request count."
    )
    async def reddit_get_my_account():
        try:
            client = RedditClient()
            result = await client.get_my_account()

            output = {
                "success": True,
                "data": result,
            }

            logger.info(f"Got user details {output}")
            return json.dumps(output, indent = 2)

        except Exception as e:
            logger.error(f"Failed to get account details: {e}", exc_info=True)
            return json.dumps({"success": False, "error": str(e)})

    @mcp.tool(
        name="getpayment_history",
        description="List the top-ups and payments made to your account, sorted newest first. Free to call — useful for invoicing, accounting, and reconciling credit purchases."
    )
    async def reddit_getpayment_history() -> str:
        try:
            client = RedditClient()
            result = await client.getpayment_history()
            payments = result.get("payments") or []

            output = {
                "success": True,
                "payments": payments,
                "count": len(payments),
            }
            logger.info(f"Got {len(payments)} records from payment history")
            return json.dumps(output, indent=2)
        except Exception as e:
            logger.error(f"Failed to get payment history: {e}", exc_info=True)
            return json.dumps({"success": False, "error": str(e)})


    # # ========== Utility Tools ==========

    @mcp.tool(
        name="reddit_health_check",
        description="Check server readiness and basic connectivity.",
    )
    def reddit_health_check() -> str:
        """Health check endpoint."""
        return json.dumps(
            {
                "status": "ok",
                "server": "CL Reddit MCP Server",
                "type": "third-party integration",
                "auth_required": "for all endpoints",
            }
        )
