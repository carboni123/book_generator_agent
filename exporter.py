# exporter.py
import os
from abc import ABC, abstractmethod
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import logging
from xml.etree import ElementTree as ET


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

    def process_book(self, book: str) -> str:
        """
        Processes a book formatted in XML and converts it into a plain-text string.

        Args:
            book (str): The XML-formatted book string.

        Returns:
            str: The processed plain-text content.
        """
        try:
            root = ET.fromstring(book)
            processed_content = []

            # Process title
            title = root.find("title")
            if title is not None:
                processed_content.append(f"Title: {title.text}\n\n")

            # Process chapters
            chapters = root.find("chapters")
            if chapters is not None:
                for chapter in chapters.findall("chapter"):
                    chapter_title = chapter.find("title")
                    if chapter_title is not None:
                        processed_content.append(f"Chapter: {chapter_title.text}\n")

                    content = chapter.find("content")
                    if content is not None:
                        for section in content.findall("section"):
                            section_title = section.find("title")
                            section_text = section.find("text")
                            if section_title is not None:
                                processed_content.append(f"  Section: {section_title.text}")
                            if section_text is not None:
                                processed_content.append(f"    {section_text.text}\n")

                    # Add chapter summary and notes if available
                    summary = chapter.find("summary")
                    if summary is not None:
                        processed_content.append(f"Summary: {summary.text}\n")
                    notes = chapter.find("notes")
                    if notes is not None:
                        processed_content.append(f"Notes: {notes.text}\n")

            return "\n".join(processed_content)
        except ET.ParseError as e:
            logging.error(f"Error processing book XML: {e}")
            return "Invalid book format."

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
                if textobject.getY() < 1 * inch:  # If text reaches the bottom margin, start a new page
                    c.drawText(textobject)
                    c.showPage()
                    textobject = c.beginText()
                    textobject.setTextOrigin(inch, 10.5 * inch)
                    textobject.setFont("Helvetica", 12)
                textobject.textLine(line)
            c.drawText(textobject)
            c.save()
            logging.info(f"Content successfully exported to {filepath}")
        except Exception as e:
            logging.error(f"Error exporting to PDF: {e}")

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    exporter = PDFExporter()
    with open(sys.argv[1], "r", encoding="utf-8") as book:
        book_xml = book.read()

    # # Example book in XML format
    # book_xml = """
    # <book>
    #     <title>The Book's Title</title>
    #     <chapters>
    #         <chapter>
    #             <title>Introduction</title>
    #             <content>
    #                 <section>
    #                     <title>What is AI?</title>
    #                     <text>Artificial intelligence is...</text>
    #                 </section>
    #             </content>
    #             <summary>An overview of AI concepts.</summary>
    #             <notes>Focus on the basics of AI.</notes>
    #         </chapter>
    #     </chapters>
    # </book>
    # """

    # Process the book and export to PDF
    processed_content = exporter.process_book(book_xml)
    exporter.export(processed_content, "example_book")
    print(f"PDF has been exported to the '{exporter.output_dir}' directory.")