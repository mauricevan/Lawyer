"""Document deep-dive endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.database import SessionLocal
from backend.src.models.tables import Document
from ingestion.src.clients.cellar_rest_client import CellarRestClient
from ingestion.src.clients.sparql_client import SparqlClient

router = APIRouter(prefix="/documents", tags=["documents"])
cellar = CellarRestClient()
sparql = SparqlClient()


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


@router.get("/{celex}")
async def get_document(
    celex: str,
    session: AsyncSession = Depends(get_db),
) -> dict:
    result = await session.execute(
        select(Document).where(Document.celex == celex)
    )
    docs = result.scalars().all()
    if not docs:
        raise HTTPException(status_code=404, detail="Document niet gevonden")
    versions = [
        {
            "celex": d.celex,
            "title": d.title,
            "language": d.language,
            "is_consolidated": d.is_consolidated,
            "is_in_force": d.is_in_force,
            "version_type": d.version_type,
            "oj_reference": d.oj_reference,
            "eurlex_url": cellar.build_eurlex_url(d.celex),
        }
        for d in docs
    ]
    relations = await sparql.fetch_document_relations(celex)
    return {
        "celex": celex,
        "versions": versions,
        "relations": relations,
        "eurlex_url": cellar.build_eurlex_url(celex),
    }


@router.get("")
async def list_documents(
    session: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
) -> dict:
    result = await session.execute(
        select(Document).offset(offset).limit(limit)
    )
    docs = result.scalars().all()
    total_result = await session.execute(select(Document))
    total = len(total_result.scalars().all())
    return {
        "total": total,
        "documents": [
            {
                "celex": d.celex,
                "title": d.title,
                "short_title": d.short_title,
                "is_in_force": d.is_in_force,
                "language": d.language,
            }
            for d in docs
        ],
    }
