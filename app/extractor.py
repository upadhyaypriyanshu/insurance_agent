import re
from .chunking import normalize_text

FIELD_SEPARATOR = r"(?:(?:[:\-]\s*)|(?:[ \t]{2,}))"

FIELD_PATTERNS = {
    "policyNumber": [rf"policy\s*number{FIELD_SEPARATOR}([A-Z0-9-]+)", rf"policy\s*#{FIELD_SEPARATOR}([A-Z0-9-]+)"],
    "policyholderName": [rf"policyholder\s*name{FIELD_SEPARATOR}([A-Za-z ,.'-]+)", rf"insured\s*name{FIELD_SEPARATOR}([A-Za-z ,.'-]+)"],
    "effectiveDates": [rf"effective\s*date[s]?{FIELD_SEPARATOR}([A-Za-z0-9 /-]+)"],
    "incidentDate": [rf"incident\s*date{FIELD_SEPARATOR}([A-Za-z0-9 /-]+)", rf"date\s*of\s*loss{FIELD_SEPARATOR}([A-Za-z0-9 /-]+)"],
    "incidentTime": [rf"incident\s*time{FIELD_SEPARATOR}([0-9:.apmAPM ]+)", rf"time\s*of\s*loss{FIELD_SEPARATOR}([0-9:.apmAPM ]+)", r"at\s*([0-9:.apmAPM ]+)"],
    "incidentLocation": [rf"location{FIELD_SEPARATOR}([A-Za-z0-9 ,./-]+)", rf"incident\s*location{FIELD_SEPARATOR}([A-Za-z0-9 ,./-]+)"],
    "incidentDescription": [rf"description{FIELD_SEPARATOR}([A-Za-z0-9 ,'\"()\-]+)", rf"loss\s*description{FIELD_SEPARATOR}([A-Za-z0-9 ,'\"()\-]+)", rf"details{FIELD_SEPARATOR}([A-Za-z0-9 ,'\"()\-]+)"],
    "claimant": [rf"claimant{FIELD_SEPARATOR}([A-Za-z ,.'-]+)", rf"reported\s*by{FIELD_SEPARATOR}([A-Za-z ,.'-]+)"],
    "thirdParties": [rf"third\s*party{FIELD_SEPARATOR}([A-Za-z ,.'-]+)", rf"other\s*party{FIELD_SEPARATOR}([A-Za-z ,.'-]+)", rf"third\s*parties{FIELD_SEPARATOR}([A-Za-z ,.'-]+)"],
    "contactDetails": [rf"contact\s*details{FIELD_SEPARATOR}([A-Za-z0-9@+().,\- ]+)", rf"phone{FIELD_SEPARATOR}([0-9\-() ]+)", rf"email{FIELD_SEPARATOR}([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+)"],
    "assetType": [rf"asset\s*type{FIELD_SEPARATOR}([A-Za-z0-9 ]+)", rf"vehicle\s*type{FIELD_SEPARATOR}([A-Za-z0-9 ]+)"],
    "assetID": [rf"asset\s*id{FIELD_SEPARATOR}([A-Z0-9-]+)", rf"vin{FIELD_SEPARATOR}([A-Z0-9-]+)", rf"serial\s*number{FIELD_SEPARATOR}([A-Z0-9-]+)"],
    "estimatedDamage": [rf"estimated\s*damage{FIELD_SEPARATOR}\$?([0-9,.]+)", rf"damage\s*estimate{FIELD_SEPARATOR}\$?([0-9,.]+)", rf"estimate{FIELD_SEPARATOR}\$?([0-9,.]+)"],
    "claimType": [rf"claim\s*type{FIELD_SEPARATOR}([A-Za-z ]+)", rf"type\s*of\s*claim{FIELD_SEPARATOR}([A-Za-z ]+)", r"injury"],
    "attachments": [rf"attachment[s]?{FIELD_SEPARATOR}([A-Za-z0-9 ,._-]+)", r"enclosed\s*documents", r"attachments\s*included"],
    "initialEstimate": [rf"initial\s*estimate{FIELD_SEPARATOR}\$?([0-9,.]+)", rf"initial\s*loss\s*estimate{FIELD_SEPARATOR}\$?([0-9,.]+)", rf"estimate{FIELD_SEPARATOR}\$?([0-9,.]+)"],
}


FORM_STRUCTURE_WORDS = {
    "and", "the", "of", "time", "code", "or", "am", "pm", "date", "loss", "if", "not", "at",
    "with", "for", "to", "by", "be", "been", "is", "are", "as", "where", "when", "how",
    "location", "contact", "name", "policy", "number", "phone", "email", "address", "state",
    "city", "zip", "street", "country", "damage", "estimate", "vehicle", "driver", "owner",
    "insured", "claimant", "report", "police", "fire", "department", "carrier", "agency",
    "description", "accident", "loss", "injury", "claim", "type", "can", "will", "from",
}

def is_form_label(value: str) -> bool:
    """Check if captured value is just form structure/labels rather than actual data."""
    words = value.lower().split()
    if len(words) == 0:
        return True
    # If most words are form structure words, it's likely just labels
    structure_count = sum(1 for w in words if w in FORM_STRUCTURE_WORDS)
    return structure_count > len(words) * 0.6 or len(value) < 3


def extract_first(patterns, text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines:
        for pattern in patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                if match.lastindex:
                    value = match.group(1).strip()
                    if is_form_label(value):
                        continue
                    return value
                return match.group(0).strip()
    return ""


def extract_fields(text: str) -> dict:
    normalized = normalize_text(text, preserve_newlines=True)
    fields = {key: extract_first(patterns, normalized) for key, patterns in FIELD_PATTERNS.items()}

    if not fields.get("claimType") and "injury" in normalized:
        fields["claimType"] = "injury"

    if not fields.get("attachments"):
        fields["attachments"] = "unknown"

    if not fields.get("initialEstimate") and fields.get("estimatedDamage"):
        fields["initialEstimate"] = fields["estimatedDamage"]

    return fields
