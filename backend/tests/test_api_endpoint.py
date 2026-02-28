from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, AsyncMock

client = TestClient(app)

@patch('app.api.v1.ocr.OCRService.extract_drug_from_image', new_callable=AsyncMock)
def test_extract_drug(mock_extract):
    # Mock the return value of the async OCRService to match our API contract
    mock_extract.return_value = {
        "success": True,
        "data": {
            "extracted_text": "AM0XIC1LL1N 500 MG",
            "matched_drug": "AMOXICILLIN",
            "confidence_score": 0.85
        },
        "error": None
    }
    
    # Test file upload
    with open("backend/test_rotated.png", "rb") as image_file:
        response = client.post(
            "/api/v1/ocr/extract-drug",
            files={"image": ("test_rotated.png", image_file, "image/png")}
        )
    
    print("\nAPI Response Output:")
    print(response.json())
    
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["data"]["matched_drug"] == "AMOXICILLIN"
    print("\n✅ FastAPI Endpoint correctly handled image upload and returned OCR JSON envelope.")

if __name__ == "__main__":
    test_extract_drug()
