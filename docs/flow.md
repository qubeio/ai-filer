# AI Filer Program Flow

```mermaid
graph TD
    A[Start] --> B[Load Configuration]
    B --> C[Initialize AI Provider]
    C --> D[Initialize File Manager]
    D --> E[Get PDFs from Watch Folder]
    E --> F[Get Directory Tree]
    
    F --> G[Process PDF Loop]
    G --> H[Extract Text]
    H --> I[Summarize Document]
    I --> J[Classify Document]
    J --> K[Generate Filename]
    
    K --> L{Filename Generated?}
    L -->|Yes| M[Add Metadata]
    M --> N[Move File]
    N --> G
    
    L -->|No| G
    
    G --> O[End]

    subgraph AI Provider Processing
        H --> H1{Provider Type}
        H1 -->|OpenAI| H2[Use OpenAI Vision]
        H1 -->|Gemini| H3[Use Gemini Vision]
        H1 -->|Ollama| H4[Use Locals OCR]
    end

    subgraph Error Handling
        G --> E1[Log Error]
        E1 --> G
    end
```

## Flow Description

1. **Initial Setup**
   - Load configuration from file or environment
   - Initialize appropriate AI provider (OpenAI, Gemini, or Ollama)
   - Set up file management system

2. **Main Processing Loop**
   - Scan watch folder for PDF files
   - Get destination directory structure
   - Process each PDF file

3. **PDF Processing**
   - Extract text using provider-specific method
   - Generate document summary
   - Classify document
   - Generate descriptive filename

4. **File Operations**
   - Add metadata to PDF
   - Move file to classified location

5. **Error Handling**
   - Log errors during processing
   - Continue with next file 