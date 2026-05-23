from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel


def to_camel(string: str) -> str:
    parts = string.split("_")
    return parts[0] + "".join(part.capitalize() for part in parts[1:])


class Tag(BaseModel):
    names: List[str] = []


class Post(BaseModel):
    id: int
    version: int | None = None
    creation_time: datetime | None = None
    last_edit_time: datetime | None = None
    safety: str | None = None
    source: str | None = None
    type: str | None = None
    mime_type: str | None = None
    checksum: str | None = None
    checksum_md5: str | None = None
    file_size: int | None = None
    canvas_width: int | None = None
    canvas_height: int | None = None
    content_url: str | None = None
    thumbnail_url: str | None = None
    flags: List[str] = []
    tags: List[Tag] = []

    model_config = {
        "populate_by_name": True,
        "alias_generator": to_camel,
        "extra": "ignore",
    }


class PagedPostResponse(BaseModel):
    query: str
    offset: int
    limit: int
    total: int
    results: List[Post] = []

    model_config = {
        "populate_by_name": True,
        "alias_generator": to_camel,
        "extra": "ignore",
    }
