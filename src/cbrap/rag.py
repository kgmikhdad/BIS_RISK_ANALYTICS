from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .scenarios import classify_scenario_query


@dataclass
class RetrievedChunk:
    source: str
    chunk_id: int
    score: float
    text: str


def load_markdown_documents(docs_dir: str | Path) -> dict[str, str]:
    docs = {}
    for path in sorted(Path(docs_dir).glob("*.md")):
        docs[path.name] = path.read_text(encoding="utf-8")
    if not docs:
        raise FileNotFoundError(f"No markdown documents found in {docs_dir}")
    return docs


def chunk_text(text: str, max_words: int = 120, overlap: int = 25) -> list[str]:
    words = re.findall(r"\S+", text)
    if not words:
        return []
    chunks = []
    step = max(1, max_words - overlap)
    for start in range(0, len(words), step):
        chunk = " ".join(words[start : start + max_words])
        if chunk:
            chunks.append(chunk)
    return chunks


def build_corpus(docs: dict[str, str]) -> pd.DataFrame:
    rows = []
    for source, text in docs.items():
        for i, chunk in enumerate(chunk_text(text)):
            rows.append({"source": source, "chunk_id": i, "text": chunk})
    return pd.DataFrame(rows)


def retrieve(query: str, docs_dir: str | Path, top_k: int = 4) -> list[RetrievedChunk]:
    docs = load_markdown_documents(docs_dir)
    corpus = build_corpus(docs)
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    matrix = vectorizer.fit_transform(corpus["text"])
    q_vec = vectorizer.transform([query])
    scores = cosine_similarity(q_vec, matrix).ravel()
    order = scores.argsort()[::-1][:top_k]
    return [
        RetrievedChunk(
            source=str(corpus.iloc[i]["source"]),
            chunk_id=int(corpus.iloc[i]["chunk_id"]),
            score=float(scores[i]),
            text=str(corpus.iloc[i]["text"]),
        )
        for i in order
    ]


def generate_scenario_card(query: str, retrieved: list[RetrievedChunk]) -> dict[str, str]:
    base = classify_scenario_query(query)
    evidence_sources = ", ".join(sorted({r.source for r in retrieved}))
    validation = (
        "Compare exact repricing with approximation, run sensitivity checks, document assumptions, "
        "and require human review before using outputs for decisions."
    )
    return {
        **base,
        "evidence_sources": evidence_sources,
        "suggested_controls": validation,
        "prototype_note": "This is a retrieval-augmented scenario-design aid using local documents, not a trained model and not production risk advice.",
    }
