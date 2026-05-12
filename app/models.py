from pydantic import BaseModel
from typing import Dict, List


class TextRequest(BaseModel):
    text: str


class ProcessResponse(BaseModel):
    extractedFields: Dict[str, str]
    missingFields: List[str]
    recommendedRoute: str
    reasoning: str
