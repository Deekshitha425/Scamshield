# Evaluation Plan

## Two evaluation axes

This project is evaluated on two distinct axes, and the second is the actual
research contribution — no reviewed prior work evaluates it.

### 1. Detection performance

| Metric | Compared against |
|---|---|
| Precision / Recall / F1 | Zero-shot LLM baseline (no RAG, no agents) |
| Precision / Recall / F1 | MultiPhishGuard's reported 97.8% (contextualize, don't chase) |
| Precision / Recall / F1 | Hmimou et al. (2025) — 93.6% detection accuracy, 87% correlation accuracy |

### 2. Component ablations

Each of the three architectural mechanisms must be **independently toggleable**
in code (this is enforced by the graph structure in `src/graph.py` — each
node can be bypassed) so these ablations are actually runnable:

| Ablation | Compares against | What it proves |
|---|---|---|
| Dynamic routing | "invoke every agent on every input" | Latency/cost reduction with no accuracy drop |
| Evidence verification | "trust the first/highest-confidence source" | Accuracy specifically on source-disagreement cases |
| Iterative retrieval | Single-pass RAG (no sufficiency loop) | Accuracy/calibration improvement on ambiguous cases |

### 3. Explainability evaluation (the novel contribution)

A **preliminary, honestly-scoped** human evaluation, not a full-scale study:

- **Sample size:** 8–15 participants, explicitly reported as a small/exploratory
  study — do not overstate statistical power.
- **Recruitment:** deliberately non-technical — family members, non-CS
  classmates, neighbors. Recruiting only AI/ML students defeats the purpose.
- **Materials:** 5–10 sample messages from the held-out test set, each with
  the system's generated explanation.
- **Rubric per message** (keep to 3–4 questions):
  1. Comprehension (1–5): "How clearly did you understand why this is flagged?"
  2. Actionability (Yes/No/Unsure): "Would you know what to do next?"
  3. Trust (1–5): "How much do you trust this explanation?"
  4. Optional open-ended: "What, if anything, was confusing?"
- **Session format:** one-on-one, 10–15 minutes per participant.
- **Analysis:** average scores, % "Yes" on actionability, compare against a
  raw-technical-explanation baseline if prepared, report informal
  inter-rater consistency.
- **Ethics note:** check with your institution whether a simple informed-consent
  statement is required, even for a small-scale exploratory study.

## Dataset split — critical rule

```
Full corpus
    │
    ├── RAG corpus (~60%)      → embedded, retrievable by agents
    ├── Test set (~30%)         → held out, NEVER embedded, used for accuracy numbers
    └── Dev/validation (~10%)   → used to tune the confidence calibrator only
```

Split **before** any embedding happens, and stratify by scam category so the
RAG corpus and test set have proportional representation of each type
(UPI fraud, fake-delivery, lottery scam, etc.) rather than an arbitrary
random cut.

**Headline accuracy numbers should come from established public benchmarks**
(PhiUSIIL, the Ham/Spam/Smishing dataset), not the self-curated Indian
corpus — the Indian corpus's role is RAG grounding and regional-relevance
storytelling, not the primary accuracy claim. See `data/README.md`.

## Readability as a lightweight complement (optional, no human study needed)

If a full human study isn't feasible on your timeline, automated readability
metrics (Flesch-Kincaid Grade Level, Flesch Reading Ease, SMOG Index — the
`textstat` package) can quantify whether the Explainer Agent's output is
simpler than a raw technical verdict. This is a legitimate proxy used in
accessibility/health-literacy research, but it measures readability, not
comprehension — state this limitation explicitly rather than conflating the two.
