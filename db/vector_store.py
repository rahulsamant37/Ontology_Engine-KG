from __future__ import annotations

from dataclasses import dataclass

from langchain_community.embeddings import FakeEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

from utils.config import settings


@dataclass
class VectorRecord:
    text: str
    metadata: dict[str, str]


class VectorIndex:
    def __init__(self) -> None:
        self._embeddings = FakeEmbeddings(size=1536)
        self._store = Chroma(
            collection_name="ontology_engine",
            embedding_function=self._embeddings,
            persist_directory=settings.vector_dir,
        )

    def add(self, records: list[VectorRecord]) -> None:
        docs = [Document(page_content=r.text, metadata=r.metadata) for r in records]
        if docs:
            self._store.add_documents(docs)

    def search(self, query: str, k: int | None = None) -> list[Document]:
        return self._store.similarity_search(query, k=k or settings.top_k_retrieval)
