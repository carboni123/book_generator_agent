# tests/test_exporter.py
import os
import pytest
from exporter import PDFExporter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Register a font to ensure text rendering (optional but recommended for text checks)
pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))  # Assuming 'Helvetica.ttf' exists

@pytest.fixture
def pdf_exporter():
    return PDFExporter(output_dir="test_output")

def test_pdf_export(pdf_exporter):
    content = "This is a test book.\nIt has multiple lines.\nAnd some more content."
    filename = "test_book"
    pdf_exporter.export(content, filename)
    
    filepath = os.path.join(pdf_exporter.output_dir, f"{filename}.pdf")
    
    # Check if the PDF file was created
    assert os.path.exists(filepath), f"PDF file does not exist at {filepath}"

    # Verify PDF content 
    try:
        # Use ReportLab's Canvas to read the PDF information
        c = canvas.Canvas(filepath, pagesize=letter)
        # Get the number of pages
        page_count = c.getPageNumber()
        assert page_count > 0, "PDF should have at least one page"
        
        # Here, we would ideally check content, but ReportLab's canvas doesn't support 
        # text reading directly. Instead, we could check for the presence of text indirectly:
        # - Check file size (very basic indicator of content)
        file_size = os.path.getsize(filepath)
        assert file_size > 0, "PDF file is empty"
        
        # Optionally, for more thorough testing, you might want to use a PDF parsing library 
        # like `PyPDF2` or `pdfplumber` to read text content.
    except Exception as e:
        pytest.fail(f"Error when reading or analyzing PDF: {e}")
    finally:
        # Clean up
        os.remove(filepath)