# Related Work & Base Paper Comparison

## Primary base paper

> Y. Hmimou, M. Tabaa, A. Khiat, Z. Hidila, "A Multi-Agent System for
> Cybersecurity Threat Detection and Correlation Using Large Language Models,"
> *IEEE Access*, vol. 13, pp. 150199–150201+, 2025.
> DOI: 10.1109/ACCESS.2025.3602681.

The only paper found across this project's literature review that is
simultaneously: a confirmed IEEE journal, genuinely multi-agent, uses
RAG/FAISS as a real component, reports real quantitative results (93.6%
detection accuracy, 87% multi-agent correlation accuracy, 41.3% false-positive
reduction), and has a cross-agent correlation/verification mechanism.

## Comparison table

| Dimension | Hmimou et al. (2025) | PhishDebate / User-Centric RAG (conf.) | This project |
|---|---|---|---|
| Core method | Multi-agent + RAG/FAISS | Multi-agent debate / RAG+LLM | Multi-agent + RAG |
| Cross-source verification | Contextual recommendation system correlates agents | Not handled explicitly | Dedicated Judge verification step |
| Scope | Email, logs, IP scanning (general threats) | URL-only / Email-only | URL, SMS, UPI, QR |
| Retrieval behavior | RAG-grounded, single-pass | None / single-pass | Sufficiency-gated, iterative |
| Target audience | SOC analysts | Security researchers | Non-technical, vulnerable users |
| Evaluation | 93.6% accuracy, 87% correlation, 41.3% FP reduction | Accuracy only | Accuracy + human comprehension |

## Other papers referenced

- W. Li et al., "PhishDebate: An LLM-Based Multi-Agent Framework for Phishing
  Website Detection," IEEE BigData 2025.
- A. H. Al Barwani et al., "User-Centric Phishing Detection: A RAG and
  LLM-Based Approach," IEEE ICCE 2026.
- Y. Xue et al., "MultiPhishGuard: An Explainable and Adaptive Multi-Agent
  LLM System for Phishing Email Detection," arXiv:2505.23803, 2025 (ACM CCS
  submission — not IEEE, cited for its 97.8% accuracy benchmark and its
  explanation-simplifier agent, which targets non-experts but never
  evaluates comprehension on them).
- J. Zhang et al., "Benchmarking and Evaluating Large Language Models in
  Phishing Detection for Small and Midsize Enterprises," IEEE Access, 2025 —
  justifies the choice of Llama-3-8b as a cost-controlled model option.
- T. Koide et al., "ChatPhishDetector: Detecting Phishing Sites Using Large
  Language Models," IEEE Access, 2024.
- A. Asai et al., "Self-RAG: Learning to Retrieve, Generate, and Critique
  through Self-Reflection," arXiv:2310.11511, 2023 — grounds the iterative
  retrieval design.
- S.-Q. Yan et al., "Corrective Retrieval Augmented Generation,"
  arXiv:2401.15884, 2024 — grounds the iterative retrieval design.
- Agent Security Bench (ASB) — cited for the memory-poisoning risk that
  motivates keeping the RAG corpus static during evaluation.

## The precise, defensible novelty claim

No individual technique here is unprecedented — multi-agent coordination,
RAG grounding, and LLM-based explanation generation all have direct prior
art (see above). What is not done by any paper found in this review is the
**combination**: dynamic routing + explicit evidence verification +
sufficiency-gated iterative retrieval in one architecture, **and** evaluating
the result on whether it changes what a non-technical, fraud-vulnerable user
understands and does — rather than only whether the classifier was accurate.

MultiPhishGuard's explanation-simplifier agent is the closest prior work on
the explainability side — it is *built for* non-experts but never *tested
on* non-experts. That distinction (built-for vs. evaluated-on) is this
project's precise, checkable contribution.
