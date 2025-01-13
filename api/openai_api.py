# api/openai_api.py
import os
import asyncio
import httpx
from api.api import API

class OpenAIAPI(API):
    """
    Concrete class for interactions with the OpenAI API.
    """

    def __init__(self, api_key=None):
        """
        Initializes the OpenAIAPI object.
        """
        super().__init__(api_key)
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables.")

    def _load_api_key_from_env(self):
      """
      Loads the OpenAI API key from environment variables.
      """
      return os.environ.get("OPENAI_API_KEY")

    async def generate_text(self, prompt, model="gpt-3.5-turbo-instruct", max_tokens=2000, temperature=0.7, timeout=10, **kwargs):
        """
        Generates text using the OpenAI API.

        Args:
            prompt (str): The input prompt for text generation.
            model (str): The OpenAI model to use.
            max_tokens (int): The maximum number of tokens for the generated text.
            temperature (float): The sampling temperature.
            timeout (int): Timeout in seconds for the API call.
            **kwargs: Additional keyword arguments for the API call.

        Returns:
            str: The generated text.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
            }
        data = {
                "model": model,
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
        async with httpx.AsyncClient() as client:
          try:
              response = await client.post(
                  "https://api.openai.com/v1/completions", 
                  headers=headers,
                  json=data,
                  timeout=timeout
                  )
              response.raise_for_status()
              return response.json()["choices"][0]["text"].strip()
          except httpx.TimeoutException:
              print("OpenAI API timeout.")
              return ""
          except httpx.HTTPError as e:
              print(f"Error generating text with OpenAI: {e}")
              return ""
          except Exception as e:
             print(f"An unexpected error occurred: {e}")
             return ""