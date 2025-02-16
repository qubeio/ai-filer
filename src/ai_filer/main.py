import os
import sys
import configparser

from datetime import datetime
from loguru import logger
from .ai import AI
from .ocr import OCR
from .file_manager import FileManager
from .types import Config


def setup_logger():
    """Setup loguru logger for console output."""

    # If DEBUG is set, set the log level to DEBUG
    if os.environ.get('DEBUG'):
        loggerLevel = "DEBUG"
    else:
        loggerLevel = "INFO"

    logger.remove()

    # Add console handler with a more readable format
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <level>{message}</level>",
        level=loggerLevel)


def setup_file_logger(watch_folder: str):
    """Setup loguru logger with json output to file.
    Args:
        watch_folder (str): The folder to watch for new files.
    """

    # If DEBUG is set, set the log level to DEBUG
    if os.environ.get('DEBUG'):
        loggerLevel = "DEBUG"
    else:
        loggerLevel = "INFO"

    logs_dir = os.path.join(watch_folder, 'logs')
    os.makedirs(logs_dir, exist_ok=True)

    log_file = os.path.join(logs_dir, f"processing_log_{datetime.now().strftime('%Y-%m')}.json")

    # Add file handler with json format
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} {level} {message}",
        level=loggerLevel,
        serialize=True
    )


def get_config_from_file_or_env() -> Config:
    """Get the config from the config file using configparser
    or environment variables.
    """
    config: Config = {
        'watch_folder': '',
        'dest_folder': '',
        'model': 'llama3.2',  # default model
        'debug': False,
        'testing': False,
        'openai_api_key': ''
    }

    # Try to read from config file first
    config_file = os.path.expanduser('~/.config/aifiler')
    if os.path.exists(config_file):
        parser = configparser.ConfigParser(allow_unnamed_section=True)
        parser.read(config_file)
        config.update({
            'watch_folder': parser.get(configparser.UNNAMED_SECTION, 'watch_folder', fallback=''),
            'dest_folder': parser.get(configparser.UNNAMED_SECTION, 'dest_folder', fallback=''),
            'model': parser.get(configparser.UNNAMED_SECTION, 'model', fallback='llama3.2'),
            'debug': parser.getboolean(configparser.UNNAMED_SECTION, 'debug', fallback=False),
            'testing': parser.getboolean(configparser.UNNAMED_SECTION, 'testing', fallback=False),
            'openai_api_key': parser.get(configparser.UNNAMED_SECTION, 'openai_api_key', fallback='')
        })

    # Environment variables override config file
    config.update({
        'watch_folder': os.environ.get('WATCH_FOLDER', config['watch_folder']),
        'dest_folder': os.environ.get('DEST_FOLDER', config['dest_folder']),
        'model': os.environ.get('MODEL', config['model']),
        'debug': os.environ.get('DEBUG', config['debug']) in ('1', 'true', 'True'),
        'testing': os.environ.get('TESTING', config['testing']) in ('1', 'true', 'True'),
        'openai_api_key': os.environ.get('OPENAI_API_KEY', config['openai_api_key'])
    })
    logger.debug(f"Config: watch_folder={config['watch_folder']}, dest_folder={config['dest_folder']}")
    logger.debug(f"Config: model={config['model']}, debug={config['debug']}, testing={config['testing']}")
    # Validate required fields
    if not config['watch_folder'] or not config['dest_folder']:
        raise ValueError("watch_folder and dest_folder must be set in config file or environment")

    return config


def main():
    """Main function to run the AI filing system."""

    setup_logger()
    config = get_config_from_file_or_env()
    setup_file_logger(config['watch_folder'])
    logger.info("Starting AI Filing System...")

    # Initialize AI
    ai = AI(config)

    # Initialize OCR
    ocr = OCR(config)

    # Initialize FileManager
    file_manager = FileManager(config)

    try:
        pdf_files = file_manager.get_all_pdf_files_in_folder(config['watch_folder'])
        tree = file_manager.get_tree_of_filing_system(config['dest_folder'])

        for pdf_file in pdf_files:
            try:
                # Extract text
                logger.info(f"Processing OCR for {os.path.basename(pdf_file)}")
                text = ocr.perform_ocr_on_pdf(pdf_file)

                # Get summary
                summary = ai.summarize_document(text)
                logger.info(f"Summary completed: {summary}")

                # Classify
                directory = ai.classify_document(summary, tree)
                logger.info(f"Classification completed: {directory}")

                # Generate filename
                filename = ai.generate_filename(text)
                if filename:
                    logger.info(f"Generated filename: {filename}")
                    # Add OCR text and metadata before moving
                    file_manager.add_metadata_to_pdf(
                        pdf_file,
                        {
                            'OCRText': text,
                            'Summary': summary,
                            'Category': directory,
                            'ProcessedDate': datetime.now().isoformat(),
                            'Keywords': summary[:100]  # First 100 chars of summary as keywords
                        }
                    )
                    file_manager.rename_and_move_file(pdf_file, filename, directory, 'pdf')

            except Exception as e:
                logger.error(f"Failed to process {pdf_file}: {str(e)}")
                continue

    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
