"""Reusable validation patterns for shared API schemas."""

UUID_PATTERN = (
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)
CELEX_PATTERN = r"^\d{5}[A-Z]\d{4}([A-Z()0-9]+)?$"
LANGUAGE_PATTERN = r"^(auto|[a-z]{2}(-[A-Z]{2})?)$"
FILTER_TEXT_PATTERN = r"^[A-Za-z0-9 _./-]{0,64}$"
