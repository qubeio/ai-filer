import os
import requests
from loguru import logger
from .types import Config
from openai import OpenAI


class AI:
    """Class to handle all AI/LLM interactions."""

    def __init__(self, config: Config):
        """Initialize the AI with the specified model."""
        self.config = config
        self.ollama_url = 'http://localhost:11434/api/generate'

        if self.config['model'] == 'openai':
            self.openai_key = os.environ.get('OPENAI_API_KEY', self.config['openai_api_key'])
            if not self.openai_key:
                raise ValueError("OPENAI_API_KEY environment variable must be set")
            self.openai_client = OpenAI(api_key=self.openai_key)

    def _call_llm(self, prompt: str) -> str:
        """Make a call to the appropriate LLM API."""
        if self.config['model'] == 'openai':
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                logger.error(f"Failed to call OpenAI: {str(e)}")
                return None
        else:
            try:
                response = requests.post(
                    self.ollama_url,
                    json={
                        'model': self.config['model'],
                        'prompt': prompt,
                        'stream': False
                    })

                if response.status_code != 200:
                    logger.error(f"Error calling Ollama: {response.text}")
                    return None

                return response.json()['response'].strip()

            except Exception as e:
                logger.error(f"Failed to call Ollama: {str(e)}")
                return None

    def summarize_document(self, text: str) -> str:
        """Summarize a document's content."""
        prompt_path = os.path.join(os.path.dirname(__file__), 'prompts', 'summarize.txt')
        with open(prompt_path, 'r') as f:
            prompt_template = f.read()

        prompt = prompt_template.replace('{{text}}', text)
        return self._call_llm(prompt)

    def classify_document(self, summary: str, tree: list[str]) -> str:
        """Classify a document based on its summary."""
        prompt_path = os.path.join(os.path.dirname(__file__), 'prompts', 'classify.txt')
        with open(prompt_path, 'r') as f:
            prompt_template = f.read()

        # Apply both replacements to the template
        prompt = prompt_template.replace('{{directories}}', tree)
        prompt = prompt.replace('{{summary}}', summary)

        category = self._call_llm(prompt)

        # Validate the category is in our tree or is "Unsorted"
        if category not in tree and category != "Unsorted":
            logger.warning(f"LLM returned invalid category '{category}', using 'Unsorted'")
            return "Unsorted"

        return category

    def generate_filename(self, text: str) -> str:
        """Generate a descriptive filename for a document."""
        prompt_path = os.path.join(os.path.dirname(__file__), 'prompts', 'describe.txt')
        with open(prompt_path, 'r') as f:
            prompt_template = f.read()

        prompt = prompt_template.replace('{{text}}', text)
        filename = self._call_llm(prompt)

        if filename and len(filename) > 100:
            logger.warning(f"Generated filename too long, truncating: {filename}")
            filename = filename[:50]

        if filename:
            # Remove any potentially problematic characters while preserving spaces
            filename = ''.join(c for c in filename if c.isalnum() or c in '- ')

        return filename
