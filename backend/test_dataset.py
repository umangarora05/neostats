import asyncio
import os
from app.core.database import db
from app.services.document_service import process_document

async def test_dataset():
    file_path = r"d:\projects\neostats\resouse and instructions\New Dataset\Balance Sheet\Consolidated Balance Sheet 2018.pdf"
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    with open(file_path, "rb") as f:
        content = f.read()
        
    print(f"Processing {file_path}...")
    try:
        result = await process_document(
            db=db,
            file_name="Consolidated Balance Sheet 2018.pdf",
            file_content=content,
            mime_type="application/pdf",
            document_type="balance_sheet"
        )
        print("Processing complete!")
        print(f"Status: {result.get('processing_status')}")
        print("Validation Results:")
        checks = result.get('validation', {}).get('checks', [])
        for check in checks:
            print(f" - {check['name']}: {check['status']} (Calc: {check['calculated_value']}, Rep: {check['reported_value']})")
            
        print("\nExtracted Data Keys:", list(result.get('extracted_data', {}).keys()))
    except Exception as e:
        print(f"Error during processing: {e}")

if __name__ == "__main__":
    asyncio.run(test_dataset())
