"""Normalize query requests before retrieval and answer generation."""
from backend.src.services.language_resolution_service import LanguageResolutionService
from shared.schemas.query import QueryRequest

_AUTO = "auto"
_resolver = LanguageResolutionService()


def normalize_query_request(request: QueryRequest) -> QueryRequest:
    """Resolve auto/unknown language codes to an enabled retrieval language."""
    resolved = _resolver.resolve(request.language, request.question)
    if resolved == request.language and not _filter_language_is_auto(request):
        return request
    updates: dict = {"language": resolved}
    if request.filters and request.filters.language:
        filter_lang = _resolver.resolve(request.filters.language, request.question)
        if filter_lang != request.filters.language:
            updates["filters"] = request.filters.model_copy(update={"language": filter_lang})
    return request.model_copy(update=updates)


def _filter_language_is_auto(request: QueryRequest) -> bool:
    return bool(request.filters and request.filters.language == _AUTO)
