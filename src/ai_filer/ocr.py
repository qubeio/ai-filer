import os
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from loguru import logger
from .types import Config


class OCR:
    """Class to handle OCR operations."""

    def __init__(self, config: Config):
        """Initialize the OCR class."""
        self.logger = logger
        self.config = config

    def extract_text_from_image(self, file_path):
        """Perform OCR on an image and return extracted text."""
        return pytesseract.image_to_string(Image.open(file_path))

    def perform_ocr_on_pdf(self, file_path: str) -> str:
        """Perform OCR on a pdf file and return extracted text.
        Converts each page of the PDF to an image and performs OCR using pytesseract.
        Returns the concatenated text from all pages.
        """
        if os.environ.get('USE_CACHED_OCR'):
            logger.info("Using cached OCR")
            if not os.path.exists(f'ocr_output_{os.path.basename(file_path)}.txt'):
                logger.warning("No cached OCR found, performing OCR")
            else:
                return open(f'ocr_output_{os.path.basename(file_path)}.txt', 'r').read()

        # Convert PDF to list of PIL Image objects
        images = convert_from_path(file_path)

        # Perform OCR on each page
        text_content = []
        for _, image in enumerate(images, start=1):
            text = pytesseract.image_to_string(image)
            text_content.append(text)

        # Combine all pages with double newlines between them
        combined_text = '\n\n'.join(text_content)

        # If we are using cached OCR, write the text to a file for debugging purposes
        if os.environ.get('USE_CACHED_OCR'):
            with open(f'ocr_output_{os.path.basename(file_path)}.txt', 'w') as f:
                f.write(combined_text)

        return combined_text
