import time
from datetime import datetime
from pymongo.database import Database
from app.services.document_validation_service import validate_document
from app.services.extraction_service import extract_data_from_document
from app.services.financial_validation_service import validate_financials
from app.repositories import document_repository

async def process_document(db: Database, file_name: str, file_content: bytes, mime_type: str, document_type: str) -> dict:
    start_time = time.time()
    
    # 1. Validation
    file_validation = validate_document(file_name, file_content, mime_type)
    if file_validation["status"] == "FAILED":
        return _build_response_and_save(db, file_name, document_type, "FAILED", file_validation, {}, {}, False, start_time)

    # 2. Extraction
    try:
        extracted_data = await extract_data_from_document(file_content, mime_type, document_type)
    except Exception as e:
        print(f"Extraction failed: {e}")
        return _build_response_and_save(db, file_name, document_type, "FAILED", file_validation, {}, {}, False, start_time)
        
    # 3. Financial Validation
    validation_results = validate_financials(document_type, extracted_data)
    
    # 4. Save and return
    status = "PASS" if validation_results["overall_status"] == "PASS" else "FAILED"
    
    return _build_response_and_save(db, file_name, document_type, status, file_validation, extracted_data, validation_results, True, start_time)

def _build_response_and_save(db: Database, file_name: str, document_type: str, status: str, file_validation: dict, extracted_data: dict, validation_results: dict, ocr_used: bool, start_time: float):
    processing_time_ms = int((time.time() - start_time) * 1000)
    processing_metadata = {
        "ocr_used": ocr_used,
        "processed_at": datetime.utcnow().isoformat() + "Z",
        "processing_time_ms": processing_time_ms
    }
    
    response = {
        "document_name": file_name,
        "document_type": document_type,
        "processing_status": status,
        "file_validation": file_validation,
        "extracted_data": extracted_data,
        "validation": validation_results,
        "processing_metadata": processing_metadata
    }
    
    # Save to db
    document_repository.create_document_result(db, response)
    
    return response
