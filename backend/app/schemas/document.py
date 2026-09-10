from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from datetime import datetime

class FileValidation(BaseModel):
    file_type: str
    is_supported: bool
    is_readable: bool
    page_count: int
    status: str

class ValidationCheck(BaseModel):
    name: str
    formula: str
    operands: Dict[str, Any]
    calculated_value: Optional[float]
    reported_value: Optional[float]
    variance: Optional[float]
    status: str

class ValidationResult(BaseModel):
    checks: List[ValidationCheck]
    overall_status: str
    issues: List[str]

class ProcessingMetadata(BaseModel):
    ocr_used: bool
    processed_at: str
    processing_time_ms: int

class DocumentResponse(BaseModel):
    document_name: str
    document_type: str
    processing_status: str
    file_validation: FileValidation
    extracted_data: Dict[str, Any]
    validation: ValidationResult
    processing_metadata: ProcessingMetadata

    class Config:
        from_attributes = True

class ErrorResponse(BaseModel):
    error: Dict[str, str]
