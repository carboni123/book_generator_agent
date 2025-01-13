# agents/writer/writer_agent.py
from api import API
from xml.etree import ElementTree

class WriterAgent:
    """
    Agent responsible for generating book content.
    """
    def __init__(self, api: API):
      self.api = api
      self.role_description = self._load_role_description()
      self.book_structure = self._load_book_structure()
    
    def _load_role_description(self):
      """
      Loads the role description for this agent from role.xml
      """
      tree = ElementTree.parse("agents/writer/role.xml")
      root = tree.getroot()
      description = root.find("description").text
      return description

    def _load_book_structure(self):
      """
      Loads the book structure for this agent from structure.xml
      """
      tree = ElementTree.parse("agents/writer/structure.xml")
      root = tree.getroot()
      return root

    def generate_book(self, input_prompt):
        """
        Generates a book based on a given input prompt, structured into chapters and sections.

        Args:
            input_prompt (str): The input prompt for the book.

        Returns:
            str: The generated book text.
        """
        book_text = ""
        
        prompt_prefix = f"""
        {self.role_description}
        
        You must write a book based on this prompt: {input_prompt}. 
        The book structure is defined as follows:
        """
        
        chapters = self.book_structure.find("book/chapters")
        
        for chapter in chapters:
            chapter_title = chapter.find("title").text
            book_text += f"\nChapter: {chapter_title}\n"
            
            for section in chapter.find("sections"):
                section_title = section.text
                prompt = f"""{prompt_prefix}
                You are now writing section {section_title} of chapter {chapter_title} following this prompt: {input_prompt}."""
                section_content = self.api.generate_text(prompt)
                book_text += f"\nSection: {section_title}\n{section_content}\n"
                
        return book_text