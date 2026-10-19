"""Evaluation package exports."""
from solo_travel.evaluation.dataset import EVALUATION_DATASET
from solo_travel.evaluation.runner import run_evaluation_suite

__all__ = ["EVALUATION_DATASET", "run_evaluation_suite"]
