
import pytest
from unittest.mock import patch, MagicMock, mock_open
from app.core.pdf_extractor import extract_text_from_pdf

def test_extract_text_valid_pdf():
    # Mocking PyPDF2 Reader
    with patch("app.core.pdf_extractor.PyPDF2.PdfReader") as mock_reader:
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Sample PDF Text"
        mock_reader.return_value.pages = [mock_page]
        
        with patch("os.path.exists", return_value=True):
             with patch("builtins.open", mock_open(read_data=b"dummy data")):
                text = extract_text_from_pdf("dummy.pdf")
        assert "Sample PDF Text" in text

def test_extract_text_empty_pdf():
    with patch("app.core.pdf_extractor.PyPDF2.PdfReader") as mock_reader:
        mock_reader.return_value.pages = []
        with patch("os.path.exists", return_value=True):
            with patch("app.core.pdf_extractor.pdfplumber") as mock_plumber:
                # Mock pdfplumber to also return empty
                mock_plumber.open.return_value.__enter__.return_value.pages = []
                mock_plumber.open.return_value.__enter__.return_value.pages = []
                with pytest.raises(Exception):
                    extract_text_from_pdf("empty.pdf")

def test_extract_text_corrupted_pdf():
    # Simulate exception in PyPDF2, triggering pdfplumber fallback (which we also mock or let fail)
    # For simplicity, we'll assume pdfplumber is not installed/mocked to fail too, or just check the exception
    # based on the implementation of extract_text_from_pdf.
    
    # If the function catches generic Exceptions and tries pdfplumber, we need to mock that too.
    with patch("app.core.pdf_extractor.PyPDF2.PdfReader") as mock_reader:
        mock_reader.side_effect = Exception("Corrupted")
        
        # We need to mock os.path.exists as well
        with patch("os.path.exists", return_value=True):
             with patch("app.core.pdf_extractor.pdfplumber") as mock_plumber:
                 mock_plumber.open.return_value.__enter__.return_value.pages = []
                 # If both fail or return empty...
                 
                 # Actually, let's just assert it raises an error if both fail
                 # Or if fallback succeeds.
                 with pytest.raises(Exception): # Assuming it raises PDFExtractionError
                     extract_text_from_pdf("corrupted.pdf")
