# ScamShield

**An Adaptive Multi-Agent RAG Framework for Explainable Phishing & Scam Defense**

PID: 13 · Dhriti Raj & Deekshitha · CBIT Hyderabad · Guide: Ms. Falak Naaz, Assistant Professor, CSE & AIML Department

---

## What this is

Most phishing-detection AI is built and evaluated for security experts — a correct
verdict like *"SPF authentication failure"* means nothing to a non-technical or
first-time internet user. ScamShield is a multi-agent, RAG-grounded system that
detects phishing and scam content across **email, URL, SMS, and QR-code**
modalities (including UPI-based fraud), and — distinct from prior work — explains
*why* in plain language, evaluated specifically for comprehension by non-technical
users.

This repository is a **working scaffold**: the architecture, agent interfaces, RAG
pipeline, and evaluation harness are implemented and runnable end-to-end on sample
data. Swapping in the full datasets and API keys turns it into the complete system
described in `docs/`.

## Architecture

```
User Input (email / URL / SMS / QR)
        │
Dynamic Agent Router
        │
Evidence Agents (Email / URL / QR / Content)
        │
Evidence Collection Layer
        │
Judge / Meta-Reasoning Agent
   ├── Evidence Verification (cross-source agreement)
   ├── Sufficiency Check → Active RAG retrieval (max 2 rounds)
   └── else → flag for human review (never a forced guess)
        │
Confidence Calibration
        │
Explainer Agent
        │
User-facing Report (Streamlit)
```

Full diagram: `docs/architecture.png`. Full writeup: `docs/architecture.md`.

## Repository layout

```
scamshield/
├── src/
│   ├── agents/        # router, evidence agents, judge, calibration, explainer
│   ├── rag/           # vector store + retriever (ChromaDB/FAISS)
│   ├── tools/         # WHOIS, Safe Browsing, VirusTotal wrappers
│   └── api/           # FastAPI backend
├── frontend/          # Streamlit UI
├── data/
│   ├── rag_corpus/    # threat-intel + regional scam examples (RAG only)
│   └── eval_sets/     # held-out test data (never in the RAG corpus)
├── docs/              # abstract, research proposal, architecture, eval plan
├── notebooks/         # optional Colab notebook for the DistilBERT ablation
└── tests/             # unit tests for agent logic
```

## Quickstart

```bash
git clone <this-repo>
cd scamshield
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your API keys
uvicorn src.api.main:app --reload      # backend
streamlit run frontend/streamlit_app.py  # frontend, separate terminal
```

## What's implemented vs. what's a stub

| Component | Status |
|---|---|
| Dynamic routing | Implemented (rule-based input-type detection) |
| Evidence agents (Email/URL/QR/Content) | Implemented, LLM calls via a swappable client |
| Judge — verification + sufficiency loop | Implemented, capped at 2 retrieval rounds |
| RAG corpus + retriever | Implemented (ChromaDB, sentence-transformers) |
| Confidence calibration | Implemented (logistic regression over evidence features) |
| Explainer agent | Implemented |
| DistilBERT classifier ablation | Stub notebook — requires GPU + labeled data |
| Human comprehension evaluation | Rubric + scoring script provided, not automatable |
| Live self-updating knowledge base | **Not implemented — explicit future work** (see `docs/architecture.md`) |

## Datasets

See `docs/evaluation_plan.md` for the full protocol. In short:
- **PhiUSIIL Phishing URL Dataset** and a **Ham/Spam/Smishing SMS dataset** — held-out evaluation sets, not part of the RAG corpus.
- **Curated Indian SMS/UPI scam corpus** — RAG knowledge base only.
- Public threat-intel sources (APWG, CERT-In, CISA, NIST) — RAG corpus.

Raw datasets are not committed to this repo (see `data/README.md` for sources and
licensing notes) — only small illustrative samples are included so the pipeline
runs out of the box.

## Base papers & related work

Full literature comparison in `docs/related_work.md`. Primary base paper:

> Y. Hmimou, M. Tabaa, A. Khiat, Z. Hidila, "A Multi-Agent System for Cybersecurity
> Threat Detection and Correlation Using Large Language Models," *IEEE Access*,
> vol. 13, pp. 150199–150201+, 2025. DOI: 10.1109/ACCESS.2025.3602681.

## License

MIT — see `LICENSE`.
