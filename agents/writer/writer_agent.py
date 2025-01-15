# agents/writer/writer_agent.py
from api.api import API
from xml.etree import ElementTree
import logging
import asyncio


class WriterAgent:
    """
    Agent responsible for generating book content.
    """

    def __init__(self, api: API):
        self.api = api
        self.role_description = self._load_role_description()
        self.book_structure = self._load_output_structure()

    def _load_role_description(self) -> str:
        """
        Loads the role description for this agent from role.xml
        """
        tree = ElementTree.parse("agents/writer/role.xml")
        root = tree.getroot()
        description = root.find("description").text
        return description

    def _load_output_structure(self) -> str:
        """
        Loads the output structure for this agent from structure.xml
        """
        prefix = """Output Structure Instructions:
1. The LLM must adhere strictly to the schema provided.
2. The LLM must use the XML format provided.
        """
        with open("agents/writer/structure.xml", "r", encoding="utf-8") as xml:
            content = xml.read()  # Read the entire file content
        return prefix + content

    def _load_instructions(self) -> str:
        instructions = "Write a book with about 300 words per chapter. The book should have at least 4 chapters."
        return instructions

    async def generate_book(self, input, book=None, review=None):
        """
        Generates a book based on a given input prompt, structured into chapters and sections.

        Args:
            input (str): The input prompt for the book.
            book (str, optional): The existing book content for refinement. Defaults to None.
            review (str, optional): The review feedback for improvement. Defaults to None.

        Returns:
            str: The generated book in XML format.
        """
        logging.info(f"Generating book with prompt: {input}")
        # Create the root element
        prompt = "<writer_prompt>"
        # Add subelements
        prompt += f"<input_instructions>{self._load_instructions()}</input_instructions>"
        if book:
            prompt += f"<book>{book}</book>"
        if review:
            prompt += f"<review>{review}</review>"
        prompt += f"<theme>{input}</theme>"
        prompt += f"<role_description>{self._load_role_description()}</role_description>"
        prompt += f"<output_structure>{self._load_output_structure()}</output_structure>"
        prompt += "</writer_prompt>"
        response = await self.api.generate_text(prompt)
        return response


if __name__ == "__main__":
    from api.google_api import GoogleAPI
    api = GoogleAPI("google_api.key")
    writer = WriterAgent(api)
    print(asyncio.run(writer.generate_book("A fantasy adventure in a magical kingdom")))
