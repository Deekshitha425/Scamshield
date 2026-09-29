"""
Build the RAG vector index from a JSONL file of {"text": ..., "source": ...}
records. Run this once after adding new corpus data.

Usage:
    python -m src.rag.build_index --input data/rag_corpus/sample_scam_examples.jsonl
"""
from __future__ import annotations
import argparse
import json
from src.rag.vector_store import VectorStore


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to a JSONL corpus file")
    args = parser.parse_args()

    docs, ids, metadatas = [], [], []
    with open(args.input, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            docs.append(record["text"])
            ids.append(f"{args.input}-{i}")
            metadatas.append({
                "source": record.get("source", "unknown"),
                "label": record.get("label", "scam"),  # back-compat: old corpora had no label
            })

    store = VectorStore()
    store.add_documents(docs, ids, metadatas)
    print(f"Indexed {len(docs)} documents from {args.input}")


if __name__ == "__main__":
    main()