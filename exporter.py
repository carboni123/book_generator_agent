# exporter.py
import os
from abc import ABC, abstractmethod
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, PageBreak
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.colors import black
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

    def __init__(self, output_dir="output", author="AI Book Generator"):
        """
        Initializes the PDFExporter object.
        """
        super().__init__(output_dir)
        logging.info("PDFExporter initialized.")
        self.styles = getSampleStyleSheet()
        self.normal_style = self.styles["Normal"]
        self.author = author
        self.page_number = 0  # Start at page 0
        self.first_page = True  # Flag to indicate if is first page

    def _parse_book_xml(self, book_xml: str) -> dict:
        """Parses the XML book structure and returns a dictionary."""
        try:
            root = ET.fromstring(book_xml)
            book_data = {}

            # Get book title
            title_element = root.find("title")
            book_data["title"] = (
                title_element.text if title_element is not None else "Untitled"
            )

            # Extract chapters
            chapters_data = []
            chapters_element = root.find("chapters")
            if chapters_element is not None:
                for chapter_element in chapters_element.findall("chapter"):
                    chapter_data = {}
                    title_element = chapter_element.find("title")
                    chapter_data["title"] = (
                        title_element.text if title_element is not None else "No Title"
                    )

                    content_data = []
                    content_element = chapter_element.find("content")
                    if content_element is not None:
                        for section_element in content_element.findall("section"):
                            section_data = {}
                            section_title = section_element.find("title")
                            section_text = section_element.find("text")
                            section_data["title"] = (
                                section_title.text
                                if section_title is not None
                                else None
                            )
                            section_data["text"] = (
                                section_text.text if section_text is not None else None
                            )
                            content_data.append(section_data)
                    chapter_data["content"] = content_data

                    summary_element = chapter_element.find("summary")
                    chapter_data["summary"] = (
                        summary_element.text if summary_element is not None else None
                    )
                    notes_element = chapter_element.find("notes")
                    chapter_data["notes"] = (
                        notes_element.text if notes_element is not None else None
                    )
                    chapters_data.append(chapter_data)

            book_data["chapters"] = chapters_data
            return book_data

        except ET.ParseError as e:
            logging.error(f"Error parsing book XML: {e}")
            raise ValueError(f"Invalid book format: {e}")

    def _format_text_from_book_data(self, book_data: dict) -> list[dict]:
        """Formats the extracted book data into a list of dictionaries,
        ready for ReportLab's Platypus."""
        formatted_content = []
        # First Page (Cover)
        formatted_content.append(
            {"type": "cover", "title": book_data["title"], "author": self.author}
        )

        for chapter in book_data.get("chapters", []):
            formatted_content.append(
                {"type": "chapter_title", "title": chapter["title"]}
            )
            for section in chapter["content"]:
                if section["title"]:
                    formatted_content.append(
                        {"type": "section_title", "title": section["title"]}
                    )
                if section["text"]:
                    formatted_content.append(
                        {"type": "paragraph", "text": section["text"]}
                    )

        #   if chapter["summary"]:
        #      formatted_content.append({"type": "paragraph", "text": "Summary: " + chapter['summary']})
        #   if chapter["notes"]:
        #      formatted_content.append({"type": "paragraph", "text": "Notes: " + chapter['notes']})

        return formatted_content

    def process_book(self, book: str) -> list[dict]:
        """
        Processes a book formatted in XML and returns a list of dictionaries with extracted and formatted content

        Args:
            book (str): The XML-formatted book string.

        Returns:
            list[dict]: The processed content, ready for export
        """
        try:
            book_data = self._parse_book_xml(book)
            formatted_text = self._format_text_from_book_data(book_data)
            return formatted_text
        except ValueError as e:
            logging.error(f"Error processing book: {e}")
            return [{"type": "error", "text": f"Error: {e}"}]

    def _build_pdf(self, filepath, content):
        """Builds the PDF document using ReportLab's Platypus."""
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        normal_style = styles["Normal"]
        normal_style.alignment = TA_JUSTIFY
        normal_style.firstLineIndent = 0.3 * inch
        title_style = styles["Title"]
        title_style.alignment = TA_CENTER
        cover_title_style = styles["Title"]
        cover_title_style.fontSize = 36
        cover_title_style.alignment = TA_CENTER
        cover_author_style = styles["h2"]
        cover_author_style.alignment = TA_CENTER
        chapter_title_style = styles["h2"]
        chapter_title_style.alignment = TA_CENTER
        section_title_style = styles["h3"]
        section_title_style.textColor = black

        for item in content:
            if item["type"] == "cover":
                story.append(Spacer(1, 2 * inch))  # Add some space before the title
                story.append(Paragraph(item["title"], cover_title_style))
                story.append(Paragraph(self.author, cover_author_style))
                self.first_page = False
            elif item["type"] == "chapter_title":
                story.append(PageBreak())
                story.append(Paragraph(item["title"], chapter_title_style))
            elif item["type"] == "section_title":
                story.append(Paragraph(item["title"], section_title_style))
            elif item["type"] == "paragraph":
                story.append(Paragraph(item["text"], normal_style))
            elif item["type"] == "error":
                story.append(Paragraph(item["text"], styles["Normal"]))

        doc.build(story)

    def export(self, content: list[dict], filename: str):
        """
        Exports content to a PDF file, applying formatting.

        Args:
            content (list[dict]): The content to export.
            filename (str): The name of the output PDF file.
        """
        filepath = os.path.join(self.output_dir, filename + ".pdf")
        try:
            self._build_pdf(filepath, content)
            logging.info(f"Content successfully exported to {filepath}")

        except (IOError, OSError) as e:
            logging.error(f"File error during PDF export: {e}")
            raise
        except Exception as e:
            logging.error(f"Error during PDF export: {e}")
            raise


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)
    exporter = PDFExporter()
    try:
        with open(sys.argv[1], "r", encoding="utf-8") as book_file:
            book_xml = book_file.read()
    except FileNotFoundError:
        logging.error(f"File not found error: {sys.argv[1]}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error reading file: {e}")
        sys.exit(1)

    # Process the book and export to PDF
    try:
        processed_content = exporter.process_book(book_xml)
        exporter.export(processed_content, "example_book")
        print(f"PDF has been exported to the '{exporter.output_dir}' directory.")
    except Exception as e:
        logging.error(f"Failed to process or export book: {e}")
        sys.exit(1)
