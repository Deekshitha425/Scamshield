"""FastAPI backend — exposes the agent pipeline over HTTP for the Streamlit frontend."""
from __future__ import annotations
from fastapi import FastAPI
from pydantic import BaseModel
from src.graph import analyze

app = FastAPI(title="ScamShield API", version="0.1.0")


class AnalyzeRequest(BaseModel):
    content: str


class AnalyzeResponse(BaseModel):
    verdict: str
    confidence: float
    explanation: str
    retrieval_rounds_used: int
    evidence_count: int


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_content(request: AnalyzeRequest) -> AnalyzeResponse:
    result = analyze(request.content)
    return AnalyzeResponse(
        verdict=result.verdict.value,
        confidence=round(result.confidence_score, 3),
        explanation=result.explanation,
        retrieval_rounds_used=result.retrieval_rounds_used,
        evidence_count=len(result.evidence),
    )
