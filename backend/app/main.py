from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.routes import documents

app = FastAPI(title=settings.PROJECT_NAME)

allowed_origins = {"https://neostats.umangarora.in"}
if settings.FRONTEND_URL:
    allowed_origins.add(settings.FRONTEND_URL.rstrip("/"))

app.include_router(documents.router, prefix=settings.API_V1_STR + "/documents", tags=["documents"])

@app.get("/api/v1/health")
def health_check():
    return {"status": "ok"}

@app.get("/")
def read_root():
    return {
        "service": settings.PROJECT_NAME,
        "status": "ok",
        "frontend": "https://neostats.umangarora.in",
        "docs": "/docs",
    }

# Exception handler for global application exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):

    print(f"Global Error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_SERVER_ERROR", "message": "An unexpected error occurred."}},
    )


app = CORSMiddleware(
    app,
    allow_origins=sorted(allowed_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)