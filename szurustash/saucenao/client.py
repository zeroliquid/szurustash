from pathlib import Path
import io

from yarl import URL
import aiohttp

from .models import SauceNAOResponse


class SauceNAOClient:
    """Minimal async client for the SauceNAO API."""

    def __init__(
        self,
        api_key: str,
        base_url: URL = URL("https://saucenao.com") / "search.php",
        default_numres: int = 16,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url
        self.default_numres = default_numres
        self._session: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> "SauceNAOClient":
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._session:
            await self._session.close()
            self._session = None

    async def search_url(
        self,
        image_url: str,
        *,
        db: int | None = None,
        dbs: list[int] | None = None,
        dbmask: int | None = None,
        numres: int | None = None,
        testmode: bool = False,
        dedupe: int | None = None,
        hide: int | None = None,
    ) -> SauceNAOResponse:
        """Search SauceNAO by remote image URL.

        All parameters map directly to SauceNAO query parameters; only the
        `image_url` and the client's `api_key` are required.
        """

        params: dict = {
            "output_type": 2,
            "api_key": self.api_key,
            "url": image_url,
            "numres": numres or self.default_numres,
        }
        if testmode:
            params["testmode"] = 1
        if db is not None:
            params["db"] = db
        if dbmask is not None:
            params["dbmask"] = dbmask
        if dedupe is not None:
            params["dedupe"] = dedupe
        if hide is not None:
            params["hide"] = hide
        # handle repeated dbs[] parameters
        if dbs is not None:
            # aiohttp accepts list values to emit multiple query params
            params["dbs[]"] = list(dbs)

        async with self._session.get(self.base_url, params=params) as resp:
            text = await resp.text()
            resp.raise_for_status()
            payload = await resp.json()
            return SauceNAOResponse.model_validate(payload)

    async def search_stream(
        self,
        image_stream: io.BytesIO,
        *,
        filename: str = "image.png",
        db: int | None = None,
        dbs: list[int] | None = None,
        dbmask: int | None = None,
        numres: int | None = None,
        testmode: bool = False,
        dedupe: int | None = None,
        hide: int | None = None,
    ) -> SauceNAOResponse:
        """Upload an image stream (BytesIO) to SauceNAO via multipart POST.

        Other query params are the same as `search_url`.
        """

        params: dict = {
            "output_type": 2,
            "api_key": self.api_key,
            "numres": numres or self.default_numres,
        }
        if testmode:
            params["testmode"] = 1
        if db is not None:
            params["db"] = db
        if dbmask is not None:
            params["dbmask"] = dbmask
        if dedupe is not None:
            params["dedupe"] = dedupe
        if hide is not None:
            params["hide"] = hide
        if dbs is not None:
            params["dbs[]"] = list(dbs)

        # ensure stream is at start
        try:
            image_stream.seek(0)
        except Exception:
            pass

        data = aiohttp.FormData()
        data.add_field("file", image_stream, filename=filename, content_type="application/octet-stream")

        async with self._session.post(self.base_url, params=params, data=data) as resp:
            text = await resp.text()
            resp.raise_for_status()
            payload = await resp.json()
            return SauceNAOResponse.model_validate(payload)

    async def search_file(self, path: Path, **kwargs) -> SauceNAOResponse:
        """Convenience wrapper to search by local file path."""
        path = Path(path).expanduser()
        with path.open("rb") as fh:
            stream = io.BytesIO(fh.read())
        return await self.search_stream(stream, filename=path.name, **kwargs)
