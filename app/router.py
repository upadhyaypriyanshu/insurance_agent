from typing import Optional, List, Tuple
from .chunking import normalize_text

FRAUD_TERMS = ["fraud", "inconsistent", "staged", "fake", "misrepresentation"]


def parse_amount(value: str) -> Optional[float]:
    if not value:
        return None
    cleaned = value.replace("$", "").replace(",", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return None


def route_claim(fields: dict, missing_fields: List[str]) -> Tuple[str, str]:
    normalized = normalize_text(" ".join(fields.values()))

    if missing_fields:
        return (
            "Manual review",
            f"Mandatory fields are missing: {', '.join(missing_fields)}. Send claim to manual review.",
        )

    if any(term in normalized.lower() for term in FRAUD_TERMS):
        return (
            "Investigation Flag",
            "Claim description contains potentially fraudulent language, so the claim is flagged for investigation.",
        )

    claim_type = fields.get("claimType", "").lower()
    if "injury" in claim_type:
        return (
            "Specialist Queue",
            "Claim type is injury, so route to the specialist queue.",
        )

    estimate = parse_amount(fields.get("initialEstimate", ""))
    if estimate is not None and estimate < 25000:
        return (
            "Fast-track",
            f"Initial estimate is {estimate:.2f}, below 25000, so this claim is eligible for fast-track.",
        )

    return (
        "Standard review",
        "No immediate fast-track or specialist rule applies, so the claim proceeds through standard review.",
    )
