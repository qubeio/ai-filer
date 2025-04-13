import os
from loguru import logger
from google import genai
from ai_filer.providers.base_provider import BaseProvider

class GeminiProvider(BaseProvider):
    """Provider for Google Gemini API."""

    def __init__(self, config):
        """Initialize the Gemini provider with the specified config."""
        super().__init__(config)
        
        if config.get('use_mac_keyring', True):
            self._initialize_from_keyring()
        else:
            self._initialize_from_env()

    def _get_from_keyring(self, service_name: str, account_name: str) -> str:
        """Get a credential from the Mac keyring."""
        try:
            import keyring
            return keyring.get_password(service_name, account_name)
        except ImportError:
            logger.error("Keyring package not installed. Please install with 'pip install keyring'")
            return None
        except Exception as e:
            logger.error(f"Failed to get credential from keyring: {str(e)}")
            return None

    def _initialize_from_keyring(self):
        """Initialize API client using credentials from Mac keyring."""
        self.api_key = self._get_from_keyring('gemini-api-cred', 'gemini-api-key')
        if not self.api_key:
            raise ValueError("Gemini API key not found in keyring")
        try:
            self.client = genai.Client(api_key=self.api_key)
        except Exception as e:
            raise Exception(f"Failed to create Gemini client: {str(e)}")

    def _initialize_from_env(self):
        """Initialize API client using credentials from environment variables or config."""
        self.api_key = os.environ.get('GEMINI_API_KEY', self.config.get('gemini_api_key'))
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable must be set")
        try:
            self.client = genai.Client(api_key=self.api_key)
        except ImportError:
            raise ImportError("Please install the google-genai package to use Gemini")

    def call_llm(self, prompt: str) -> str:
        """Make a call to the Gemini API."""
        try:
            model = "gemini-2.0-flash"
            response = self.client.models.generate_content(
                model=model,
                contents=[prompt]
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Failed to call Gemini: {str(e)}")
            return None

    def summarize_document(self, text: str = None, pdf_file: str = None) -> str:
        """Summarize a document's content."""
        if pdf_file:
            prompt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'prompts', 'summarize.txt')
            with open(prompt_path, 'r') as f:
                prompt = f.read()
            return self._summarize_with_pdf(prompt, pdf_file)
        
        if text:
            prompt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'prompts', 'summarize_local.txt')
            with open(prompt_path, 'r') as f:
                prompt = f.read()
            prompt = prompt.replace('{{text}}', text)
            return self.call_llm(prompt)
        
        raise ValueError("Either text or pdf_file must be provided")

    def _summarize_with_pdf(self, prompt: str, pdf_file: str) -> str:
        """Summarize a PDF document using Gemini's API."""
        try:
            model = "gemini-2.0-flash"
            staged_pdf = self.client.files.upload(file=pdf_file)
            response = self.client.models.generate_content(
                model=model,
                contents=[prompt, staged_pdf]
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Failed to summarize with Gemini: {str(e)}")
            return None

    def extract_text_from_pdf(self, pdf_file: str) -> str:
        """Extract text from a PDF file using Gemini."""
        try:
            # Load the OCR prompt
            prompt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'prompts', 'perform_ocr.txt')
            with open(prompt_path, 'r') as f:
                prompt = f.read()
            
            logger.info("Extracting text from PDF using Gemini")
            
            model = "gemini-2.0-flash"
            staged_pdf = self.client.files.upload(file=pdf_file)
            response = self.client.models.generate_content(
                model=model,
                contents=[prompt, staged_pdf]
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Failed to extract text with Gemini: {str(e)}")
            return "" 