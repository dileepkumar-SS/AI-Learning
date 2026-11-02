from __future__ import annotations

import math
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    sdk_version: str
    symbol: str
    section: str
    text: str
    code: str
    url: str


def tokenize(value: str) -> set[str]:
    return set(re.findall(r"[a-z0-9_.]+", value.lower()))


def build_index(docs: dict) -> list[Chunk]:
    """Week 4-style structure-aware chunks with version metadata retained."""
    chunks = []
    for version, symbols in docs.items():
        for symbol, record in symbols.items():
            if not record.get("exists"):
                continue
            chunks.append(
                Chunk(
                    chunk_id=f"{version}:{symbol}:reference",
                    sdk_version=version,
                    symbol=symbol,
                    section="reference",
                    text=record["summary"],
                    code=record["code"],
                    url=record["url"],
                )
            )
    return chunks


def score(query: str, chunk: Chunk) -> float:
    query_terms = tokenize(query) | tokenize(chunk.symbol)
    chunk_terms = tokenize(f"{chunk.symbol} {chunk.section} {chunk.text} {chunk.code}")
    return len(query_terms & chunk_terms) / math.sqrt(len(chunk_terms) or 1)


def version_scoped_search(docs: dict, query: str, symbol: str, api_version: str) -> Chunk | None:
    """Hard metadata filtering occurs before scoring; other live versions cannot rank."""
    eligible = [
        chunk
        for chunk in build_index(docs)
        if chunk.sdk_version == api_version and chunk.symbol == symbol
    ]
    if not eligible:
        return None
    return max(eligible, key=lambda chunk: score(query, chunk))
