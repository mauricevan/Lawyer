"""Curated EUR-Lex corpus for prototype and scaled ingestion."""
from ingestion.src.data.curated_loader import load_curated_documents

SEED_DOCUMENTS: list = load_curated_documents()
