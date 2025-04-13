import os
from abc import ABC, abstractmethod
from loguru import logger

class BaseProvider(ABC):
    """Base class for AI providers."""

    def __init__(self, config):
        """Initialize the provider with the specified config."""
        self.config = config

    @abstractmethod
    def call_llm(self, prompt: str) -> str:
        """Make a call to the LLM API."""
        pass

    @abstractmethod
    def summarize_document(self, text: str = None, pdf_file: str = None) -> str:
        """Summarize a document's content."""
        pass

    @abstractmethod
    def extract_text_from_pdf(self, pdf_file: str) -> str:
        """Extract text from a PDF file."""
        pass

    def classify_document(self, summary: str, tree: list[str]) -> str:
        """Classify a document based on its summary."""
        prompt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'prompts', 'classify.txt')
        with open(prompt_path, 'r') as f:
            prompt_template = f.read()

        # Apply both replacements to the template
        prompt = prompt_template.replace('{{directories}}', tree)
        prompt = prompt.replace('{{summary}}', summary)

        category = self.call_llm(prompt)

        # Validate the category is in our tree or is "Unsorted"
        if category not in tree and category != "Unsorted":
            logger.warning(f"LLM returned invalid category '{category}', using 'Unsorted'")
            return "Unsorted"

        return category

    def generate_filename(self, text: str) -> str:
        """Generate a descriptive filename for a document."""
        prompt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'prompts', 'describe.txt')
        with open(prompt_path, 'r') as f:
            prompt_template = f.read()

        prompt = prompt_template.replace('{{text}}', text)
        filename = self.call_llm(prompt)

        if filename and len(filename) > 100:
            logger.warning(f"Generated filename too long, truncating: {filename}")
            filename = filename[:50]

        if filename:
            # Remove any potentially problematic characters while preserving spaces
            filename = ''.join(c for c in filename if c.isalnum() or c in '- ')

        return filename 