"""
FastAPI REST API Endpoints for Bank Statement Table Extraction & Banking Analytics.
"""

import os
import time
import tempfile
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Query, Response, status, Depends, Security
from fastapi.security.api_key import APIKeyHeader
from fastapi.responses import JSONResponse, PlainTextResponse

from app.schemas.transaction import (
    ExtractionResponse,
    CategorizeRequest,
    CategorizeResponse,
    CategorizeResult
)
from app.services.extractor import StatementExtractorService
from app.extraction.profiles import PROFILES

router = APIRouter()
extractor_service = StatementExtractorService()

MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE_BYTES", 20 * 1024 * 1024))  # 20 MB

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(x_api_key: Optional[str] = Security(api_key_header)) -> Optional[str]:
    """
    Validate incoming request against configured API_KEY.
    If API_KEY is unset or empty, requests are permitted (open development/demo mode).
    If API_KEY is set, requests must supply the exact key in the X-API-Key header.
    """
    expected_key = os.getenv("API_KEY", "").strip()
    if expected_key:
        if not x_api_key or x_api_key != expected_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing API key in 'X-API-Key' header."
            )
    return x_api_key


@router.get("/health", tags=["System"])
def health_check() -> Dict[str, Any]:
    """Report API health status, loaded machine learning components, and supported profiles."""
    return {
        "status": "healthy",
        "service": "Bank Statement Table Extraction API",
        "version": "1.0.0",
        "brd_series": "Bank Muscat Series",
        "ml_line_classifier_loaded": extractor_service.line_classifier.pipeline is not None,
        "nlp_categorizer_loaded": extractor_service.nlp_categorizer.pipeline is not None,
        "supported_profiles": list(PROFILES.keys()),
        "timestamp": time.time()
    }


@router.get("/profiles", tags=["Configuration"])
def list_profiles() -> Dict[str, Any]:
    """Return all configured bank statement layout profiles."""
    profiles_info = []
    for pid, p in PROFILES.items():
        profiles_info.append({
            "id": p.id,
            "name": p.name,
            "country": p.country,
            "currency": p.currency,
            "currency_decimals": p.currency_decimals,
            "date_format": p.date_format,
            "direction_derivation": p.direction_derivation,
            "multi_account": p.multi_account
        })
    return {"profiles": profiles_info, "count": len(profiles_info)}


@router.post(
    "/extract",
    response_model=ExtractionResponse,
    summary="Extract structured transaction table from bank statement PDF",
    tags=["Extraction"]
)
async def extract_statement(
    file: UploadFile = File(..., description="Bank statement PDF file"),
    profile: Optional[str] = Form("auto", description="Statement profile ID ('auto', 'bank_muscat', 'straits_capital', etc.)"),
    output_format: Optional[str] = Form("json", description="Output format: 'json', 'csv', or 'benchmark'"),
    use_ml: bool = Form(True, description="Enable scikit-learn ML line & table classification"),
    use_transformers: bool = Form(False, description="Enable Hugging Face transformers for NLP classification"),
    api_key: Optional[str] = Depends(verify_api_key)
):
    """
    Extract, normalize, validate, and categorize transactions from an input bank statement PDF.
    Supports Bank Muscat (OMR 3-decimal), international formats, and auto-detection.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Please upload a PDF document."
        )

    # Read content with size check
    pdf_bytes = await file.read()
    if len(pdf_bytes) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum permissible size of {MAX_UPLOAD_SIZE // (1024*1024)} MB."
        )
    if len(pdf_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )
    if not pdf_bytes.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid PDF format: file header does not begin with '%PDF-' signature."
        )

    try:
        response_obj = extractor_service.extract_from_bytes(
            pdf_bytes=pdf_bytes,
            file_name=file.filename,
            profile_id=profile,
            use_ml=use_ml,
            use_transformers=use_transformers
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Extraction pipeline failure: {str(exc)}"
        )

    # Handle requested output format
    fmt = (output_format or "json").lower()
    if fmt == "csv":
        csv_text = StatementExtractorService.to_csv(response_obj)
        return PlainTextResponse(
            content=csv_text,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={file.filename}.csv"}
        )
    elif fmt == "benchmark":
        return JSONResponse(content=response_obj.to_benchmark_submission())
    else:
        return response_obj


@router.post(
    "/categorize",
    response_model=CategorizeResponse,
    summary="Categorize transaction narratives using ML / Hugging Face NLP",
    tags=["Banking Analytics"]
)
def categorize_transactions(
    req: CategorizeRequest,
    api_key: Optional[str] = Depends(verify_api_key)
):
    """Classify free-form transaction descriptions and extract payment channel and reference IDs."""
    results: List[CategorizeResult] = []
    try:
        for desc in req.descriptions:
            cat, conf, entities = extractor_service.nlp_categorizer.categorize(
                desc, use_transformers=req.use_transformers
            )
            results.append(CategorizeResult(
                description=desc,
                category=cat,
                confidence=conf,
                channel=entities.get("channel"),
                reference_id=entities.get("reference_id"),
                counterparty=entities.get("counterparty")
            ))
        model_name = (
            f"HuggingFace Transformers ({extractor_service.nlp_categorizer.hf_model_name})"
            if req.use_transformers
            else "scikit-learn TF-IDF Classifier"
        )
        return CategorizeResponse(
            results=results,
            model_used=model_name
        )
    except RuntimeError as re:
        if req.use_transformers:
            raise HTTPException(
                status_code=503,
                detail=f"Hugging Face Transformer pipeline unavailable: {str(re)}. Set use_transformers=false to use fast production scikit-learn classifier."
            )
        raise HTTPException(status_code=500, detail=str(re))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
