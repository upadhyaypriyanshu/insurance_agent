# Insurance Agent

Lightweight insurance FNOL (First Notice of Loss) processing system with:
- Python backend for text extraction, validation, and routing
- React frontend for file upload / text submission and results display

## Architecture

- `app/` - FastAPI backend modules
- `frontend/` - React + Vite user interface
- `requirements.txt` - Python dependencies
- `.gitignore` - common ignore patterns

## Backend Setup

1. Create and activate a Python virtual environment:

```powershell
cd c:\Users\deepa\Project\insurance_agent
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run the backend:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The backend API will be available at `http://127.0.0.1:8000`.

## Frontend Setup

1. Install Node dependencies:

```powershell
cd frontend
npm install
```

2. Run the frontend development server:

```powershell
npm run dev
```

3. Open the URL provided by Vite, typically `http://127.0.0.1:4173`.

## How to Use

- Upload a PDF or TXT file, or paste FNOL text directly.
- The frontend sends the document to the backend.
- The backend returns JSON with extracted fields, missing fields, recommended route, and reasoning.

## Example JSON Response

```json
{
  "extractedFields": {
    "policyNumber": "ABC-12345",
    "policyholderName": "John Doe",
    "effectiveDates": "01/01/2024 - 12/31/2024",
    "incidentDate": "05/10/2026",
    "incidentTime": "14:30",
    "incidentLocation": "123 Main St, Springfield",
    "incidentDescription": "Rear-end collision at traffic light.",
    "claimant": "John Doe",
    "thirdParties": "Jane Smith",
    "contactDetails": "john.doe@example.com",
    "assetType": "Vehicle",
    "assetID": "1HGCM82633A004352",
    "estimatedDamage": "18000",
    "claimType": "property",
    "attachments": "accident_photo.jpg",
    "initialEstimate": "18000"
  },
  "missingFields": [],
  "recommendedRoute": "Fast-track",
  "reasoning": "Initial estimate is 18000.00, below 25000, so this claim is eligible for fast-track."
}
```

## Routing Logic: Which Route Does Your Claim Take?

The backend automatically routes claims based on extracted field data. Here's exactly when each route is triggered:

### 1. **Manual Review** (if ANY required field is missing)
**Conditions:**
- Any mandatory field is empty or not found: `policyNumber`, `policyholderName`, `incidentDate`, `incidentLocation`, or `incidentDescription`

**When it applies:**
- You submit a PDF or text with incomplete information
- The extraction engine cannot locate a required field

**Example:**
```json
{
  "recommendedRoute": "Manual review",
  "reasoning": "Mandatory fields are missing: policyNumber, incidentLocation. Send claim to manual review.",
  "missingFields": ["policyNumber", "incidentLocation"]
}
```

**User Action:** Review the document and fill in the missing information, then resubmit.

---

### 2. **Investigation Flag** (if fraud-related language detected)
**Conditions:**
- Claim description or other fields contain suspicious keywords: `fraud`, `inconsistent`, `staged`, `fake`, `misrepresentation`

**When it applies:**
- BEFORE any other routing rule is evaluated
- Text contains red-flag language even if all fields are present

**Example:**
```json
{
  "recommendedRoute": "Investigation Flag",
  "reasoning": "Claim description contains potentially fraudulent language, so the claim is flagged for investigation.",
  "extractedFields": {
    "incidentDescription": "staged accident with inconsistent witness statements"
  }
}
```

**Next Step:** Claim goes to fraud investigation team.

---

### 3. **Specialist Queue** (if claim is injury-related)
**Conditions:**
- `claimType` field contains the word `injury`

**When it applies:**
- All required fields present AND no fraud detected
- Injury keyword detected in claim type or description

**Example:**
```json
{
  "recommendedRoute": "Specialist Queue",
  "reasoning": "Claim type is injury, so route to the specialist queue.",
  "extractedFields": {
    "claimType": "injury",
    "incidentDescription": "Person sustained head injury from vehicle collision"
  }
}
```

**Next Step:** Claim goes to injury/liability specialists.

---

### 4. **Fast-track** (if damage is low/moderate)
**Conditions:**
- `initialEstimate` is present AND numeric value is < $25,000

**When it applies:**
- All required fields present
- No fraud or injury keywords detected
- Estimate is below fast-track threshold

**Example:**
```json
{
  "recommendedRoute": "Fast-track",
  "reasoning": "Initial estimate is 18000.00, below 25000, so this claim is eligible for fast-track.",
  "extractedFields": {
    "initialEstimate": "18000",
    "claimType": "property"
  }
}
```

**Next Step:** Claim processed with expedited timeline.

---

### 5. **Standard Review** (default)
**Conditions:**
- All required fields present
- No fraud language detected
- No injury keyword detected
- Estimate is >= $25,000 OR no estimate provided

**When it applies:**
- Claim meets baseline requirements but doesn't fit special categories

**Example:**
```json
{
  "recommendedRoute": "Standard review",
  "reasoning": "No immediate fast-track or specialist rule applies, so the claim proceeds through standard review.",
  "extractedFields": {
    "initialEstimate": "35000",
    "claimType": "property"
  }
}
```

**Next Step:** Claim processed through standard underwriting.

---

### Routing Decision Tree

```
Start
  ↓
[Any mandatory field missing?]
  ├─→ YES → MANUAL REVIEW
  └─→ NO ↓
[Fraud language detected?]
  ├─→ YES → INVESTIGATION FLAG
  └─→ NO ↓
[Claim type is "injury"?]
  ├─→ YES → SPECIALIST QUEUE
  └─→ NO ↓
[Estimate < $25,000?]
  ├─→ YES → FAST-TRACK
  └─→ NO → STANDARD REVIEW
```

---

## Routing Cases and Form Behavior

- `Manual review`:
  - occurs when any required field is missing
  - missing fields are listed in `missingFields`
  - the form should include as much detail as possible in the document or text input so the backend can extract the required fields

- `Investigation Flag`:
  - occurs when the text contains fraud-related terms such as `fraud`, `inconsistent`, or `staged`
  - the form should include the incident description clearly so this language is detectable if present

- `Specialist Queue`:
  - occurs when `claimType` contains `injury`
  - include a clear claim type or injury-related terms in the document text

- `Fast-track`:
  - occurs when `initialEstimate` is present and below `25000`
  - the form should contain a numeric estimate or damage amount such as `Initial Estimate: 18000`

- `Standard review`:
  - occurs when no other special rule applies
  - this is the default route for complete claims without fraud or injury rules

## Why `prompts/extraction_prompt.py` is removed

The current implementation does not use `prompts/extraction_prompt.py`.
The backend uses regex-based extraction in `app/extractor.py`, so the prompt file was an unused placeholder.
It has been removed to avoid confusion.

## Notes

- The backend uses simple extraction heuristics and can be extended later with NLP or AI models.
- If you want AI-based extraction in the future, add a prompt template and integrate it into `app/extractor.py`.
