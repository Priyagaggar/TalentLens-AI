
import logging
from typing import Optional
import os

import PyPDF2

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import pdfplumber
except ImportError:
    pdfplumber = None
    logger.warning("pdfplumber not found. Fallback extraction will not be available.")


class PDFExtractionError(Exception):
    """Custom exception for PDF extraction failures."""
    pass


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts text from a PDF file using PyPDF2 with a fallback to pdfplumber.

    Args:
        file_path (str): The absolute path to the PDF file.

    Returns:
        str: The extracted text as a single string.

    Raises:
        FileNotFoundError: If the file does not exist.
        PDFExtractionError: If text extraction fails with all available methods.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    text = ""
    
    # Method 1: PyPDF2 (Primary)
    try:
        logger.info(f"Attempting to extract text from {file_path} using PyPDF2...")
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        
        text = text.strip()
        if text:
            logger.info("Successfully extracted text using PyPDF2.")
            return text
        else:
            logger.warning("PyPDF2 extracted empty text. Attempting fallback...")

    except Exception as e:
        logger.error(f"PyPDF2 extraction failed: {e}")

    # Method 2: pdfplumber (Fallback)
    if pdfplumber:
        try:
            logger.info(f"Attempting to extract text from {file_path} using pdfplumber...")
            with pdfplumber.open(file_path) as pdf:
                text = ""
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
            
            text = text.strip()
            if text:
                logger.info("Successfully extracted text using pdfplumber.")
                return text
            else:
                logger.error("pdfplumber also returned empty text.")
        except Exception as e:
            logger.error(f"pdfplumber extraction failed: {e}")
    else:
        logger.warning("pdfplumber is not installed, skipping fallback.")

    raise PDFExtractionError(f"Failed to extract text from {file_path}. File might be empty, corrupted, or scanned image.")


if __name__ == "__main__":
    # Test execution
    import sys
    
    # Create a dummy PDF if none is provided via command line
    test_pdf_path = "test_resume.pdf"
    
    # Create a simple PDF for testing purposes if it doesn't exist
    if not os.path.exists(test_pdf_path):
        from reportlab.pdfgen import canvas
        c = canvas.Canvas(test_pdf_path)
        c.drawString(100, 750, "Jane Doe")
        c.drawString(100, 730, "Software Engineer")
        c.drawString(100, 710, "Experience: 5 years in Python and AI.")
        c.save()
        print(f"Created temporary test file: {test_pdf_path}")

    try:
        extracted_text = extract_text_from_pdf(test_pdf_path)
        print("\n--- Extracted Text ---")
        print(extracted_text)
        print("----------------------\n")
    except Exception as e:
        print(f"Error: {e}")
    
    # cleanup
    if os.path.exists("test_resume.pdf"):
        os.remove("test_resume.pdf") 
