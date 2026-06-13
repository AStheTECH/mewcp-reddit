import json

from click import argument
import pytest
from mcp.types import TextContent
from fastmcp import Client

import os

from server import mcp

@pytest.mark.asyncio
async def test_reddit_fetch_posts_from_subreddit():
    """Verify Fetch posts from any subreddit"""
    async with Client(mcp) as client:
        response = await client.call_tool(
            "reddit_fetch_posts_from_subreddit",
            arguments={"api_key": os.environ.get("api_key"), "subreddit": "GATEtards", "sort": "all", "t": "all", "limit": 1, "after": ""}
        )

        posts = response.structured_content.get("posts") or []
        assert response is not None
        assert len(posts) != 0




