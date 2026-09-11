import os
import json
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import Dict, Any, Type
import base64

from app.schemas.extraction import (
    InvoiceExtraction,
    BalanceSheetExtraction,
    ProfitAndLossExtraction,
    CashFlowExtraction
)
from app.core.config import settings

def get_gemini_client():
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set.")
    return genai.Client(api_key=settings.GEMINI_API_KEY)

def determine_schema(document_type: str) -> Type[BaseModel]:
    if document_type == "invoice":
        return InvoiceExtraction
    elif document_type == "balance_sheet":
        return BalanceSheetExtraction
    elif document_type == "profit_and_loss":
        return ProfitAndLossExtraction
    elif document_type == "cash_flow_statement":
        return CashFlowExtraction
    else:
        raise ValueError(f"Unknown document type: {document_type}")

async def extract_data_from_document(file_content: bytes, mime_type: str, document_type: str) -> Dict[str, Any]:
    """
    Extracts structured data from the provided document bytes using Gemini Multimodal.
    """
    client = get_gemini_client()
    schema = determine_schema(document_type)

    prompt = f"""
    You are an expert document data extraction system.
    Please extract the data from the provided {document_type} according to the provided JSON schema.
    
    JSON SCHEMA STRUCTURE TO FOLLOW:
    {json.dumps(schema.model_json_schema(), indent=2)}
    
    CRITICAL INSTRUCTIONS:
    1. Extract ALL meaningful information visible in the document. Do not just look for the standard fields.
    2. If a value is missing or not visible in the document, you MUST return null. DO NOT hallucinate, infer, or assume values.
    3. For every ExtractedValue, fill out the `evidence` object. Provide the exact `source_text` from the document that supports the value, and the `page_number` where it is found.
    4. For any additional headers, totals, or fields not explicitly named in the schema, include them in the `additional_header_fields` dictionary.
    5. Ensure complete table extraction. Include all rows in `line_items`.
    6. Return ONLY valid JSON matching the exact schema provided above.
    7. For confidence, you can estimate a confidence score between 0.0 and 1.0.
    """

    # Using gemini-2.5-flash or gemini-1.5-flash as per the SDK availability
    # In this case study we can use gemini-1.5-flash
    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=[
                types.Part.from_bytes(data=file_content, mime_type=mime_type),
                prompt
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.0
            ),
        )
        # Parse response to dict
        return json.loads(response.text)
    except Exception as e:
        print(f"Extraction Error: {e}")
        # Try fallback to gemini-3.6-flash if needed
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=[
                types.Part.from_bytes(data=file_content, mime_type=mime_type),
                prompt
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.0
            ),
        )
        return json.loads(response.text)
