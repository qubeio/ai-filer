import os
from loguru import logger
import shutil
from .types import Config
from PyPDF2 import PdfReader, PdfWriter


class FileManager:
    """Class to handle file operations."""

    def __init__(self, config: Config):
        """Initialize the file object."""
        self.config = config
        self.logger = logger

    def move_file(self, file_path, destination_folder):
        """Move the file to the correct folder.
        Args:
            file_path (str): The path to the file to move.
            destination_folder (str): The folder to move the file to.
        """
        if os.environ.get('TESTING'):
            logger.info(f"Would move {file_path} to {destination_folder}")
            return
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
        shutil.move(file_path, os.path.join(destination_folder, os.path.basename(file_path)))
        logger.info(f"Moved {file_path} to {destination_folder}")

    def get_tree_of_filing_system(self, root_folder: str):
        """
        Get the tree of the filing system recursively, including all subdirectories.
        Returns a comma separated list of quoted directories
        """
        self.logger.debug("Getting tree of filing system")

        def walk_dir(current_dir):
            dirs = []
            for item in os.listdir(current_dir):
                full_path = os.path.join(current_dir, item)
                if os.path.isdir(full_path):
                    # Get relative path from DEST_FOLDER
                    rel_path = os.path.relpath(full_path, root_folder)
                    dirs.append(rel_path)
                    # Recursively get subdirectories
                    dirs.extend(walk_dir(full_path))
            return dirs
        return ','.join([f'"{d}"' for d in walk_dir(root_folder)])

    def rename_and_move_file(self, file_path, new_name, relative_path, extension):
        """Renames a file to a new name and moves it to the correct folder.
        Args:
            file_path (str): The path to the file to rename.
            new_name (str): The new name for the file.
        """
        self.logger.debug(f"Renaming file {os.path.basename(file_path)} to {new_name}.{extension}")
        if os.environ.get('TESTING'):
            self.logger.info(f"Would rename file {os.path.basename(file_path)} to {new_name}.{extension}")
            return
        try:
            # Get the directory of the original file
            original_dir = os.path.dirname(file_path)
            # Create new path in the same directory as the original file
            new_file_path = os.path.join(original_dir, f"{new_name}.{extension}")
            
            os.rename(file_path, new_file_path)
            self.logger.info(f"File renamed {os.path.basename(file_path)} to {new_name}.{extension}")
            # Move the file to the correct folder
            self.move_file(new_file_path, os.path.join(self.config['dest_folder'], relative_path))
            self.logger.info(
                f"File moved {os.path.basename(file_path)} to {os.path.join(self.config['dest_folder'],
                                                                            relative_path)}")
        except Exception as e:
            self.logger.error(
                        "Failed to rename file",
                        file_name=os.path.basename(file_path),
                        error=str(e))
            raise

    def get_all_pdf_files_in_folder(self, folder: str) -> list[str]:
        """Get all pdf files in a folder. Returns a list of full paths."""
        return [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith('.pdf')]

    def add_metadata_to_pdf(self, file_path: str, metadata: dict):
        """Add metadata to PDF file including OCR text.
        Args:
            file_path (str): Path to the PDF file
            metadata (dict): Dictionary of metadata to add
        """
        if os.environ.get('TESTING'):
            self.logger.info(f"Would add metadata to {file_path}: {metadata}")
            return

        try:
            reader = PdfReader(file_path)
            writer = PdfWriter()

            # Copy all pages
            for page in reader.pages:
                writer.add_page(page)

            # Format metadata with proper PDF prefix
            pdf_metadata = {
                f'/{k}': str(v) for k, v in metadata.items()
            }

            # Add metadata
            writer.add_metadata(pdf_metadata)

            # Save the file with metadata
            with open(file_path, 'wb') as output_file:
                writer.write(output_file)
            
            self.logger.info(f"Added metadata to {os.path.basename(file_path)}")
        except Exception as e:
            self.logger.error(
                "Failed to add metadata to PDF",
                file_name=os.path.basename(file_path),
                error=str(e)
            )
            raise
