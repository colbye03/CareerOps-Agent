"""Deterministic retrieval baseline; replaceable by an embedding retriever."""
import re
from typing import Protocol


def contains(text, term):
    return bool(re.search(r"(?<!\w)" + re.escape(term.casefold()) + r"(?!\w)", text.casefold()))


class Retriever(Protocol):
    def retrieve(self, terms: list[str], evidence: list[dict]) -> list[dict]: ...


class LexicalRetriever:
    def retrieve(self, terms, evidence):
        hits = []
        for item in evidence:
            if not item["verified"]:
                continue
            text = " ".join([item["summary"], *item["skills"], *item["capabilities"]])
            matched = [t for t in terms if contains(text, t)]
            if matched:
                hits.append({"evidence_id": item["id"], "matched_terms": matched,
                             "level": item["level"], "source": item["source"],
                             "summary": item["summary"], "metrics": item["metrics"]})
        return sorted(hits, key=lambda h: (-len(h["matched_terms"]), -h["level"], h["evidence_id"]))
