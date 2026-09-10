from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from pymongo.database import Database
from typing import List
from app.core.database import get_db
from app.services.document_service import process_document
from app.repositories import document_repository
from app.schemas.document import DocumentResponse

router = APIRouter()

@router.post("/process", response_model=DocumentResponse)
async def process_document_endpoint(
    file: UploadFile = File(...),
    document_type: str = Form(...),
    db: Database = Depends(get_db)
):
    if document_type not in ["invoice", "balance_sheet", "profit_and_loss", "cash_flow_statement"]:
        raise HTTPException(status_code=400, detail="Invalid document_type")
        
    mime_type = file.content_type
    if mime_type not in ["application/pdf", "image/jpeg", "image/png", "image/jpg"]:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": "UNSUPPORTED_FILE_TYPE",
                    "message": "Only PDF / JPG / PNG documents are supported."
                }
            }
        )

    file_content = await file.read()
    response_data = await process_document(db, file.filename, file_content, mime_type, document_type)
    
    return response_data

@router.get("/{document_name}", response_model=DocumentResponse)
def get_document(document_name: str, db: Database = Depends(get_db)):
    doc = document_repository.get_document_by_name(db, document_name)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return DocumentResponse(
        document_name=doc.get("document_name"),
        document_type=doc.get("document_type"),
        processing_status=doc.get("processing_status"),
        file_validation=doc.get("file_validation"),
        extracted_data=doc.get("extracted_data") or {},
        validation=doc.get("validation") or {"checks": [], "overall_status": "UNKNOWN", "issues": []},
        processing_metadata=doc.get("processing_metadata")
    )

@router.get("", response_model=List[DocumentResponse])
def list_documents(skip: int = 0, limit: int = 100, db: Database = Depends(get_db)):
    docs = document_repository.list_documents(db, skip=skip, limit=limit)
    return [
        DocumentResponse(
            document_name=doc.get("document_name"),
            document_type=doc.get("document_type"),
            processing_status=doc.get("processing_status"),
            file_validation=doc.get("file_validation"),
            extracted_data=doc.get("extracted_data") or {},
            validation=doc.get("validation") or {"checks": [], "overall_status": "UNKNOWN", "issues": []},
            processing_metadata=doc.get("processing_metadata")
        ) for doc in docs
    ]
