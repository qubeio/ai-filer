from ai_filer.types import Config
from ai_filer.providers.openai_provider import OpenAIProvider
from ai_filer.providers.gemini_provider import GeminiProvider
from ai_filer.providers.ollama_provider import OllamaProvider

class AI:
    """Class to handle all AI/LLM interactions."""

    def __init__(self, config: Config):
        """Initialize the AI with the specified model."""
        self.config = config

        # Initialize the appropriate provider
        if self.config['model'] == 'openai':
            self.provider = OpenAIProvider(config)
        elif self.config['model'] == 'gemini':
            self.provider = GeminiProvider(config)
        else:
            # Assume it's an Ollama model
            self.provider = OllamaProvider(config)

    def summarize_document(self, text: str = None, pdf_file: str = None) -> str:
        """Summarize a document's content."""
        return self.provider.summarize_document(text=text, pdf_file=pdf_file)

    def extract_text_from_pdf(self, pdf_file: str) -> str:
        """Extract text from a PDF file."""
        return self.provider.extract_text_from_pdf(pdf_file)

    def classify_document(self, summary: str, tree: list[str]) -> str:
        """Classify a document based on its summary."""
        return self.provider.classify_document(summary, tree)

    def generate_filename(self, text: str) -> str:
        """Generate a descriptive filename for a document."""
        return self.provider.generate_filename(text)
