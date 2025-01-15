# agents/reviewer/reviewer_agent.py
from api.api import API
from xml.etree import ElementTree
import asyncio

class ReviewerAgent:
    """
    Agent responsible for reviewing and scoring generated content.
    """

    def __init__(self, api: API):
        self.api = api
        self.role_description = self._load_role_description()
        self.review_structure = self._load_review_structure()

    def _load_role_description(self) -> str:
        """
        Loads the role description for this agent from role.xml
        """
        tree = ElementTree.parse("agents/reviewer/role.xml")
        root = tree.getroot()
        description = root.find("description").text
        return description

    def _load_review_structure(self) -> str:
        """
        Loads the review structure for this agent from structure.xml
        """
        prefix = """Output Structure Instructions:
1. The LLM must adhere strictly to the schema provided.
2. The LLM must use the XML format provided.
        """
        with open("agents/reviewer/structure.xml", "r", encoding="utf-8") as xml:
            content = xml.read()  # Read the entire file content
        return prefix + content

    def _load_instructions(self) -> str:
        instructions = "You must review the following book based on the given input."
        return instructions

    async def review_book(self, book, input_prompt):
        """
        Reviews a generated book and provides a score and feedback.

        Args:
            book (str): The generated book text.
            input_prompt (str): The input prompt used for generating the book.

        Returns:
             tuple: (score, feedback) where score is int and feedback is str
        """
        prompt = "<reviewer_prompt>"
        prompt += (
            f"<input_instructions>{self._load_instructions()}</input_instructions>"
        )
        prompt += f"<input_prompt>{input_prompt}</input_prompt>"
        prompt += f"<book>{book}</book>"
        prompt += (
            f"<role_description>{self._load_role_description()}</role_description>"
        )
        prompt += (
            f"<output_structure>{self._load_review_structure()}</output_structure>"
        )
        prompt += "</reviewer_prompt>"
        response = await self.api.generate_text(prompt)
        return response

    def parse_review(self, xml_review):
        """
        Parses the review XML and extracts scores and feedback details.

        Args:
            xml_review (str): The review XML string.

        Returns:
            dict: A dictionary containing the overall score, category scores, and feedback.
        """
        try:
            root = ElementTree.fromstring(xml_review)

            # Extract overall score
            overall_score = int(root.find(".//score/overall").text)

            # Extract category scores
            categories = {}
            for category in root.findall(".//score/categories/category"):
                name = category.get("name")
                score = int(category.get("score"))
                categories[name] = score

            # Extract feedback for each aspect
            feedback = {}
            for aspect in root.findall(".//feedback/aspect"):
                name = aspect.get("name")
                rating = int(aspect.get("rating"))
                comment = aspect.find("comment").text
                feedback[name] = {"rating": rating, "comment": comment}

            return {
                "overall_score": overall_score,
                "categories": categories,
                "feedback": feedback
            }

        except ElementTree.ParseError as e:
            raise ValueError(f"Failed to parse review XML: {e}")
        except Exception as e:
            raise ValueError(f"Error processing review XML: {e}")


if __name__ == "__main__":
    from api.google_api import GoogleAPI
    api = GoogleAPI("google_api.key")
    reviewer = ReviewerAgent(api)
    input_prompt = "A fantasy adventure in a magical kingdom"
    with open("agents/reviewer/input_example.xml", "r") as f:
        book = f.read()
    print(asyncio.run(reviewer.review_book(book, input_prompt)))
