# api/api.py
from abc import ABC, abstractmethod

class API(ABC):
    """
    Abstract base class for API interactions.
    """
    def __init__(self, api_key=None):
        """
        Initializes the API object.

        Args:
            api_key (str, optional): The API key for the service.
                                     If not provided, it tries to load it from an environment variable.
        """
        if not api_key:
            api_key = self._load_api_key_from_env()
        self.api_key = api_key

    @abstractmethod
    def _load_api_key_from_env(self):
      """
      Abstract method to load api key from system environments.
      """
      pass

    @abstractmethod
    async def generate_text(self, prompt, **kwargs):
        """
        Abstract method to generate text from a given prompt.

        Args:
            prompt (str): The input prompt for text generation.
            **kwargs: Additional keyword arguments for the API call.

        Returns:
            str: The generated text.
        """
        pass