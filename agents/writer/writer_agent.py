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
        self.book_draft = False

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
        if not self.book_draft:
            self.book_draft = True
            return (
                "Write a book with approximately 500 words per chapter. "
                "Ensure the book contains at least 4 chapters and follows a clear narrative structure with a distinct beginning, middle, and end. "
                "The beginning should introduce the setting, characters, and conflict. "
                "The middle should develop the story, building tension and deepening the conflict. "
                "The end should resolve the conflict and provide a satisfying conclusion, even if it leaves room for a sequel."
            )
        return "Refine the book based on the feedback provided by the Reviewer, focusing on clarity, coherence, and depth."

    async def generate_book(self, input, previous_books=None, previous_reviews=None):
        """
        Generates a book based on a given input prompt, structured into chapters and sections.

        Args:
            input (str): The input prompt for the book.
            previous_books (list, optional): A list of the previous book content for refinement. Defaults to None.
            previous_reviews (list, optional): A list of the previous review feedback for improvement. Defaults to None.

        Returns:
            str: The generated book in XML format.
        """
        logging.info(f"Generating book with prompt: {input}")
        # Create the root element
        prompt = "<writer_prompt>"
        # Add subelements
        prompt += f"<input_instructions>{self._load_instructions()}</input_instructions>"
        prompt += f"<theme>{input}</theme>"
        prompt += f"<role_description>{self._load_role_description()}</role_description>"
        prompt += f"<output_structure>{self._load_output_structure()}</output_structure>"
        if previous_books and previous_reviews:
            for i, (book, review) in enumerate(zip(previous_books, previous_reviews)):
                if i == 0:
                    prompt += f"<best_book>"
                else:
                    prompt += f"<last_book>"
                prompt += f"<book_content>{book}</book_content>"
                prompt += f"<review_content>{review}</review_content>"
                if i == 0:
                    prompt += f"</best_book>"
                else:
                    prompt += f"<last_book>"
        prompt += "</writer_prompt>"

        # Log the prompt to a file
        with open("writer_sent_prompts.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"Prompt Sent:\n{prompt}\n\n")

        response = await self.api.generate_text(prompt)
        return response


if __name__ == "__main__":
    from api.google_api import GoogleAPI
    api = GoogleAPI("google_api.key")
    writer = WriterAgent(api)
    print(asyncio.run(writer.generate_book("A fantasy adventure in a magical kingdom")))
