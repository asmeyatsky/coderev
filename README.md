# Enhanced Code Review Platform (ECRP)

The Enhanced Code Review Platform (ECRP) is a comprehensive solution designed to transform the code review process by integrating advanced features like ephemeral review environments, in-browser IDE capabilities, AI-driven risk analysis, and collaborative workflows.

## Architecture

The ECRP follows clean architecture principles with the following layers:

- **Domain Layer**: Core business logic, entities, value objects, and domain services
- **Application Layer**: Use cases and DTOs that orchestrate the domain layer
- **Infrastructure Layer**: Repository implementations and external service adapters
- **Presentation Layer**: API controllers and UI components

### Domain Layer

The domain layer implements core business concepts using Domain-Driven Design principles:

- **Entities**: User, CodeReview, Comment, RiskScore, Environment
- **Value Objects**: ReviewPriority, URL, Email
- **Domain Services**: ReviewDomainService
- **Ports**: Repository and external service interfaces

### Application Layer

The application layer contains use cases that orchestrate the domain layer:

- **Use Cases**: CreateCodeReview, ApproveCodeReview, RequestChanges, MergeCodeReview, CreateComment
- **DTOs**: Data transfer objects for communication between layers

### Infrastructure Layer

The infrastructure layer provides implementations for ports:

- **Repositories**: In-memory implementations for MVP
- **Adapters**: Mock adapters for external services (Git providers, risk analysis, etc.)

### Presentation Layer

The presentation layer handles user interaction:

- **API**: Flask-based REST API
- **UI**: HTML/CSS/JavaScript interface for demonstration

## Features Implemented

1. **Code Review Management**: Create, approve, request changes, merge reviews
2. **Risk Analysis**: AI-driven risk scoring with multiple factors
3. **Ephemeral Environments**: Automatic provisioning of review environments
4. **Comments**: Threaded comments on code reviews
5. **User Management**: Role-based access control

## Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository
2. Navigate to the project root directory
3. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   # or if using the setup.py:
   pip install -e .
   ```

### Running the Application

1. From the project root directory, run the Flask application:
   ```bash
   python -m presentation.main
   ```
   or
   ```bash
   cd presentation && python main.py
   ```

2. The API will be available at `http://localhost:5000`
3. The UI is available at `http://localhost:5000/` (the main page serves the HTML file)

### Running Tests

First, install the testing dependencies:
```bash
pip install pytest
```

Then run tests:
```bash
python -m pytest tests/
```

## API Endpoints

- `POST /api/code-reviews` - Create a new code review
- `POST /api/code-reviews/<review_id>/approve` - Approve a code review
- `POST /api/code-reviews/<review_id>/request-changes` - Request changes on a code review
- `POST /api/code-reviews/<review_id>/merge` - Merge a code review
- `POST /api/code-reviews/<review_id>/comments` - Add a comment to a code review
- `GET /health` - Health check endpoint

## Architecture Decisions

- **Clean Architecture**: Clear separation of concerns with dependency inversion
- **Domain-Driven Design**: Rich domain models with business logic encapsulation
- **Ports and Adapters**: Interface-first design for flexibility and testability
- **Immutable Models**: Domain entities are immutable to prevent accidental state changes
- **Comprehensive Testing**: Unit tests for all layers with architectural validation

---
*Repository updated on 2025-10-27*