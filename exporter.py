# exporter.py
import os
from abc import ABC, abstractmethod
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import logging


class Exporter(ABC):
    """
    Abstract base class for exporting content.
    """

    def __init__(self, output_dir="output"):
        """
        Initializes the exporter object.
        """
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    @abstractmethod
    def export(self, content, filename):
        """
        Abstract method to export content to a file.

        Args:
            content (str): The content to export.
            filename (str): The name of the output file.
        """
        pass


class PDFExporter(Exporter):
    """
    Concrete class for exporting content to a PDF file.
    """

    def __init__(self, output_dir="output"):
        """
        Initializes the PDFExporter object.
        """
        super().__init__(output_dir)
        logging.info("PDFExporter initialized.")
        
    def export(self, content, filename):
        """
        Exports content to a PDF file.

        Args:
            content (str): The content to export.
            filename (str): The name of the output PDF file.
        """
        try:
            filepath = os.path.join(self.output_dir, filename + ".pdf")
            c = canvas.Canvas(filepath, pagesize=letter)
            textobject = c.beginText()
            textobject.setTextOrigin(inch, 10.5 * inch)
            textobject.setFont("Helvetica", 12)

            lines = content.split('\n')
            for line in lines:
                textobject.textLine(line)
            c.drawText(textobject)
            c.save()
            logging.info(f"Content successfully exported to {filepath}")
        except Exception as e:
            logging.error(f"Error exporting to PDF: {e}")