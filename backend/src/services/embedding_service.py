"""Embedding generation — local sentence-transformers or OpenAI."""
import logging
from functools import lru_cache

from backend.src.config import settings

logger = logging.getLogger(__name__)

MODEL_NAME = "intfloat/multilingual-e5-large"
EMBEDDING_DIM = 1024


class EmbeddingService:
    """Generates dense embeddings for chunks and queries."""

    def __init__(self) -> None:
        self._model = None
        self._openai = None

    def embed_texts(self, texts: list[str], is_query: bool = False) -> list[list[float]]:
        if settings.use_local_embeddings:
            return self._embed_local(texts, is_query)
        return self._embed_openai(texts)

    def embed_query(self, query: str) -> list[float]:
        prefixed = f"query: {query}"
        return self.embed_texts([prefixed], is_query=True)[0]

    def embed_passages(self, passages: list[str]) -> list[list[float]]:
        prefixed = [f"passage: {p}" for p in passages]
        return self.embed_texts(prefixed)

    def _embed_local(self, texts: list[str], is_query: bool) -> list[list[float]]:
        model = self._get_local_model()
        return model.encode(texts, normalize_embeddings=True).tolist()

    def _embed_openai(self, texts: list[str]) -> list[list[float]]:
        from openai import OpenAI
        client = OpenAI(api_key=settings.openai_api_key)
        response = client.embeddings.create(
            model="text-embedding-3-large",
            input=texts,
            dimensions=EMBEDDING_DIM,
        )
        return [item.embedding for item in response.data]

    def _get_local_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading embedding model: %s", MODEL_NAME)
            self._model = SentenceTransformer(MODEL_NAME)
        return self._model


@lru_cache
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()
