# AI Filer - Product Requirements Document

## Overview

AI Filer is a native macOS application that automatically processes, classifies, and organizes PDF documents using AI. It transforms the existing Python CLI tool into a user-friendly SwiftUI app with real-time file monitoring and native macOS integration.

## Target Platform

- **Platform**: macOS 13.0+
- **Framework**: SwiftUI with native macOS frameworks
- **Development**: VSCode with Swift Package Manager (no Xcode dependency)
- **Distribution**: Personal use, simple installer/DMG

## Core Functionality

### Document Processing Pipeline

1. **Monitor**: Watch folder for new PDF files using FSEvents
2. **Extract**: Text extraction via PDFKit + Vision framework OCR fallback
3. **Summarize**: AI-generated document summaries
4. **Classify**: AI-powered category assignment based on folder structure
5. **Generate**: Descriptive filename creation
6. **Organize**: File movement with metadata embedding

### AI Provider System

- **OpenAI**: GPT-4o-mini for cloud processing
- **Google Gemini**: Alternative cloud provider
- **Ollama**: Local LLM support for privacy
- **Protocol-based**: Extensible provider architecture

## Architecture

### Core Services

```
Sources/
├── Models/           # Data structures (Config, Document, ProcessingResult)
├── Services/         # Business logic services
│   ├── ConfigurationManager      # Settings & keychain integration
│   ├── AIProvider               # Protocol + concrete implementations
│   ├── FileManagerService       # File operations
│   ├── PDFProcessingService     # PDFKit integration
│   ├── DocumentProcessor        # Main workflow orchestration
│   └── FileWatcherService       # FSEvents monitoring
├── Views/            # SwiftUI interface components
└── Utilities/        # Helpers and extensions
```

### Key Data Models

```swift
struct Config: Codable {
    var watchFolder: URL
    var destFolder: URL
    var aiProvider: AIProviderType
    var apiKey: String
    var debugMode: Bool
    var testingMode: Bool
}

struct Document {
    let path: URL
    var summary: String?
    var category: String?
    var suggestedFilename: String?
    var metadata: [String: Any]
}
```

## User Interface

### Main Window

- **Sidebar Navigation**: Settings, Processing, History
- **Central Panel**: Current processing status and document queue
- **Folder Selection**: Watch and destination folder pickers
- **Processing Controls**: Start/stop monitoring, manual processing
- **Status Display**: Real-time progress and logs

### Settings Window

- **AI Provider Tab**: Model selection, API key management
- **Folders Tab**: Path configuration with validation
- **Processing Tab**: Debug mode, testing mode, advanced options
- **Import/Export**: Configuration backup and restore

### Processing Display

- **Progress Tracking**: Individual document progress bars
- **Live Logs**: Filterable processing logs with timestamps
- **Error Handling**: User-friendly error messages and recovery options
- **Statistics**: Processing metrics and performance data

## Technical Requirements

### Native Integration

- **Menu Bar**: Standard macOS menus with keyboard shortcuts
- **File Operations**: Native file handling with conflict resolution
- **Security**: Keychain integration for API key storage
- **Monitoring**: FSEvents for efficient file system watching
- **Sandboxing**: App Store compatibility (if needed)

### Error Handling

- **Network Resilience**: Retry logic for API failures
- **File System**: Robust handling of locked/missing files
- **User Feedback**: Clear error messages with recovery suggestions
- **Logging**: Structured logging with rotation and filtering

### Performance

- **Async Processing**: Non-blocking UI with concurrent document processing
- **Resource Management**: Efficient memory usage for large documents
- **Background Processing**: Continued operation when window is closed
- **Batch Operations**: Queue management for multiple documents

## Development Environment

### Toolchain

- **Language**: Swift 5.9+
- **Package Manager**: Swift Package Manager
- **IDE**: VSCode with Swift extension
- **Build System**: Native Swift build tools
- **Testing**: XCTest framework with UI tests

### Project Structure

```
Package.swift           # Dependencies and build configuration
Sources/               # Main application code
Tests/                 # Unit and integration tests
Resources/             # Prompt templates and assets
.vscode/               # VSCode configuration
```

### Dependencies

- **PDFKit**: Native PDF processing
- **Vision**: OCR capabilities
- **Network**: HTTP client for AI APIs
- **SwiftUI**: User interface framework
- **Combine**: Reactive programming

## Success Criteria

### Functional Requirements

- [ ] Processes PDF documents with 95%+ success rate
- [ ] Supports all three AI providers (OpenAI, Gemini, Ollama)
- [ ] Real-time file monitoring with <5 second detection
- [ ] Native macOS UI with proper menu integration
- [ ] Comprehensive error handling and recovery

### Quality Requirements

- [ ] Startup time under 3 seconds
- [ ] Processing time under 30 seconds per document
- [ ] Memory usage under 200MB during idle
- [ ] 90%+ test coverage for core services
- [ ] Zero data loss during processing failures

### User Experience

- [ ] Intuitive setup process under 5 minutes
- [ ] Clear visual feedback for all operations
- [ ] Accessible keyboard shortcuts for power users
- [ ] Comprehensive help documentation
- [ ] Reliable configuration persistence

## Migration Strategy

The Swift app will maintain full compatibility with the existing Python implementation's:

- Configuration file format
- Folder structure expectations
- Prompt templates
- AI provider interfaces
- Processing workflow

This ensures users can seamlessly transition from the CLI tool to the native app while preserving their existing filing systems and configurations.
