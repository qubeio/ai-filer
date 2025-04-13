import os
import requests
from loguru import logger
from ai_filer.providers.base_provider import BaseProvider
from ai_filer.providers.ocr import OCR

class OllamaProvider(BaseProvider):
    """Provider for Ollama API."""

    def __init__(self, config):
        """Initialize the Ollama provider with the specified config."""
        super().__init__(config)
        self.ollama_url = 'http://localhost:11434/api/generate'
        self.model = config['model']
        self.ocr = OCR()

    def call_llm(self, prompt: str) -> str:
        """Make a call to the Ollama API."""
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    'model': self.model,
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

    def summarize_document(self, text: str = None, pdf_file: str = None) -> str:
        """Summarize a document's content."""
        # For Ollama, we need to extract text from PDF first
        if pdf_file and not text:
            logger.info("Extracting text from PDF using local OCR")
            text = self.ocr.extract_text_from_pdf(pdf_file)
            if not text:
                raise ValueError("Failed to extract text from PDF")
        
        if text:
            prompt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'prompts', 'summarize_local.txt')
            with open(prompt_path, 'r') as f:
                prompt = f.read()
            prompt = prompt.replace('{{text}}', text)
            return self.call_llm(prompt)
        
        raise ValueError("Either text or pdf_file must be provided")

    def extract_text_from_pdf(self, pdf_file: str) -> str:
        """Extract text from a PDF file."""
        return self.ocr.extract_text_from_pdf(pdf_file) 