"""Merge retrieval result lists without duplicate chunk IDs."""


def merge_deduped_results(*result_groups: list[dict]) -> list[dict]:
    seen: set[str] = set()
    merged: list[dict] = []
    for group in result_groups:
        for result in group:
            chunk_id = result.get("chunk_id")
            if chunk_id and chunk_id not in seen:
                seen.add(chunk_id)
                merged.append(result)
    return merged
