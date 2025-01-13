# api/google_api.py
import os
from api.api import API
import google.generativeai as genai


class GoogleAPI(API):
    """
    Concrete class for interactions with the Google API.
    """

    MODEL_NAME = "models/gemini-2.0-flash-thinking-exp"

    def __init__(self, api_key=None):
        """
        Initializes the GoogleAPI object.

        :param api_key: Can be either an actual API key string or a path to a file containing the API key.
        """
        super().__init__(api_key)

        # Check if api_key is a file path
        if api_key and os.path.exists(api_key):
            self.api_key = self._load_api_key_from_file(api_key)
        elif api_key:
            # If api_key is provided but not a file path, assume it's the key itself
            self.api_key = api_key
            genai.configure(
                api_key=api_key
            )  # Configure genai if the key is directly provided

        # If api_key is not set or loading from file failed, attempt to load from environment
        if not self.api_key:
            self.api_key = self._load_api_key_from_env()

        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables.")

    def _load_api_key_from_file(self, key_path: str) -> str:
        """
        Loads the Google API key from a file.

        :param key_path: Path to the file containing the API key.
        :return: The API key as a string.
        :raises ValueError: If the key file cannot be read or is not found.
        """
        try:
            with open(key_path, "r") as f:
                api_key = f.read().strip()
                genai.configure(api_key=api_key)
                return api_key
        except FileNotFoundError:
            raise ValueError(
                f"API key file '{key_path}' not found. Please create this file with your API key."
            )
        except Exception as e:
            raise ValueError(f"Error reading API key file: {e}")

    def _load_api_key_from_env(self) -> str:
        """
        Loads the Google API key from environment variables.

        :return: The API key as a string.
        :raises ValueError: If the API key is not found in the environment variables or configuration fails.
        """
        api_key = os.environ.get("GOOGLE_API_KEY")
        if api_key:
            try:
                genai.configure(api_key=api_key)
                return api_key
            except Exception as e:
                raise ValueError(f"Error configuring Google API: {e}")
        else:
            raise ValueError("API key not found in environment variables.")

    async def generate_text(self, prompt, timeout=10, **kwargs):
        """
        Generates text using the Google API.

        Args:
            prompt (str): The input prompt for text generation.
            timeout (int): Timeout in seconds for the API call.
            **kwargs: Additional keyword arguments for the API call.

        Returns:
            str: The generated text.

        Raises:
             NotImplementedError: This method is not yet implemented for Google API.
        """
        model = genai.GenerativeModel(self.MODEL_NAME)
        try:
            response = model.generate_content(prompt)
        except Exception as e:
            self.log_output({"error": str(e)}, self.LOG_FILE)
            print(f"Error generating text with Google API: {e}")
            raise

    def list_models(self):
        print("List of models that support generateContent:\n")
        for m in genai.list_models():
            if "generateContent" in m.supported_generation_methods:
                print(m.name)

    def get_model_info(self, model: str):
        model_info = genai.get_model(model)
        print(model_info)


if __name__ == "__main__":
    api = GoogleAPI("google_api.key")
    api.list_models()
