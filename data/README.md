# Data

Only small **sample** files are committed here (`sample_*`) so the pipeline runs
end-to-end without any external downloads. They are illustrative, not a real
evaluation set.

## Full datasets (not committed — download separately)

| File to populate | Source | Used for |
|---|---|---|
| `eval_sets/phiusiil.csv` | [PhiUSIIL Phishing URL Dataset](https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+dataset) — UCI ML Repository | Held-out URL detection evaluation |
| `eval_sets/smishing.csv` | SMS Phishing Dataset (Ham/Spam/Smishing) — search Kaggle/Mendeley for the current mirror | Held-out SMS/content detection evaluation |
| `rag_corpus/apwg/` | [APWG](https://apwg.org/) advisory reports | RAG corpus |
| `rag_corpus/cert_in/` | [CERT-In](https://www.cert-in.org.in/) advisories | RAG corpus |
| `rag_corpus/indian_upi_corpus.jsonl` | Self-curated — see `docs/evaluation_plan.md` for methodology and the real-vs-synthetic disclosure | RAG corpus only, **not used for headline accuracy** |

## Critical rule — do not violate

**Never let the same example exist in both `rag_corpus/` and `eval_sets/`.**
If a test example is also retrievable by the RAG agents, the system can "cheat"
by recognizing something it's already seen, which invalidates any accuracy
number reported from that test set. Keep the split enforced at data-curation
time, not just at training time.

## Building the vector store from the sample corpus

```bash
python -m src.rag.build_index --input data/rag_corpus/sample_scam_examples.jsonl
```

(See `src/rag/build_index.py` for the indexing script.)
