"""
Main entry point for Bank Statement Table Extraction & Banking Analytics API.
Built for the Bank Muscat BRD Series with FastAPI, scikit-learn, and Hugging Face Transformers.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as api_router

app = FastAPI(
    title="Bank Statement Table Extraction API",
    description=(
        "Production-grade document extraction service for bank statements. "
        "Compliant with Bank Muscat BRD series requirements: supports 3-decimal OMR currencies, "
        "bilingual headers, multi-line narration parsing, accounting balance checks, "
        "and scikit-learn / Hugging Face Transformers for layout & NLP categorization."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    redirect_slashes=False
)

# Enable CORS for banking analytics frontend clients
raw_origins = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = [o.strip() for o in raw_origins.split(",") if o.strip()]
if not allowed_origins:
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API endpoints at root and subpath prefixes for flexible deployment routing
app.include_router(api_router)
app.include_router(api_router, prefix="/api")
app.include_router(api_router, prefix="/api/index")


@app.get("/", tags=["System"])
@app.get("/api", tags=["System"])
@app.get("/api/", tags=["System"])
@app.get("/api/index", tags=["System"])
@app.get("/api/index/", tags=["System"])
def root():
    return {
        "message": "Bank Statement Table Extraction Service is Running",
        "documentation": "/docs",
        "health": "/health",
        "endpoints": {
            "extract": "POST /extract",
            "categorize": "POST /categorize",
            "profiles": "GET /profiles"
        }
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("APP_PORT", 8000))
    host = os.getenv("APP_HOST", "0.0.0.0")
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
