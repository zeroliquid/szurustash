from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class SauceNAOResultHeader(BaseModel):
    similarity: Optional[float]
    thumbnail: Optional[str]
    index_id: Optional[int]
    index_name: Optional[str]
    dupe: Optional[int] = 0
    hidden: Optional[int] = 0


class SauceNAOResult(BaseModel):
    header: SauceNAOResultHeader
    data: Dict[str, Any]


class SauceNAOResponseHeader(BaseModel):
    user_id: Optional[str]
    account_type: Optional[str]
    short_limit: Optional[int]
    long_limit: Optional[int]
    short_remaining: Optional[int]
    long_remaining: Optional[int]
    status: Optional[int]
    results_requested: Optional[int]
    minimum_similarity: Optional[float]


class SauceNAOResponse(BaseModel):
    header: SauceNAOResponseHeader
    results: List[SauceNAOResult]
