# Abstract

**Title:** An Adaptive Multi-Agent RAG Framework for Explainable Phishing and Scam
Defense in Non-Technical User Populations

Phishing and scam attacks—spanning email, URL, SMS, and UPI/QR-based fraud—remain
a persistent cybersecurity threat, exploiting human trust rather than technical
vulnerability. Recent multi-agent, LLM-based systems (e.g., Hmimou et al., IEEE
Access 2025) achieve strong detection accuracy using RAG-grounded reasoning, but
are built and evaluated for security analysts, with none measuring whether outputs
are actually understood or acted upon by non-technical, fraud-vulnerable users.
This project proposes an adaptive multi-agent framework combining dynamic
input-based agent routing, explicit cross-source evidence verification, and
sufficiency-gated iterative retrieval—grounded in Self-RAG and Corrective
RAG—across email, URL, SMS, and QR-code modalities, including UPI-based fraud. A
Judge agent governs verification and a bounded retrieval loop, deferring to human
review when evidence is insufficient rather than forcing a low-confidence verdict.
Effectiveness will be evaluated using standard detection metrics against
established benchmarks, alongside a preliminary human evaluation of explanation
comprehension—a dimension absent from prior work—contributing both an
architectural extension and a new evaluation axis for an underserved population.

**Keywords:** Phishing Detection, Scam Defense, Retrieval-Augmented Generation,
Multi-Agent Systems, Large Language Models, Explainable AI, Human-Centered
Security, Evidence Verification, UPI/QR Fraud, Non-Technical User Evaluation.

See `related_work.md` for the full base-paper comparison and `research_proposal.md`
for the complete research framing.
