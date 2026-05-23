from __future__ import annotations

import base64
from pathlib import Path

from yarl import URL

import aiohttp

from .models import Post, PagedPostResponse


class SzurubooruClient:
    def __init__(
        self,
        base_url: str,
        username: str,
        api_token: str,
        default_page_size: int = 25,
    ) -> None:
        self.base_url = URL(str(base_url).rstrip("/"))
        self.default_page_size = default_page_size
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": self._auth_token(username, api_token),
        }

    @staticmethod
    def _auth_token(username: str, api_token: str) -> str:
        raw = f"{username}:{api_token}".encode("utf-8")
        return "Token " + base64.b64encode(raw).decode("ascii")

    async def get_posts(
        self,
        query: str = "",
        limit: int | None = None,
        offset: int = 0,
    ) -> PagedPostResponse:
        limit = limit or self.default_page_size
        url = self.base_url / "api" / "posts"
        params = {"query": query, "limit": limit, "offset": offset}

        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url, params=params) as response:
                payload = await response.json()
                if response.status >= 400:
                    raise RuntimeError(
                        f"Szurubooru API error {response.status}: {payload}"
                    )
                return PagedPostResponse.model_validate(payload)

    async def get_post(self, post_id: int) -> Post:
        url = self.base_url / "api" / "post" / str(post_id)

        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as response:
                payload = await response.json()
                if response.status >= 400:
                    raise RuntimeError(
                        f"Szurubooru API error {response.status}: {payload}"
                    )
                return Post.model_validate(payload)

    async def download_media(self, media_url: str, destination: Path) -> Path:
        destination = destination.expanduser()
        destination.parent.mkdir(parents=True, exist_ok=True)
        url = self._absolute_url(media_url)

        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as response:
                if response.status >= 400:
                    payload = await response.text()
                    raise RuntimeError(
                        f"Szurubooru media download failed {response.status}: {payload}"
                    )

                with destination.open("wb") as out_file:
                    async for chunk in response.content.iter_chunked(65536):
                        out_file.write(chunk)

        return destination

    async def download_post_content(self, post: Post, destination_dir: Path) -> Path:
        if not post.content_url:
            raise ValueError("Post does not contain a content URL.")

        file_name = Path(post.content_url).name
        target_path = destination_dir.expanduser() / file_name
        return await self.download_media(post.content_url, target_path)

    def _absolute_url(self, media_url: str) -> str:
        if media_url.startswith("http://") or media_url.startswith("https://"):
            return media_url
        return str(self.base_url / media_url.lstrip("/"))

