"""Typed FastAPI path and query parameters with enforced bounds."""
from typing import Annotated

from fastapi import Path, Query

from shared.schemas.validation_patterns import UUID_PATTERN

ConversationIdPath = Annotated[
    str,
    Path(..., min_length=36, max_length=36, pattern=UUID_PATTERN),
]
PageLimit = Annotated[int, Query(ge=1, le=200)]
PageOffset = Annotated[int, Query(ge=0, le=10_000)]
SampleSize = Annotated[int, Query(ge=1, le=500)]
TitleQuery = Annotated[str | None, Query(max_length=200)]
