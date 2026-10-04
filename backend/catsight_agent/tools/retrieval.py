"""Clause retrieval — FR-INGEST-2 and the `search_treaty_clauses` tool.

Two swappable seams, so the shape of the system is settled before GCP access
is and only the backends change afterwards:

  **Embedder** - `DeterministicEmbedder` for tests and local development,
  `GeminiEmbedder` for production. The production one is written but not
  exercised here; see the warning below.

  **VectorStore** - `InMemoryVectorStore` (pure-Python cosine) and
  `FirestoreVectorStore`. Both honour C-11's constraint that **vector
  pre-filters are equality only**, so the same query works against either and
  nothing has to change when the index lands.

## What the local path does and does not prove

It proves the plumbing: chunking, filtering, ranking, the tool's contract,
and the QA harness that scores it. It does **not** prove retrieval quality.
`DeterministicEmbedder` is a hashing bag-of-words with no semantics, so a
recall figure measured against it is a measure of the harness, not of the
system. Numbers for the deck come from `GeminiEmbedder` against a real
Firestore index, and from nothing else.

`clause_type` is a filter of convenience, never a gate. W8 hides its hours
clause inside a clause titled "Definitions", which classifies as OTHER, so a
hard filter on `clause_type == "HOURS"` would miss exactly the case DR-2
planted to catch a lazy extractor.
"""

from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass
from typing import Any, Iterable, Protocol, Sequence, runtime_checkable

from ingest.chunking import Chunk

__all__ = [
    "EMBED_DIM",
    "Embedder",
    "DeterministicEmbedder",
    "GeminiEmbedder",
    "SearchHit",
    "VectorStore",
    "InMemoryVectorStore",
    "FirestoreVectorStore",
    "l2_normalise",
    "cosine",
]

#: C-2. 768 dimensions, matching `gemini-embedding-001`'s configured output,
#: so the local and production vectors are at least the same shape.
EMBED_DIM = 768

_TOKEN = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> list[str]:
    return _TOKEN.findall(text.lower())


def l2_normalise(vector: Sequence[float]) -> list[float]:
    """Unit-length a vector. FR-INGEST-2 requires stored embeddings to be
    L2-normalised, which makes cosine similarity a plain dot product."""
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return [0.0] * len(vector)
    return [value / norm for value in vector]


def cosine(a: Sequence[float], b: Sequence[float]) -> float:
    """Cosine similarity. Assumes nothing about normalisation."""
    if len(a) != len(b):
        raise ValueError(f"dimension mismatch: {len(a)} vs {len(b)}")
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


# --------------------------------------------------------------------------- #
# Embedders
# --------------------------------------------------------------------------- #


@runtime_checkable
class Embedder(Protocol):
    """Anything that turns text into a fixed-width vector."""

    dimensions: int

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]: ...

    def embed_query(self, text: str) -> list[float]: ...


@dataclass
class DeterministicEmbedder:
    """A hashing bag-of-words embedder. **Not semantic.**

    Exists so retrieval, the tool contract and the QA harness can be built and
    tested without a model call or a network. Same text always gives the same
    vector, so tests are stable and cheap.

    It will match on shared vocabulary and nothing else: "hours clause" and
    "loss occurrence" are unrelated to it, though they are the same concept.
    **Never quote a retrieval metric measured against this.** It is scaffolding.
    """

    dimensions: int = EMBED_DIM
    #: Sub-linear term weighting, so a word repeated twenty times does not
    #: dominate the vector.
    sublinear_tf: bool = True

    def _vector(self, text: str) -> list[float]:
        counts: dict[int, float] = {}
        for token in _tokens(text):
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
            bucket = int.from_bytes(digest, "big") % self.dimensions
            counts[bucket] = counts.get(bucket, 0.0) + 1.0
        vector = [0.0] * self.dimensions
        for bucket, count in counts.items():
            vector[bucket] = 1.0 + math.log(count) if self.sublinear_tf else count
        return l2_normalise(vector)

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        return [self._vector(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._vector(text)


@dataclass
class GeminiEmbedder:
    """`gemini-embedding-001` at 768 dimensions (C-2, FR-INGEST-2).

    **Not exercised by the test suite** - it needs a live project. The call
    shape follows RESEARCH_FINDINGS: one input per request with batching done
    by the caller's loop, `output_dimensionality=768`, and `task_type`
    distinguishing a stored document from a query, which materially affects
    retrieval quality and is easy to forget.

    Vectors are L2-normalised here rather than relying on the API to do it,
    so the store's assumptions hold whatever the endpoint returns.
    """

    project: str
    location: str = "global"
    model: str = "gemini-embedding-001"
    dimensions: int = EMBED_DIM
    _client: Any = None

    def _ensure_client(self) -> Any:  # pragma: no cover - needs a live project
        if self._client is None:
            from google import genai

            self._client = genai.Client(
                enterprise=True, project=self.project, location=self.location
            )
        return self._client

    def _embed(self, text: str, task_type: str) -> list[float]:  # pragma: no cover
        from google.genai import types

        client = self._ensure_client()
        response = client.models.embed_content(
            model=self.model,
            contents=text,
            config=types.EmbedContentConfig(
                output_dimensionality=self.dimensions, task_type=task_type
            ),
        )
        return l2_normalise(response.embeddings[0].values)

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:  # pragma: no cover
        return [self._embed(text, "RETRIEVAL_DOCUMENT") for text in texts]

    def embed_query(self, text: str) -> list[float]:  # pragma: no cover
        return self._embed(text, "RETRIEVAL_QUERY")


# --------------------------------------------------------------------------- #
# Stores
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class SearchHit:
    chunk: Chunk
    score: float

    def citation_fields(self) -> dict[str, Any]:
        """The fields a citation needs, so a caller cannot assemble one from
        the wrong chunk's metadata."""
        return {
            "treaty_id": self.chunk.treaty_id,
            "page": self.chunk.page,
            "clause_no": self.chunk.clause_no or "n/a",
            "source": self.chunk.source,
        }


@runtime_checkable
class VectorStore(Protocol):
    def add(self, chunks: Sequence[Chunk], vectors: Sequence[Sequence[float]]) -> int: ...

    def search(
        self,
        query_vector: Sequence[float],
        *,
        treaty_id: str | None = None,
        limit: int = 5,
    ) -> list[SearchHit]: ...


class InMemoryVectorStore:
    """Brute-force cosine search over the stored chunks.

    Exact rather than approximate, and at 8 wordings x ~31 chunks the whole
    corpus is about 250 vectors, so brute force is instant and needs no index
    to be built. That also makes it a useful reference: a recall difference
    between this and Firestore is the index's doing, not the embedder's.

    Pre-filtering is **equality only**, matching C-11, so a query written
    against this store behaves the same against Firestore.
    """

    def __init__(self) -> None:
        self._rows: list[tuple[Chunk, list[float]]] = []

    def __len__(self) -> int:
        return len(self._rows)

    def add(self, chunks: Sequence[Chunk], vectors: Sequence[Sequence[float]]) -> int:
        if len(chunks) != len(vectors):
            raise ValueError(f"{len(chunks)} chunks but {len(vectors)} vectors")
        seen = {chunk.chunk_id for chunk, _ in self._rows}
        added = 0
        for chunk, vector in zip(chunks, vectors):
            if chunk.chunk_id in seen:
                continue  # idempotent: re-ingesting a wording must not duplicate
            self._rows.append((chunk, list(vector)))
            seen.add(chunk.chunk_id)
            added += 1
        return added

    def search(
        self,
        query_vector: Sequence[float],
        *,
        treaty_id: str | None = None,
        limit: int = 5,
    ) -> list[SearchHit]:
        if limit < 1:
            raise ValueError("limit must be >= 1")
        candidates = [
            (chunk, vector)
            for chunk, vector in self._rows
            if treaty_id is None or chunk.treaty_id == treaty_id
        ]
        scored = [
            SearchHit(chunk=chunk, score=cosine(query_vector, vector))
            for chunk, vector in candidates
        ]
        # Tie-break on chunk_id so equal scores order deterministically -
        # otherwise retrieval output wobbles between runs and the ADK eval
        # trajectory check becomes flaky.
        scored.sort(key=lambda hit: (-hit.score, hit.chunk.chunk_id))
        return scored[:limit]


@dataclass
class FirestoreVectorStore:
    """Firestore vector search over `treaty_chunks` (C-11).

    **Not exercised by the test suite** - it needs a live database and an
    index in state READY. Two constraints are baked in rather than discovered
    later: the index is created with **gcloud, not the Firebase CLI**, and
    pre-filters are **equality only**, which is why `treaty_id` is the only
    filter the interface offers.
    """

    client: Any
    collection: str = "treaty_chunks"
    embed_dim: int = EMBED_DIM

    def add(self, chunks: Sequence[Chunk], vectors: Sequence[Sequence[float]]) -> int:  # pragma: no cover
        from google.cloud.firestore_v1.vector import Vector

        if len(chunks) != len(vectors):
            raise ValueError(f"{len(chunks)} chunks but {len(vectors)} vectors")
        collection = self.client.collection(self.collection)
        for chunk, vector in zip(chunks, vectors):
            collection.document(chunk.chunk_id).set(
                {
                    "treaty_id": chunk.treaty_id,
                    "page": chunk.page,
                    "clause_no": chunk.clause_no,
                    "clause_title": chunk.clause_title,
                    "clause_type": chunk.clause_type,
                    "text": chunk.text,
                    "source": chunk.source,
                    "embedding": Vector(list(vector)),
                }
            )
        return len(chunks)

    def search(  # pragma: no cover
        self,
        query_vector: Sequence[float],
        *,
        treaty_id: str | None = None,
        limit: int = 5,
    ) -> list[SearchHit]:
        from google.cloud.firestore_v1.base_vector_query import DistanceMeasure
        from google.cloud.firestore_v1.vector import Vector

        query: Any = self.client.collection(self.collection)
        if treaty_id is not None:
            query = query.where("treaty_id", "==", treaty_id)  # equality only
        results = query.find_nearest(
            vector_field="embedding",
            query_vector=Vector(list(query_vector)),
            distance_measure=DistanceMeasure.COSINE,
            limit=limit,
        ).get()

        hits: list[SearchHit] = []
        for document in results:
            data = document.to_dict()
            hits.append(
                SearchHit(
                    chunk=Chunk(
                        treaty_id=data["treaty_id"],
                        chunk_id=document.id,
                        page=data["page"],
                        clause_no=data.get("clause_no"),
                        clause_title=data.get("clause_title"),
                        clause_type=data.get("clause_type", "OTHER"),
                        text=data["text"],
                        source=data.get("source", "text"),
                    ),
                    score=1.0 - float(data.get("vector_distance", 0.0)),
                )
            )
        return hits


# --------------------------------------------------------------------------- #
# The agent-facing tool
# --------------------------------------------------------------------------- #

#: Canonical queries FR-WORD runs for each matched treaty. Phrased as the
#: clause would read rather than as a keyword, because the production embedder
#: is semantic even though the local one is not.
STANDARD_QUERIES: dict[str, str] = {
    "HOURS": (
        "loss occurrence definition, the number of consecutive hours within which "
        "individual losses are treated as one event"
    ),
    "EXCLUSION": "excluded perils, storm surge, flood written as such, earthquake exclusion",
    "TERRITORY": "territorial scope, which territories and regions are covered or carved out",
    "REINSTATEMENT": "reinstatement of the limit, number of reinstatements and the premium basis",
    "PERIOD": "period of the agreement, inception and expiry, extended expiration",
    "LIMIT": "limit and retention per loss occurrence for each layer",
}


def search_treaty_clauses(
    query: str,
    *,
    store: VectorStore,
    embedder: Embedder,
    treaty_id: str | None = None,
    limit: int = 5,
    clause_type: str | None = None,
) -> list[SearchHit]:
    """Retrieve clauses relevant to a query (the AG-3 tool).

    `clause_type` is applied **after** ranking, as a preference rather than a
    pre-filter: it reorders matching types ahead of others but never removes a
    hit. Dropping non-matching types would lose W8's hours clause, which lives
    in a chunk titled "Definitions".

    Idempotent and side-effect free, as ADK requires of tools, since a failed
    workflow node re-runs on resume.
    """
    if not query.strip():
        raise ValueError("query must not be empty")
    hits = store.search(embedder.embed_query(query), treaty_id=treaty_id, limit=limit * 3)
    if clause_type:
        hits.sort(key=lambda hit: (hit.chunk.clause_type != clause_type, -hit.score))
    return hits[:limit]


def index_chunks(
    chunks: Iterable[Chunk], *, store: VectorStore, embedder: Embedder
) -> int:
    """Embed and store chunks. Returns the number newly added."""
    batch = list(chunks)
    if not batch:
        return 0
    vectors = embedder.embed_documents([chunk.text for chunk in batch])
    return store.add(batch, vectors)
