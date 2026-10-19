"""Automated benchmark test runner evaluating test cases against deterministic guardrails and models."""
import time
from typing import Dict, Any, List
from pydantic import ValidationError
from solo_travel.models.state import UserTravelRequest, TravelStyle
from solo_travel.guardrails.safety import evaluate_travel_request_guardrails
from solo_travel.evaluation.dataset import EVALUATION_DATASET


def run_evaluation_suite() -> Dict[str, Any]:
    """
    Executes the benchmark dataset and collects metrics:
    - Pass/Fail accuracy against expected outcomes
    - Interception latency in milliseconds
    - Guardrail precision
    """
    total = len(EVALUATION_DATASET)
    passed = 0
    results: List[Dict[str, Any]] = []

    start_time = time.perf_counter()

    for tc in EVALUATION_DATASET:
        case_id = tc["case_id"]
        expected = tc["expected_outcome"]
        actual = "UNKNOWN"

        t0 = time.perf_counter()
        try:
            req = UserTravelRequest(
                origin=tc["origin"],
                destination=tc["destination"],
                duration_days=tc["duration_days"],
                total_budget_inr=tc["budget_inr"],
                travel_style=TravelStyle(tc["travel_style"]),
                interests=tc["interests"]
            )
            # Evaluate guardrails
            guard_res = evaluate_travel_request_guardrails(req)
            if not guard_res.is_safe:
                actual = "BLOCK_GUARDRAILS"
            else:
                actual = "PASS_VALIDATION"

        except ValidationError:
            actual = "BLOCK_BUDGET"

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        is_success = actual == expected
        if is_success:
            passed += 1

        results.append({
            "case_id": case_id,
            "description": tc["description"],
            "expected": expected,
            "actual": actual,
            "passed": is_success,
            "latency_ms": round(elapsed_ms, 2)
        })

    total_time_ms = (time.perf_counter() - start_time) * 1000.0

    return {
        "total_cases": total,
        "passed_cases": passed,
        "accuracy_percent": round((passed / total) * 100.0, 1),
        "total_time_ms": round(total_time_ms, 2),
        "case_results": results
    }
