# agents/reviewer/reviewer_agent.py
from api import API
from xml.etree import ElementTree

class ReviewerAgent:
    """
    Agent responsible for reviewing and scoring generated content.
    """
    def __init__(self, api: API):
      self.api = api
      self.role_description = self._load_role_description()
      self.review_structure = self._load_review_structure()
    
    def _load_role_description(self):
      """
      Loads the role description for this agent from role.xml
      """
      tree = ElementTree.parse("agents/reviewer/role.xml")
      root = tree.getroot()
      description = root.find("description").text
      return description

    def _load_review_structure(self):
      """
      Loads the review structure for this agent from structure.xml
      """
      tree = ElementTree.parse("agents/reviewer/structure.xml")
      root = tree.getroot()
      return root

    def review_book(self, book, input_prompt):
        """
        Reviews a generated book and provides a score and feedback.

        Args:
            book (str): The generated book text.
            input_prompt (str): The input prompt used for generating the book.

        Returns:
             tuple: (score, feedback) where score is int and feedback is str
        """
        prompt = f"""
        {self.role_description}

        You must review the following book based on the given input:

        Input: {input_prompt}

        Book:
        {book}

        Provide a score between 0 and 10 and detailed feedback based on:
        {', '.join([aspect.text for aspect in self.review_structure.find('feedback')])}

        Output in the following format:
        Score: <score>
        Feedback: <feedback>
        """
        response = self.api.generate_text(prompt)

        try:
          score_start = response.find("Score:") + len("Score:")
          score_end = response.find("Feedback:")
          score = int(response[score_start:score_end].strip())
          feedback = response[score_end + len("Feedback:"):].strip()
          return score, feedback
        except Exception as e:
           print(f"Error parsing review output: {e}")
           return 0, "Could not process review."