# BNI PALMS Analysis - Architecture Guide

## Overview

This application follows **Clean Architecture** principles, providing a maintainable, testable, and scalable codebase for BNI PALMS data analysis. The architecture separates concerns into distinct layers, making it easy to add new features, modify existing functionality, and maintain the codebase.

## Architecture Layers

```
src/
├── domain/           # Business logic and entities (innermost layer)
├── application/      # Use cases and application services 
├── infrastructure/   # External dependencies and frameworks
├── presentation/     # User interfaces (CLI, Streamlit)
└── shared/          # Common utilities and constants
```

## Layer Details

### 🎯 Domain Layer (`src/domain/`)

**Purpose**: Contains the core business logic and domain entities. This layer is independent of all external frameworks and libraries.

```
domain/
├── models/          # Domain entities (Member, Referral, OneToOne, etc.)
├── services/        # Domain services (AnalysisService, MatrixService, etc.)
└── exceptions/      # Custom domain exceptions
```

**Key Components**:
- **Models**: Core business entities that represent the problem domain
- **Services**: Business logic that doesn't belong to a specific entity
- **Exceptions**: Domain-specific error handling

**Adding New Features**: 
- Add new domain models in `models/` for new business entities
- Create domain services in `services/` for complex business operations
- Define custom exceptions in `exceptions/` for domain-specific errors

### 🔧 Application Layer (`src/application/`)

**Purpose**: Orchestrates the domain layer to fulfill specific use cases. Contains application-specific business rules.

```
application/
├── use_cases/       # Application use cases (GenerateReports, CompareMatrices, etc.)
└── dto/            # Data Transfer Objects for input/output
```

**Key Components**:
- **Use Cases**: High-level application operations that coordinate domain services
- **DTOs**: Data structures for transferring data between layers

**Adding New Features**:
- Create new use cases in `use_cases/` for new application workflows
- Add DTOs in `dto/` for new request/response structures
- Use cases should orchestrate domain services, not contain business logic

### 🏗️ Infrastructure Layer (`src/infrastructure/`)

**Purpose**: Implements interfaces defined by the domain and application layers. Handles external dependencies.

```
infrastructure/
├── config/          # Application configuration and settings
├── data/           # Data access and file handling
│   ├── file_handlers/  # Excel and file conversion utilities
│   └── repositories/   # Data access patterns
```

**Key Components**:
- **Config**: Application settings, paths, and environment configuration
- **File Handlers**: Excel processing, file conversion utilities
- **Repositories**: Data access patterns for reading/writing data

**Adding New Features**:
- Add new file handlers in `data/file_handlers/` for new file formats
- Create repositories in `data/repositories/` for new data sources
- Update configuration in `config/` for new settings

### 🖥️ Presentation Layer (`src/presentation/`)

**Purpose**: Handles user interaction through different interfaces (web, CLI).

```
presentation/
├── cli/            # Command-line interface
├── streamlit/      # Web interface using Streamlit
│   ├── pages/      # Individual page components
│   ├── components/ # Reusable UI components
│   └── utils/      # Streamlit-specific utilities
```

**Key Components**:
- **CLI**: Command-line interface for automation and scripting
- **Streamlit Pages**: Web interface pages for interactive analysis
- **Components**: Reusable UI components
- **Utils**: Presentation layer utilities

**Adding New Features**:
- Add new pages in `streamlit/pages/` for new web interfaces
- Create reusable components in `streamlit/components/`
- Add CLI commands in `cli/` for new command-line operations

### 🔄 Shared Layer (`src/shared/`)

**Purpose**: Contains utilities and constants shared across all layers.

```
shared/
├── constants/      # Application-wide constants
└── utils/         # Common utilities (export, formatting, etc.)
```

## Entry Points

### 1. Streamlit Web Application
```bash
streamlit run streamlit_app.py
```
- **Main File**: `streamlit_app.py`
- **Pages**: `src/presentation/streamlit/pages/`
- **Navigation**: Multi-page app with Introduction, Reports, and Comparison

### 2. Command Line Interface
```bash
python -m src.presentation.cli.main
```
- **Main File**: `src/presentation/cli/main.py`
- **Commands**: Generate reports, process data, compare matrices

### 3. Legacy Entry Point
```bash
python main.py
```
- **Main File**: `main.py`
- **Purpose**: Backward compatibility, uses new architecture internally

## Key Design Patterns

### 1. **Use Case Pattern**
Each major application operation is encapsulated in a use case class:
- `GenerateReportsUseCase`: Generate all BNI analysis reports
- `ProcessPalmsDataUseCase`: Process raw PALMS data
- `CompareMatricesUseCase`: Compare matrix files

### 2. **Repository Pattern**
Data access is abstracted through repository interfaces:
- `MemberRepository`: Access member data
- `PalmsRepository`: Access PALMS data

### 3. **Service Pattern**
Business logic is organized in domain services:
- `AnalysisService`: Core analysis operations
- `MatrixService`: Matrix generation and manipulation
- `ComparisonService`: Matrix comparison logic

### 4. **DTO Pattern**
Data transfer between layers uses dedicated objects:
- `ReportGenerationRequest/Response`
- `MatrixComparisonRequest/Response`
- `ProcessPalmsDataRequest/Response`

## Adding New Features

### 🆕 Adding a New Analysis Type

1. **Domain Layer**:
   ```python
   # src/domain/models/new_analysis.py
   @dataclass
   class NewAnalysis:
       # Define your domain entity
   
   # src/domain/services/new_analysis_service.py
   class NewAnalysisService:
       # Implement business logic
   ```

2. **Application Layer**:
   ```python
   # src/application/use_cases/new_analysis_use_case.py
   class NewAnalysisUseCase:
       # Orchestrate domain services
   
   # src/application/dto/new_analysis_dto.py
   @dataclass
   class NewAnalysisRequest:
       # Define request structure
   ```

3. **Presentation Layer**:
   ```python
   # src/presentation/streamlit/pages/new_analysis_page.py
   def render_new_analysis_page():
       # Create Streamlit interface
   ```

### 🔧 Adding a New File Format

1. **Infrastructure Layer**:
   ```python
   # src/infrastructure/data/file_handlers/new_format_handler.py
   class NewFormatHandler:
       # Implement file parsing logic
   ```

2. **Update Configuration**:
   ```python
   # src/infrastructure/config/settings.py
   # Add new format to supported extensions
   ```

### 📊 Adding a New Export Format

1. **Shared Layer**:
   ```python
   # src/shared/utils/export_utils.py
   class ExportService:
       def export_to_new_format(self, data, file_path):
           # Implement export logic
   ```

### 🖥️ Adding a New UI Component

1. **Presentation Layer**:
   ```python
   # src/presentation/streamlit/components/new_component.py
   def create_new_component():
       # Create reusable Streamlit component
   ```

## Configuration Management

### Settings Structure
- **Application Settings**: `src/infrastructure/config/settings.py`
- **Path Management**: `src/infrastructure/config/paths.py`
- **Constants**: `src/shared/constants/app_constants.py`

### Environment Variables
```bash
BNI_DEBUG=true              # Enable debug mode
BNI_LOG_LEVEL=DEBUG         # Set log level
BNI_EXCEL_DIR=./excel       # Custom Excel files directory
BNI_MEMBERS_DIR=./members   # Custom member files directory
BNI_REPORTS_DIR=./reports   # Custom reports directory
```

## Testing Strategy

### Unit Tests
- Test domain services in isolation
- Mock external dependencies
- Focus on business logic correctness

### Integration Tests
- Test use cases with real repositories
- Test file handlers with sample files
- Test end-to-end workflows

### UI Tests
- Test Streamlit components
- Test user interactions
- Test file upload/download flows

## Directory Structure Reference

```
BNI-Palms-Analysis/
├── main.py                 # Legacy entry point (backward compatibility)
├── streamlit_app.py        # Streamlit web application entry point
├── requirements.txt        # Python dependencies
├── README.md              # Project overview and setup
├── ARCHITECTURE.md        # This file - architecture documentation
│
├── src/                   # Main source code following clean architecture
│   ├── domain/           # Core business logic (framework-independent)
│   │   ├── models/       # Business entities (Member, Referral, etc.)
│   │   ├── services/     # Domain services (AnalysisService, etc.)
│   │   └── exceptions/   # Custom domain exceptions
│   │
│   ├── application/      # Application use cases and DTOs
│   │   ├── use_cases/    # Application workflows
│   │   └── dto/         # Data transfer objects
│   │
│   ├── infrastructure/   # External dependencies and frameworks
│   │   ├── config/      # Configuration and settings
│   │   └── data/        # Data access layer
│   │       ├── file_handlers/  # File processing utilities
│   │       └── repositories/   # Data access patterns
│   │
│   ├── presentation/     # User interfaces
│   │   ├── cli/         # Command-line interface
│   │   └── streamlit/   # Web interface
│   │       ├── pages/   # Individual web pages
│   │       ├── components/  # Reusable UI components
│   │       └── utils/   # Presentation utilities
│   │
│   └── shared/          # Common utilities and constants
│       ├── constants/   # Application-wide constants
│       └── utils/      # Shared utility functions
│
├── Excel Files/         # Input: PALMS Excel reports (created automatically)
├── Member Names/        # Input: Member names Excel files (created automatically)
├── Reports/            # Output: Generated analysis reports (created automatically)
├── New Matrix/         # Input: New matrix files for comparison (created automatically)
└── Old Matrix/         # Input: Old matrix files for comparison (created automatically)
```

## Best Practices

### 1. **Dependency Rule**
- Inner layers should not depend on outer layers
- Use dependency injection for external dependencies
- Keep domain layer pure and framework-independent

### 2. **Single Responsibility**
- Each class should have one reason to change
- Separate data access from business logic
- Keep UI logic separate from business logic

### 3. **Interface Segregation**
- Create small, focused interfaces
- Depend on abstractions, not concretions
- Use repository pattern for data access

### 4. **Error Handling**
- Use custom exceptions for domain errors
- Handle errors at appropriate layer boundaries
- Provide meaningful error messages to users

### 5. **Testing**
- Write tests for domain services first
- Mock external dependencies in unit tests
- Test use cases for integration scenarios

## Future Enhancements

### Potential Features to Add
1. **Database Support**: Add database repositories alongside file-based ones
2. **API Layer**: Add REST API for external integrations
3. **Batch Processing**: Add support for processing multiple files in batch
4. **Advanced Analytics**: Add statistical analysis and trend reporting
5. **User Management**: Add user authentication and role-based access
6. **Scheduling**: Add automated report generation scheduling
7. **Notifications**: Add email/SMS notifications for report completion
8. **Data Validation**: Add comprehensive data validation and error reporting

### Architecture Improvements
1. **Event-Driven Architecture**: Add domain events for loose coupling
2. **CQRS**: Separate read and write models for complex queries
3. **Microservices**: Split into separate services for large-scale deployment
4. **Caching**: Add caching layer for improved performance
5. **Monitoring**: Add application monitoring and logging

This architecture provides a solid foundation for building upon the BNI PALMS Analysis application while maintaining clean separation of concerns and high testability.