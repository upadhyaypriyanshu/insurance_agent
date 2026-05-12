from typing import List


def find_missing_fields(fields: dict) -> List[str]:
    # Mandatory fields for FNOL processing
    required_fields = [
        "policyNumber",
        "policyholderName",
        "incidentDate",
        "incidentLocation",
        "incidentDescription",
    ]
    return [field for field in required_fields if not fields.get(field) or fields.get(field).lower() in ["", "unknown"]]
