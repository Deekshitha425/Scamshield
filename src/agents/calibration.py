"""
Confidence Calibration — turns raw evidence features into a trustworthy
confidence percentage. This is the one component in the whole architecture
that trains a real model (logistic regression), separate from the LLM
agents, which only prompt and retrieve.
"""
from __future__ import annotations
import numpy as np
from sklearn.linear_model import LogisticRegression
from src.agents.schemas import CaseState

FEATURE_NAMES = [
    "domain_age_days_lt_30",
    "safe_browsing_flagged",
    "virustotal_ratio_gt_0_1",
    "content_supports_scam",
    "display_name_mismatch",
]


def extract_features(state: CaseState) -> np.ndarray:
    """Turn a CaseState's evidence list into a fixed-length feature vector."""
    feature_map = {name: 0 for name in FEATURE_NAMES}

    for e in state.evidence:
        if e.signal == "domain_age_days" and e.supports_scam:
            feature_map["domain_age_days_lt_30"] = 1
        elif e.signal == "safe_browsing_flagged" and e.supports_scam:
            feature_map["safe_browsing_flagged"] = 1
        elif e.signal == "virustotal_malicious_ratio" and e.supports_scam:
            feature_map["virustotal_ratio_gt_0_1"] = 1
        elif e.source == "content_agent" and e.supports_scam:
            feature_map["content_supports_scam"] = 1
        elif e.signal == "display_name_address_mismatch" and e.supports_scam:
            feature_map["display_name_mismatch"] = 1

    return np.array([feature_map[name] for name in FEATURE_NAMES]).reshape(1, -1)


class ConfidenceCalibrator:
    """
    Wraps a scikit-learn LogisticRegression. Call `fit()` once during
    training on your labeled evaluation set, then `predict_confidence()`
    at inference time. A freshly-constructed, unfit instance falls back to
    a simple weighted-average heuristic so the pipeline still runs before
    you've trained on real data.
    """

    def __init__(self):
        self._model = LogisticRegression()
        self._is_fit = False

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self._model.fit(X, y)
        self._is_fit = True

    def predict_confidence(self, state: CaseState) -> float:
        features = extract_features(state)
        if self._is_fit:
            return float(self._model.predict_proba(features)[0][1])
        # Fallback heuristic before the model has been trained on real data.
        return float(features.sum() / len(FEATURE_NAMES))


def calibrate(state: CaseState, calibrator: ConfidenceCalibrator) -> CaseState:
    state.confidence_score = calibrator.predict_confidence(state)
    return state
