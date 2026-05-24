import base64

from yarl import URL
import aiohttp

from szurustash.exceptions import SzurubooruError

from .models import Post, PagedPostResponse


class SzurubooruClient:
    """Minimal async client for the Szurubooru API."""

    def __init__(
        self,
        base_url: str,
        username: str,
        api_token: str,
        default_page_size: int = 25,
        timeout_seconds: float = 30,
    ) -> None:
        self.base_url = URL(str(base_url).rstrip("/"))
        self.default_page_size = default_page_size
        self.timeout = aiohttp.ClientTimeout(total=timeout_seconds)

        self.headers = {
            "Accept": "application/json",
            "Authorization": self._auth_token(username, api_token),
        }

        self._session: aiohttp.ClientSession | None = None

    @staticmethod
    def _auth_token(username: str, api_token: str) -> str:
        raw = f"{username}:{api_token}".encode("utf-8")
        return "Token " + base64.b64encode(raw).decode("ascii")

    async def __aenter__(self) -> "SzurubooruClient":
        self._session = aiohttp.ClientSession(headers=self.headers, timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._session is not None:
            await self._session.close()
            self._session = None


    async def get_posts(self, query: str = "", limit: int | None = None, offset: int = 0) -> PagedPostResponse:
        limit = limit or self.default_page_size
        url = self.base_url / "api" / "posts"
        params = {"query": query, "limit": limit, "offset": offset}

        async with self._session.get(url, params=params) as response:
            payload = await response.json()
            if response.status >= 400:
                raise SzurubooruError(
                    f"Szurubooru API error {response.status}: {payload}"
                )
            return PagedPostResponse.model_validate(payload)

    async def get_post(self, post_id: int) -> Post:
        url = self.base_url / "api" / "post" / str(post_id)

        async with self._session.get(url) as response:
            payload = await response.json()
            if response.status >= 400:
                raise SzurubooruError(
                    f"Szurubooru API error {response.status}: {payload}"
                )
            return Post.model_validate(payload)
