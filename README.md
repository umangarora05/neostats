# NeoStats Intelligent Document Platform

## Solution Overview & Architecture
NeoStats is an end-to-end AI-powered document extraction and validation platform. It accepts financial documents (Invoices, Balance Sheets, Profit & Loss Statements, and Cash Flow Statements), validates the files, extracts structured data, runs financial validations, and presents the results through a modern, responsive web dashboard.

The architecture follows a decoupled pattern:
- **Frontend Layer**: HTML/CSS templates served directly by FastAPI. Features a premium glassmorphism design.
- **API Layer**: FastAPI application exposing REST endpoints for document processing and retrieval.
- **Service Layer**: 
  - `document_validation_service`: File integrity and limits.
  - `extraction_service`: Interacts with LLM for structured output.
  - `financial_validation_service`: Performs robust mathematical checks.
- **Data Layer**: SQLAlchemy ORM backing into a persistent SQLite database (`database.db`).

## Technology Stack
- **Backend Framework**: FastAPI (High performance, async, built-in OpenAPI documentation)
- **Database**: MongoDB Atlas with PyMongo (NoSQL schema-less document store perfect for extracted JSON data)
- **AI / Extraction Model**: Google Gemini Flash via `google-genai` SDK (Fast multimodal extraction with structured JSON schemas)
- **Frontend**: Vanilla HTML/CSS/JS (No heavy frameworks, modern UI)

## Local Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository_url>
   cd neostats
   ```

2. **Create a virtual environment and install dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up Environment Variables**
   Create a `.env` file in the root directory (use `.env.example` as a template). Ensure you add your MongoDB Atlas Connection String.

4. **Run the Server**
   ```bash
   uvicorn app.main:app --reload
   ```
   Access the dashboard at `http://localhost:8000`
   Access API Docs (Swagger) at `http://localhost:8000/docs`

## Environment Variables (.env.example)
```env
# Server Settings
PROJECT_NAME="NeoStats"
API_V1_STR="/api/v1"

# Database (MongoDB Atlas)
DATABASE_URL="mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority"

# LLM Config
GEMINI_API_KEY="your_api_key_here"
```

## API Request Examples

### Process Document (POST /api/v1/documents/process)
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/documents/process' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@sample_invoice.pdf;type=application/pdf' \
  -F 'document_type=invoice'
```

### Retrieve Document (GET /api/v1/documents/{document_name})
```bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/documents/sample_invoice.pdf' \
  -H 'accept: application/json'
```

## Extraction Model
This application utilizes **Google Gemini 1.5/2.5 Flash** via multimodal prompts. The model directly ingests the document bytes (PDF/JPG/PNG) and extracts data natively into strict JSON structures provided by Pydantic schemas. It also extracts evidence texts and page numbers for each field.

## Financial Validation Rules Implemented
- **Invoice**: Qty * Price = Line Total; Sum of lines = Subtotal; Subtotal + Tax - Discount = Total. Checks cash/change if present.
- **Balance Sheet**: Assets = Liabilities + Equity. Sums individual asset and liability components to cross-check totals.
- **Profit & Loss**: Validates Net Profit calculations and aggregates component incomes/expenditures.
- **Cash Flow**: Sums Operating, Investing, Financing, and FX adjustments to verify Net Change. Validates Opening + Change = Closing cash.

## Persistence Approach
**MongoDB Atlas** is used as the persistent store via `pymongo`. Since the extracted data comprises deeply nested and dynamic unstructured JSON fields, a NoSQL document database like MongoDB is an exponentially better fit than a relational SQL DB. Each processed document's raw structured output is inserted directly into a MongoDB collection alongside its processing metadata. The dashboard retrieves these results dynamically.

## Known Limitations
- Gemini's built-in PDF ingestion is highly effective but may struggle with severely rotated or extremely blurry scans without prior preprocessing (e.g., specialized OCR pipelines like Tesseract/EasyOCR).
- Only a fixed set of financial formulas are checked. Highly custom line-item terminologies might bypass granular validation.

## Production Improvements
- Add a dedicated asynchronous job queue (e.g., Celery or RQ) so the UI doesn't block while waiting for LLM extraction.
- Integrate AWS S3 or GCP Cloud Storage for securely storing uploaded document files instead of keeping them only in-memory.
- Implement specialized pre-processing (deskewing, contrast enhancement) before sending to the LLM.

## AI Tools Used
This project was developed with the assistance of GitHub Copilot and Google Gemini to accelerate writing boilerplate code, UI styling, and robust validation logic.

## Deployed Links
- **Frontend / Dashboard**: https://neostats.umangarora.in/
- **API Base URL**: https://neostats-api.onrender.com
- **Swagger Docs**: https://neostats-api.onrender.com/docs

## Deploying with Render and Vercel

### 1. Deploy the backend to Render

1. Create a new **Web Service** in Render from this repository.
2. Use the included `render.yaml`, or set these values manually:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r ../requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path**: `/api/v1/health`
3. Add `DATABASE_URL` and `GEMINI_API_KEY` as Render environment variables. Use MongoDB Atlas for `DATABASE_URL`.
4. Copy the deployed Render URL, for example `https://neostats-api.onrender.com`.

The backend includes `backend/runtime.txt` to pin Render to Python 3.12.4. This is required because the currently pinned dependency versions do not provide compatible prebuilt wheels for Python 3.14.

### 2. Deploy the frontend to Vercel

1. Import the same repository into Vercel.
2. Set **Root Directory** to `frontend`.
3. Deploy with the default static site settings. `frontend/vercel.json` routes `/` to the dashboard template.
4. Before deploying, set `window.NEOSTATS_API_BASE_URL` in `frontend/config.js` to the Render URL:

   ```js
   window.NEOSTATS_API_BASE_URL = "https://neostats-api.onrender.com";
   ```

5. Copy the Vercel URL and set Render's `FRONTEND_URL` environment variable to that exact URL, without a trailing slash. Redeploy the Render service.

When the Vercel dashboard is opened, it calls `GET /api/v1/health` on the Render service and displays the API connection status. Uploads and document history use the same Render API base URL.
