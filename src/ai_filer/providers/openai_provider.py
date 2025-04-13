import os
import time
from loguru import logger
from openai import OpenAI
from ai_filer.providers.base_provider import BaseProvider

class OpenAIProvider(BaseProvider):
    """Provider for OpenAI API."""

    def __init__(self, config):
        """Initialize the OpenAI provider with the specified config."""
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
        self.api_key = self._get_from_keyring('ai_filer', 'openai_api_key')
        if not self.api_key:
            raise ValueError("OpenAI API key not found in keyring")
        self.client = OpenAI(api_key=self.api_key)

    def _initialize_from_env(self):
        """Initialize API client using credentials from environment variables or config."""
        self.api_key = os.environ.get('OPENAI_API_KEY', self.config.get('openai_api_key'))
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable must be set")
        self.client = OpenAI(api_key=self.api_key)

    def call_llm(self, prompt: str) -> str:
        """Make a call to the OpenAI API."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Failed to call OpenAI: {str(e)}")
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

    def _summarize_with_pdf(self, prompt_template: str, pdf_file: str) -> str:
        """Summarize a PDF document using OpenAI's API with file upload capability."""
        try:
            # First, upload the file
            with open(pdf_file, "rb") as file:
                file_upload = self.client.files.create(
                    file=file,
                    purpose="assistants"
                )
            
            # Create a message with the file attachment
            thread = self.client.beta.threads.create()
            
            # Extract the prompt instruction part from the template
            prompt_instruction = prompt_template.split('{{text}}')[0].strip()
            
            # Create a message with the file and instruction
            message = self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=prompt_instruction,
                file_ids=[file_upload.id]
            )
            
            # Run the assistant on the thread
            run = self.client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=self.config.get('openai_assistant_id', 'asst_abc123'),
                instructions="Summarize the PDF document"
            )
            
            # Wait for completion
            while run.status != "completed":
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
                if run.status in ["failed", "cancelled", "expired"]:
                    logger.error(f"OpenAI run failed with status: {run.status}")
                    return None
                time.sleep(1)
            
            # Get the response
            messages = self.client.beta.threads.messages.list(
                thread_id=thread.id
            )
            
            # Return the assistant's response
            for message in messages.data:
                if message.role == "assistant":
                    return message.content[0].text.value
            
            return None
        except Exception as e:
            logger.error(f"Failed to summarize with OpenAI: {str(e)}")
            return None

    def extract_text_from_pdf(self, pdf_file: str) -> str:
        """Extract text from a PDF file using OpenAI."""
        try:
            # Load the OCR prompt
            prompt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'prompts', 'perform_ocr.txt')
            with open(prompt_path, 'r') as f:
                prompt = f.read()
            
            logger.info("Extracting text from PDF using OpenAI")
            
            # Upload the file
            with open(pdf_file, "rb") as file:
                file_upload = self.client.files.create(
                    file=file,
                    purpose="assistants"
                )
            
            # Create a thread
            thread = self.client.beta.threads.create()
            
            # Create a message with the file and instruction
            message = self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=prompt,
                file_ids=[file_upload.id]
            )
            
            # Run the assistant on the thread
            run = self.client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=self.config.get('openai_assistant_id', 'asst_abc123'),
                instructions="Extract all text content from the PDF document"
            )
            
            # Wait for completion
            while run.status != "completed":
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
                if run.status in ["failed", "cancelled", "expired"]:
                    logger.error(f"OpenAI run failed with status: {run.status}")
                    return ""
                time.sleep(1)
            
            # Get the response
            messages = self.client.beta.threads.messages.list(
                thread_id=thread.id
            )
            
            # Return the assistant's response
            for message in messages.data:
                if message.role == "assistant":
                    return message.content[0].text.value
            
            return ""
        except Exception as e:
            logger.error(f"Failed to extract text with OpenAI: {str(e)}")
            return "" 