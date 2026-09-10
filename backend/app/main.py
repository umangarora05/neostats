from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api.routes import documents

app = FastAPI(title=settings.PROJECT_NAME)

allowed_origins = ["*"]
if settings.FRONTEND_URL:
    allowed_origins = [settings.FRONTEND_URL.rstrip("/")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=bool(settings.FRONTEND_URL),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router, prefix=settings.API_V1_STR + "/documents", tags=["documents"])

@app.get("/api/v1/health")
def health_check():
    return {"status": "ok"}

from fastapi.templating import Jinja2Templates
project_root = Path(__file__).resolve().parents[3]
frontend_root = project_root / "frontend"
templates = Jinja2Templates(directory=str(frontend_root / "templates"))

static_directory = frontend_root / "static"
if static_directory.is_dir():
    app.mount("/static", StaticFiles(directory=str(static_directory)), name="static")

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/document/{document_name}")
def view_document(request: Request, document_name: str):
    return templates.TemplateResponse("document_result.html", {"request": request, "document_name": document_name})

# Exception handler for global application exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):

    print(f"Global Error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_SERVER_ERROR", "message": "An unexpected error occurred."}},
    )