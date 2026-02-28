import pytest
from unittest.mock import patch
from app.services.ocr.ocr_service import OCRService

@pytest.fixture
def ocr_service():
    return OCRService()

@pytest.fixture
def mock_db_drugs():
    return ["ASPIRIN", "WARFARIN", "METFORMIN"]

@pytest.mark.asyncio
@patch("app.services.ocr.ocr_service.ImageProcessor.preprocess_for_ocr")
@patch("app.services.ocr.ocr_service.pytesseract.image_to_string")
async def test_successful_ocr_extraction(mock_image_to_string, mock_preprocess, ocr_service, mock_db_drugs):
    # Arrange
    mock_preprocess.return_value = b"MOCK_PROCESSED_IMAGE_BYTES"
    mock_image_to_string.return_value = "WARNING: ASP1R1N 50MG" # Intentional noise + typo
    
    dummy_image = b"RAW_IMAGE_BYTES"
    
    # Act
    result = await ocr_service.extract_drug_from_image(dummy_image, mock_db_drugs)
    
    # Assert
    assert result["matched_drug"] == "ASPIRIN"
    assert "ASP1R1N" in result["extracted_text"]
    assert result["confidence_score"] > 0.70

@pytest.mark.asyncio
@patch("app.services.ocr.ocr_service.ImageProcessor.preprocess_for_ocr")
@patch("app.services.ocr.ocr_service.pytesseract.image_to_string")
async def test_empty_image_or_no_text(mock_image_to_string, mock_preprocess, ocr_service, mock_db_drugs):
    # Arrange
    mock_preprocess.return_value = b"PROCESSED_BYTES"
    mock_image_to_string.return_value = "   \n  " # White space only
    
    # Act & Assert
    with pytest.raises(ValueError, match="No recognizable text found in the image"):
        await ocr_service.extract_drug_from_image(b"BLANK_IMAGE", mock_db_drugs)

@pytest.mark.asyncio
@patch("app.services.ocr.ocr_service.ImageProcessor.preprocess_for_ocr")
@patch("app.services.ocr.ocr_service.pytesseract.image_to_string")
async def test_no_drug_match_found(mock_image_to_string, mock_preprocess, ocr_service, mock_db_drugs):
    # Arrange
    mock_preprocess.return_value = b"PROCESSED_BYTES"
    # Supply text that doesn't strongly match the Mock DB bounds
    mock_image_to_string.return_value = "CHOCOLATE BAR CANDY" 
    
    # Act & Assert
    with pytest.raises(ValueError, match="did not confidently match any known drugs"):
        await ocr_service.extract_drug_from_image(b"IMAGE", mock_db_drugs)

@pytest.mark.asyncio
@patch("app.services.ocr.ocr_service.ImageProcessor.preprocess_for_ocr")
async def test_invalid_image_format_exception(mock_preprocess, ocr_service, mock_db_drugs):
    # Arrange - ImageProcessor raises ValueError when image is corrupt
    mock_preprocess.side_effect = ValueError("Format not recognized by OpenCV")
    
    # Act & Assert
    with pytest.raises(ValueError, match="Format not recognized by OpenCV"):
        await ocr_service.extract_drug_from_image(b"CORRUPT_BYTES", mock_db_drugs)
