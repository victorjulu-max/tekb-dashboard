"""
TEKB Core v1.4 - Phase 3 Research Engine
Anti-Circularity + FDR/BH + Permutation + Falsification
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
import random
from datetime import datetime
from .constants import RESEARCH_WARMUP_BARS, MIN_RESEARCH_BARS

@dataclass
class ResearchHypothesis:
    hypothesis_id: str
    description: str
    batch_id: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    p_value: Optional[float] = None
    is_tested: bool = False

@dataclass
class ResearchBatch:
    batch_id: str
    hypothesis_ids: List[str] = field(default_factory=list)
    cutoff_date: Optional[datetime] = None
    is_frozen: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    def freeze(self, cutoff_date: datetime):
        self.cutoff_date = cutoff_date
        self.is_frozen = True

class ResearchLedger:
    def __init__(self):
        self.hypotheses: Dict[str, ResearchHypothesis] = {}
        self.batches: Dict[str, ResearchBatch] = {}
    def register_batch(self, batch_id: str):
        if batch_id in self.batches:
            return self.batches[batch_id]
        b = ResearchBatch(batch_id=batch_id)
        self.batches[batch_id] = b
        return b
    def register_hypothesis(self, hypothesis_id: str, description: str, batch_id: str):
        if batch_id not in self.batches:
            self.register_batch(batch_id)
        batch = self.batches[batch_id]
        if batch.is_frozen:
            raise ValueError(f"Batch {batch_id} already frozen - no new hypothesis allowed (anti-circularity)")
        h = ResearchHypothesis(hypothesis_id=hypothesis_id, description=description, batch_id=batch_id)
        self.hypotheses[hypothesis_id] = h
        batch.hypothesis_ids.append(hypothesis_id)
        return h
    def freeze_batch(self, batch_id: str, cutoff_date: datetime):
        if batch_id not in self.batches:
            raise KeyError(f"Batch {batch_id} not found")
        self.batches[batch_id].freeze(cutoff_date)
    def validate_no_future_leak(self, hypothesis_id: str, data_date: datetime) -> bool:
        h = self.hypotheses.get(hypothesis_id)
        if not h:
            raise KeyError(f"Hypothesis {hypothesis_id} not found")
        batch = self.batches.get(h.batch_id)
        if not batch or not batch.is_frozen or not batch.cutoff_date:
            raise ValueError(f"Batch {h.batch_id} not frozen yet")
        return data_date <= batch.cutoff_date

def benjamini_hochberg(p_values: List[float], alpha: float = 0.05):
    if not p_values:
        return [], []
    n = len(p_values)
    sorted_pairs = sorted(enumerate(p_values), key=lambda x: x[1])
    sorted_indices = [i for i, _ in sorted_pairs]
    sorted_p = [p for _, p in sorted_pairs]
    rejected_sorted = [False]*n
    max_k = -1
    for k, p in enumerate(sorted_p, start=1):
        if p <= (k / n) * alpha:
            max_k = k-1
    if max_k >= 0:
        for i in range(max_k+1):
            rejected_sorted[i] = True
    q_sorted = [0.0]*n
    min_q = 1.0
    for i in range(n-1, -1, -1):
        q = sorted_p[i] * n / (i+1)
        if q < min_q:
            min_q = q
        q_sorted[i] = min(min_q, 1.0)
    rejected = [False]*n
    q_values = [0.0]*n
    for sorted_pos, orig_idx in enumerate(sorted_indices):
        rejected[orig_idx] = rejected_sorted[sorted_pos]
        q_values[orig_idx] = q_sorted[sorted_pos]
    return rejected, q_values

def fdr_control_summary(p_values: List[float], alpha: float = 0.05):
    rejected, q_values = benjamini_hochberg(p_values, alpha)
    return {"alpha": alpha, "n_tests": len(p_values), "n_rejected": sum(rejected), "rejected": rejected, "q_values": q_values, "fdr_controlled": True}

def permutation_test(observed_stat: float, null_distribution: List[float], alternative: str = "two-sided") -> float:
    if not null_distribution:
        raise ValueError("null_distribution empty")
    if alternative == "greater":
        count = sum(1 for x in null_distribution if x >= observed_stat)
    elif alternative == "less":
        count = sum(1 for x in null_distribution if x <= observed_stat)
    else:
        abs_obs = abs(observed_stat)
        count = sum(1 for x in null_distribution if abs(x) >= abs_obs)
    p_value = (count + 1) / (len(null_distribution) + 1)
    return min(max(p_value, 0.0), 1.0)

def generate_null_distribution(data: List[float], n_permutations: int = 1000, seed: int = 42):
    rng = random.Random(seed)
    if not data:
        return []
    mean = sum(data) / len(data)
    centered = [x - mean for x in data]
    nulls = []
    for _ in range(n_permutations):
        sample = [rng.choice(centered) for _ in centered]
        stat = sum(sample) / len(sample) if sample else 0.0
        nulls.append(stat)
    return nulls

def falsification_test(p_values_real: List[float], p_values_fake: List[float], alpha: float = 0.05):
    real_res, _ = benjamini_hochberg(p_values_real, alpha)
    fake_res, _ = benjamini_hochberg(p_values_fake, alpha)
    return {"real_rejected": sum(real_res), "fake_rejected": sum(fake_res), "real_rate": sum(real_res)/len(real_res) if real_res else 0, "fake_rate": sum(fake_res)/len(fake_res) if fake_res else 0, "passes_falsification": sum(real_res) > sum(fake_res) or (sum(real_res)==0 and sum(fake_res)==0), "alpha": alpha}

def check_research_eligibility(n_bars: int) -> bool:
    return n_bars >= (RESEARCH_WARMUP_BARS + MIN_RESEARCH_BARS)