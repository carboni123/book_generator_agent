# api/deepseek_api.py
import os
import asyncio
from api.api import API
from openai import OpenAI


class DeepSeekAPI(API):
    """
    Concrete class for interactions with the DeepSeek API.
    """

    def __init__(self, api_key=None):
        """
        Initializes the OpenAI (DeepSeek) API object.

        :param api_key: Can be either an actual API key string or
                        a path to a file containing the API key.
        """
        super().__init__(api_key)
        self.client = None
        self.api_url = "https://api.deepseek.com"

        # 1. If an api_key is provided and it's a file path, load from file.
        if api_key and os.path.isfile(api_key):
            self.api_key = self._load_api_key_from_file(api_key)
            self.client = OpenAI(api_key=self.api_key, base_url=self.api_url)
        # 2. If an api_key is provided but not a file path, assume it's the key itself.
        elif api_key:
            self.api_key = api_key
            self.client = OpenAI(api_key=self.api_key, base_url=self.api_url)

        # 3. If no api_key passed in or file loading failed, attempt to load from the environment.
        if not self.api_key:
            self.api_key = self._load_api_key_from_env()
            self.client = OpenAI(api_key=self.api_key, base_url=self.api_url)

        # 4. If we still don’t have a key or a client, raise an error.
        if not self.api_key or not self.client:
            raise ValueError(
                "No valid DeepSeek API key found. Provide it as a string, file path, "
                "or set DEEPSEEK_API_KEY in the environment."
            )

    def _load_api_key_from_file(self, key_path: str) -> str:
        """
        Loads the DeepSeek API key from a file.

        :param key_path: Path to the file containing the API key.
        :return: The API key as a string.
        :raises ValueError: If the key file cannot be read or is not found.
        """
        try:
            with open(key_path, "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            raise ValueError(
                f"API key file '{key_path}' not found. Please create this file with your API key."
            )
        except Exception as e:
            raise ValueError(f"Error reading API key file: {e}")

    def _load_api_key_from_env(self) -> str:
        """
        Loads the DeepSeek API key from environment variables.

        :return: The API key as a string.
        :raises ValueError: If the API key is not found in the environment variables.
        """
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY not found in environment variables.")
        return api_key

    async def generate_text(
        self,
        prompt,
        model="deepseek-chat",
        max_tokens=8192,
        temperature=1.0,
        timeout=10,
        **kwargs,
    ):
        """
        Generates text using the DeepSeek API.

        Args:
            prompt (str): The input prompt for text generation.
            model (str): The DeepSeek model to use.
            max_tokens (int): The maximum number of tokens for the generated text.
            temperature (float): The sampling temperature.
            timeout (int): Timeout in seconds for the API call.
            **kwargs: Additional keyword arguments for the API call.

        Returns:
            str: The generated text, or None if an error occurred.
        """
        # Convert a plain string prompt into a "system" message.
        # If `prompt` is a list, assume it's already in the correct chat format.
        if isinstance(prompt, str):
            messages = [{"role": "system", "content": prompt}]
        else:
            if not isinstance(prompt, list):
                raise TypeError(
                    "Prompt must be either a string or a list of messages (JSON)."
                )
            messages = prompt

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=False,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs,
            )
            generated_text = response.choices[0].message.content
            return generated_text
        except Exception as e:
            print(f"An error occurred while generating text: {e}")
            return None

    def test_api(self):
        """
        A simple test method to verify the API setup by making a single request.
        """
        prompt = "You are a helpful assistant. What is the capital of France?"
        result = asyncio.run(self.generate_text(prompt))
        print("Test API result:", result)


if __name__ == "__main__":
    # Example: Supply a path to a file containing your key,
    # or just ensure DEEPSEEK_API_KEY is set in your environment.
    api = DeepSeekAPI("deepseek_api.key")
    api.test_api()
