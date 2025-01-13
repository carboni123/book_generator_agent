# tests/test_filter_exporter.py
import os
import pytest
from exporter import PDFExporter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from filter import Filter
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Register a font to ensure text rendering (optional but recommended for text checks)
pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))  # Assuming 'Vera.ttf' exists

@pytest.fixture
def pdf_exporter():
    return PDFExporter(output_dir="test_output")

def test_pipeline(pdf_exporter):
    # Mock reviewer output
    approved_score = 8
    approved_feedback = "This book is fantastic!"
    disapproved_score = 4
    disapproved_feedback = "This book needs a lot of work."
    content = "Test Content"
    filename = "pipeline_test"

    # Test with approval
    filter_approved = Filter(threshold=7)
    if filter_approved.is_approved(approved_score, approved_feedback):
        pdf_exporter.export(content, filename + "_approved")
        filepath_approved = os.path.join(pdf_exporter.output_dir, filename + "_approved.pdf")
        assert os.path.exists(filepath_approved), f"PDF file does not exist at {filepath_approved}"

        # Basic pdf check
        try:
            c = canvas.Canvas(filepath_approved, pagesize=letter)
            page_count = c.getPageNumber()
            assert page_count > 0, "PDF should have at least one page"

            #Basic file size check
            file_size = os.path.getsize(filepath_approved)
            assert file_size > 0, "PDF file is empty"

        except Exception as e:
          pytest.fail(f"Error when reading approved pdf: {e}")
        finally:
             os.remove(filepath_approved)

    else:
      pytest.fail("Approved book was not approved by the filter")

    # Test with disapproval
    filter_disapproved = Filter(threshold=7)
    if not filter_disapproved.is_approved(disapproved_score, disapproved_feedback):
        filepath_disapproved = os.path.join(pdf_exporter.output_dir, filename + "_disapproved.pdf")
        assert not os.path.exists(filepath_disapproved), f"PDF file should not exist at {filepath_disapproved}"
    else:
        pytest.fail("Disapproved book was approved by the filter")