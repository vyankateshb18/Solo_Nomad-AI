"""Guardrails and safety checks for Solo Travel Intelligence Platform."""
import re
from typing import List, Tuple
from pydantic import BaseModel, Field
from solo_travel.models.state import UserTravelRequest

# Common prompt injection, system override, and jailbreak patterns
INJECTION_PATTERNS = [
    r"(?i)\bignore\s+(all\s+)?(previous|prior|above)\s+instructions\b",
    r"(?i)\byou\s+are\s+now\s+(in\s+)?developer\s+mode\b",
    r"(?i)\bsystem\s+prompt\b",
    r"(?i)\bjailbreak\b",
    r"(?i)\bdisregard\s+(all\s+)?rules\b",
    r"(?i)\bexecute\s+(system|os|bash|cmd|powershell)\b",
    r"(?i)\bcurl\s+https?://",
    r"(?i)\brm\s+-rf\b",
    r"(?i)\bapi[_-]?key\b",
]

# High-risk / restricted words or script injection attempts
RESTRICTED_CHARS = re.compile(r"[<>{}\\\$;`]")


class GuardrailCheckResult(BaseModel):
    """Structured result of input validation and guardrail checks."""
    is_safe: bool = Field(..., description="Whether the request passed all safety and business guardrails")
    rejection_reasons: List[str] = Field(default_factory=list, description="Specific failure reasons if rejected")
    sanitized_interests: List[str] = Field(default_factory=list, description="Cleaned, sanitized interests list")


def detect_prompt_injection(text: str) -> Tuple[bool, str]:
    """
    Deterministic regex pattern matching for prompt injection and directive override attempts.
    Returns (has_injection, matched_pattern).
    """
    for pattern in INJECTION_PATTERNS:
        match = re.search(pattern, text)
        if match:
            return True, match.group(0)
    return False, ""


def sanitize_text(text: str, max_chars: int = 200) -> str:
    """Strip malicious shell/script characters and bound length."""
    # Remove potentially dangerous shell/code execution characters
    clean = RESTRICTED_CHARS.sub(" ", text)
    # Collapse multiple whitespaces
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean[:max_chars]


def evaluate_travel_request_guardrails(request: UserTravelRequest) -> GuardrailCheckResult:
    """
    Comprehensive pre-execution guardrail evaluation:
    1. Input size boundaries
    2. Prompt injection detection across all text inputs
    3. Realistic solo travel budget limits (INR)
    4. Text sanitization
    """
    rejection_reasons: List[str] = []

    # 1. Check prompt injection in origin & destination
    for field_name, value in [("Origin", request.origin), ("Destination", request.destination)]:
        has_inj, matched = detect_prompt_injection(value)
        if has_inj:
            rejection_reasons.append(
                f"Suspicious directive detected in {field_name}: '{matched}'. Request blocked."
            )

    # 2. Check prompt injection across interests
    clean_interests: List[str] = []
    for idx, interest in enumerate(request.interests):
        has_inj, matched = detect_prompt_injection(interest)
        if has_inj:
            rejection_reasons.append(
                f"Suspicious instruction detected in interest #{idx+1}: '{matched}'. Request blocked."
            )
        else:
            sanitized = sanitize_text(interest, max_chars=100)
            if sanitized:
                clean_interests.append(sanitized)

    # 3. Budget & Duration Guardrails (Solo Travel in INR)
    # Check minimum feasible daily budget
    daily_budget = request.total_budget_inr / request.duration_days
    if daily_budget < 300.0:
        rejection_reasons.append(
            f"Daily budget of ₹{daily_budget:.0f} is below the survival minimum of ₹300/day for solo travel."
        )

    # Check maximum ceiling for a budget platform to prevent absurd/typo entries
    if request.total_budget_inr > 500000.0:
        rejection_reasons.append(
            f"Budget of ₹{request.total_budget_inr:,.0f} exceeds the platform ceiling (₹5,00,000) for budget solo travel."
        )

    # 4. Check origin vs destination identity
    if request.origin.lower() == request.destination.lower():
        rejection_reasons.append(
            "Origin and destination cannot be identical for travel planning."
        )

    is_safe = len(rejection_reasons) == 0
    return GuardrailCheckResult(
        is_safe=is_safe,
        rejection_reasons=rejection_reasons,
        sanitized_interests=clean_interests
    )
