from typing import List, Optional
from datetime import datetime
from pymongo.database import Database

def create_document_result(db: Database, result_data: dict) -> dict:
    # Ensure created_at exists for sorting
    if "created_at" not in result_data:
        result_data["created_at"] = datetime.utcnow()
        
    db.documents.insert_one(result_data)
    # The dictionary now has an '_id' field added by PyMongo, but we can return it as-is
    return result_data

def get_document_by_name(db: Database, document_name: str) -> Optional[dict]:
    # Return the latest document by name
    return db.documents.find_one(
        {"document_name": document_name}, 
        sort=[("created_at", -1)]
    )

def list_documents(db: Database, skip: int = 0, limit: int = 100) -> List[dict]:
    cursor = db.documents.find().sort("created_at", -1).skip(skip).limit(limit)
    return list(cursor)
