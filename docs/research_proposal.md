# Research Proposal
## An Adaptive Multi-Agent RAG Framework for Explainable Phishing/Scam Defense Targeting Non-Technical Users

---

## 1. Title (working)
"Beyond Accuracy: An Adaptive, Evidence-Verified, RAG-Grounded Multi-Agent Framework for Explainable Phishing Defense in Non-Technical User Populations"

*(Refine after literature confirmation of the ontology-based paper's exact title/venue — avoid overlapping phrasing.)*

---

## 2. Problem Statement

Phishing and digital-fraud attacks (email, SMS, UPI/OTP scams, malicious URLs, QR codes) remain one of the most persistent cybersecurity threats because they exploit human trust rather than technical vulnerabilities. Existing automated defenses fall into two categories:

1. **Classifier-centric systems** (classical ML, deep learning, and recent LLM-agent systems such as PhishDebate and MultiPhishGuard) that optimize purely for detection accuracy, evaluated against technical benchmarks and assumed to be consumed by security-literate users or analysts.
2. **Enterprise-oriented agentic frameworks** (e.g., ontology/RL-based Agent-AI phishing defense systems) designed for SOC integration, with no quantitative evaluation and no consideration of non-technical end users.

**Neither category addresses the population most harmed by phishing/scam attacks in practice**: elderly users, first-time smartphone/internet users, and non-technical individuals who cannot interpret technical verdicts ("homoglyph domain detected," "SPF failure") even when detection is accurate. This is a significant, underserved gap — particularly relevant in the Indian context, where UPI/OTP fraud disproportionately affects exactly this demographic.

---

## 3. Research Gap (grounded in literature review)

| Gap | Evidence from prior work |
|---|---|
| No dynamic, input-adaptive agent routing | PhishDebate, MultiPhishGuard, MemoPhishAgent all use a fixed agent set regardless of input type |
| No explicit cross-source evidence verification/conflict resolution | Prior agent systems aggregate or vote on evidence; none explicitly reconcile disagreement between sources (WHOIS, blacklist, similarity score) before deciding |
| No sufficiency-gated iterative retrieval in phishing-specific agent systems | Retrieval (where present) is single-pass; Self-RAG/CRAG-style iterative sufficiency checking is established in general RAG literature but not applied here |
| No evaluation of explanation comprehension by non-technical users | All reviewed systems evaluate only detection accuracy; none measure whether an end user understands or correctly acts on the output |
| No quantitative evaluation in the closest architecturally-similar prior system (ontology-based Agent-AI phishing paper) | That paper proposes a comparable multi-agent structure but reports zero accuracy/precision/recall figures — architecture-only, not empirically validated |

---

## 4. Research Objectives

**RO1.** Design and implement a multi-agent phishing/scam investigation framework with dynamic, input-type-based agent routing.

**RO2.** Design and implement an Evidence Verification mechanism that explicitly reconciles agreement/conflict across heterogeneous threat-intelligence sources (WHOIS, URL-safety APIs, RAG-retrieved similar scams, content-pattern analysis) before a verdict is issued.

**RO3.** Design and implement a sufficiency-gated iterative retrieval loop (grounded in Self-RAG/CRAG), bounded by an explicit stopping condition, that defers to human review rather than forcing a low-confidence verdict.

**RO4.** Evaluate the system's detection performance (precision/recall/F1) against a zero-shot LLM baseline and contextualize against MultiPhishGuard's reported benchmark.

**RO5.** Evaluate the system's explanations for comprehension and actionability among non-technical users via a structured human-rated rubric — the axis absent from all reviewed prior work.

---

## 5. Proposed Methodology (summary — full detail in SRS)

- **Architecture**: Input Understanding Agent → Dynamic Router → specialized evidence agents (Email/URL/QR/Content) → Judge/Meta-Reasoning Agent (owns Evidence Verification + sufficiency-gated retrieval) → Confidence Calibration → Explainer Agent → user-facing report.
- **Datasets**: PhishTank/OpenPhish (dated snapshots), APWG/CERT-In/CISA/NIST as RAG corpus sources, curated Indian SMS/UPI scam corpus (methodology to be documented transparently, including real-vs-synthetic composition).
- **Models**: Llama 3 via Groq (free-tier API) for agent reasoning; sentence-transformers for embeddings; optional fine-tuned DistilBERT/RoBERTa content classifier as an ablation comparison; logistic regression/gradient boosting for confidence calibration.
- **Toggleable components**: routing, evidence verification, and iterative retrieval must each be independently disable-able in code to support ablation studies (RO4 requirement).

---

## 6. Expected Contributions

1. An adaptive agent-routing mechanism reducing unnecessary agent invocations without accuracy loss.
2. An evidence-verification framework that measurably improves accuracy specifically on source-disagreement cases.
3. A sufficiency-gated iterative retrieval loop grounded in and extending Self-RAG/CRAG to the phishing-defense domain.
4. The first (per current literature review) quantitative evaluation of phishing-defense explanation quality from a non-technical end-user comprehension standpoint.

---

## 7. Scope Boundaries (stated upfront, not discovered late)

- Live self-updating knowledge base from user feedback: **out of scope** for implementation; feedback is logged for offline evaluation only. Stated as future work due to reproducibility and memory-poisoning attack-surface concerns (per Agent Security Bench).
- Real-time OS-level SMS/call interception: **out of scope**; system operates on user-submitted/forwarded messages. Native mobile integration stated as future work.
- Full adversarial robustness testing against prompt-injection attacks on the RAG/agent pipeline: **acknowledged as a limitation**, not solved within this project's scope.

---

## 8. Timeline (fill in with your actual academic calendar)

| Phase | Deliverable |
|---|---|
| Phase 1 | SRS finalized, datasets collected/snapshotted |
| Phase 2 | Evidence agents + routing implemented |
| Phase 3 | Judge, verification, iterative retrieval implemented |
| Phase 4 | Calibration + Explainer agent implemented |
| Phase 5 | Evaluation: baseline comparison, three ablations, human comprehension study |
| Phase 6 | Paper writing, submission |

---

## 9. Base References (to expand into full IEEE-format bibliography)

1. PhishDebate — https://arxiv.org/abs/2506.15656
2. MultiPhishGuard — https://arxiv.org/abs/2505.23803
3. MemoPhishAgent — https://arxiv.org/pdf/2602.21394
4. User-Centric Phishing Detection: RAG + LLM (confirm exact citation)
5. Ontology-based Agent AI Phishing Defense paper (confirm exact citation — venue/year/DOI)
6. Self-RAG, Asai et al., arXiv:2310.11511
7. Corrective RAG (CRAG), Yan et al., arXiv:2401.15884
8. Agent Security Bench (ASB) (confirm exact citation)
