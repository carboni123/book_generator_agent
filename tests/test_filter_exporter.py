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
from xml.etree import ElementTree as ET

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Register a font to ensure text rendering (optional but recommended for text checks)
pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))  # Assuming 'Vera.ttf' exists

@pytest.fixture
def pdf_exporter():
    return PDFExporter(output_dir="test_output")

def test_pipeline(pdf_exporter):
    # Read the book and review content from files
    with open("tests/book.txt", "r", encoding="utf-8") as file:
        book_xml = file.read()
    with open("tests/review.txt", "r", encoding="utf-8") as file:
        review_xml = file.read()

    #Parse Review
    try:
        root = ET.fromstring(review_xml)
        score = int(root.find(".//score/overall").text)
        feedback_elements = root.findall(".//feedback/aspect")
        feedback = " ".join([f.find("comment").text for f in feedback_elements])
    except Exception as e:
         pytest.fail(f"Error parsing review XML: {e}")
         return

    filename = "pipeline_test"

    # Test with approval
    filter_approved = Filter(threshold=6) #changed threshold to 6
    
    processed_book = pdf_exporter.process_book(book_xml)
    if filter_approved.is_approved(score, feedback):
        pdf_exporter.export(processed_book, filename + "_approved")
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
    filter_disapproved = Filter(threshold=9) #Changed threshold to 9
    if not filter_disapproved.is_approved(score, feedback):
        filepath_disapproved = os.path.join(pdf_exporter.output_dir, filename + "_disapproved.pdf")
        assert not os.path.exists(filepath_disapproved), f"PDF file should not exist at {filepath_disapproved}"
    else:
        pytest.fail("Disapproved book was approved by the filter")