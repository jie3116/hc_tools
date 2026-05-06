from __future__ import annotations

import math
import re
from collections import Counter


TOKEN_RE = re.compile(r"[a-zA-Z0-9]+")


def normalize_text(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def split_into_chunks(text: str, chunk_size: int = 500) -> list[str]:
    words = " ".join(text.split()).split(" ")
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for word in words:
        if not word:
            continue
        next_len = current_len + len(word) + 1
        if current and next_len > chunk_size:
            chunks.append(" ".join(current))
            current = [word]
            current_len = len(word)
            continue
        current.append(word)
        current_len = next_len
    if current:
        chunks.append(" ".join(current))
    return chunks


def cosine_similarity(query_tokens: list[str], chunk_tokens: list[str]) -> float:
    if not query_tokens or not chunk_tokens:
        return 0.0
    query_counter = Counter(query_tokens)
    chunk_counter = Counter(chunk_tokens)
    numerator = sum(query_counter[token] * chunk_counter[token] for token in set(query_counter) & set(chunk_counter))
    query_norm = math.sqrt(sum(value * value for value in query_counter.values()))
    chunk_norm = math.sqrt(sum(value * value for value in chunk_counter.values()))
    if not query_norm or not chunk_norm:
        return 0.0
    return numerator / (query_norm * chunk_norm)
