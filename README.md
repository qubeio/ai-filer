# AI Filing System

An intelligent document filing system that automatically categorizes and organizes
your PDF documents using AI. It can process scanned documents using OCR and then
use AI to determine the appropriate filing location.

It can use local llms via Ollama or remote llms via OpenAI.

Great for just using your phone camera to scan documents to a cloud folder
and then have it automatically filed away by AI.

## Features

- 🤖 AI-powered document classification
- 📄 OCR for scanned documents
- 📁 Automatic file organization
- 📝 Smart filename generation
- 📋 Document summarization
- 🔄 Support for both local (Ollama) and cloud (OpenAI) AI models

## Prerequisites

- Python 3.13 or higher
- Tesseract OCR
- Ollama (optional, for local AI)
- OpenAI API key (optional, for GPT models)

## Installation

1. Install Tesseract OCR:

   ```bash
   brew install tesseract
   ```

2. Install Ollama (optional, for local AI):

   ```bash
   curl https://ollama.ai/install.sh | sh
   ```

3. Create and activate a virtual environment using uv:

   ```bash
   pip install uv
   uv venv
   source .venv/bin/activate
   ```

4. Install dependencies:

   ```bash
   uv pip install -e .
   ```

## Configuration

Create a configuration file at `~/.config/aifiler` with your settings:

   ```ini
   watch_folder = /path/to/incoming/documents
   dest_folder = /path/to/filing/system
   model = llama3.1:8b  # or 'openai' for GPT models
   openai_api_key = your-api-key # only if using OpenAI
   debug = false
   ```

Any of the settings can be overridden/set by environment variables.

## Usage

Run the script manually:

   ```bash
   python -m ai_filer
   ```

### Setting up as a Cron Job (MacOS)

1. Create a shell script to run the filing system (e.g., `run_filer.sh`):

   ```bash
   #!/bin/bash
   export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

   # If using homebrew's poppler
   if [ -d "/opt/homebrew" ]; then
      export PATH="/opt/homebrew/bin:$PATH"
   fi

   cd /path/to/ai_filer
   source .venv/bin/activate
   python -m ai_filer
   ```

2. Make the script executable:

   ```bash
   chmod +x run_filer.sh
   ```

3. Open your crontab:

   ```bash
   crontab -e
   ```

4. Add a cron job to run every day at 12:00:

   ```bash
   0 12 * * * /path/to/run_filer.sh >> /path/to/logFile.log 2>&1
   ```

## File Organization

The system organizes files into categories like:

- Tax/Council Tax
- Bills/Utilities
- Medical
- Insurance
- etc.

Files that can't be categorized are moved to an "Unsorted" directory for manual review.

## Logging

Logs are written to the `logs` subdirectory of your watch folder in a structured format. You can monitor the filing system's activity with:

```bash
tail -f /path/to/watch_folder/logs/processing_log_YYYY-MM.log
```

## Troubleshooting

- Ensure Tesseract is properly installed and in your PATH
- Check the logs for detailed error messages
- Verify file permissions on watch and destination folders
- If using Ollama, ensure the service is running
- For OpenAI, verify your API key is correctly set
