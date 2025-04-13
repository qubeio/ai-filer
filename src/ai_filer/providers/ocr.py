from loguru import logger

class OCR:
    """Class to handle OCR (Optical Character Recognition) operations."""
    
    @staticmethod
    def extract_text_from_pdf(pdf_file: str) -> str:
        """Extract text from a PDF file using local OCR tools.
        
        Args:
            pdf_file (str): Path to the PDF file.
            
        Returns:
            str: The extracted text from the PDF.
        """
        try:
            # Use PyPDF2 for basic text extraction
            import PyPDF2
            
            text_content = ""
            with open(pdf_file, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                # Extract text from each page
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text_content += page.extract_text() + "\n\n"
            
            # If we got meaningful text, return it
            if text_content.strip() and len(text_content.strip()) > 100:
                return text_content
            
            # If PyPDF2 didn't extract enough text, try with Tesseract if available
            try:
                import pytesseract
                from pdf2image import convert_from_path
                
                logger.info("Basic text extraction yielded insufficient results, using Tesseract OCR")
                
                # Convert PDF to images
                images = convert_from_path(pdf_file)
                
                # Extract text from each image
                ocr_text = ""
                for i, image in enumerate(images):
                    page_text = pytesseract.image_to_string(image)
                    ocr_text += f"Page {i+1}:\n{page_text}\n\n"
                
                # If we got meaningful text from Tesseract, return it
                if ocr_text.strip() and len(ocr_text.strip()) > 100:
                    return ocr_text
            except ImportError:
                logger.warning("Tesseract OCR not available. Install with 'pip install pytesseract pdf2image'")
            except Exception as e:
                logger.error(f"Failed to use Tesseract OCR: {str(e)}")
            
            # If we still don't have text, return what we got from PyPDF2
            return text_content
        
        except ImportError:
            logger.error("PyPDF2 not installed. Please install with 'pip install PyPDF2'")
            return ""
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {str(e)}")
            return ""
