from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import io
import pdfplumber
from .models import TextRequest, ProcessResponse
from .extractor import extract_fields
from .validator import find_missing_fields
from .router import route_claim

app = FastAPI(
    title="Insurance Claim Processing Agent",
    description="Lightweight FNOL processing backend for field extraction and routing.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def process_document(text: str) -> ProcessResponse:
    fields = extract_fields(text)
    missing_fields = find_missing_fields(fields)
    recommended_route, reasoning = route_claim(fields, missing_fields)
    return ProcessResponse(
        extractedFields=fields,
        missingFields=missing_fields,
        recommendedRoute=recommended_route,
        reasoning=reasoning,
    )


@app.get("/", response_class=JSONResponse)
def health_check():
    return {"status": "ok", "message": "Insurance agent backend is running."}


@app.post("/process-text", response_model=ProcessResponse)
def process_text(request: TextRequest):
    return process_document(request.text)


@app.post("/process-file", response_model=ProcessResponse)
async def process_file(file: UploadFile = File(...)):
    content_type = file.content_type or ""
    raw = await file.read()

    if content_type == "application/pdf" or file.filename.lower().endswith(".pdf"):
        try:
            with pdfplumber.open(io.BytesIO(raw)) as pdf:
                text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        except Exception:
            text = raw.decode("utf-8", errors="ignore")
    else:
        text = raw.decode("utf-8", errors="ignore")

    return process_document(text)
