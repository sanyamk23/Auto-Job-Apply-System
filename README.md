# Auto Job Apply and Recommendation System

A comprehensive system that recommends jobs to students based on their skills and preferences, automatically applies to jobs on their behalf, and sends personalized emails to HR contacts when available.

## Features

- **Student Profile Management**: Create and manage student profiles with skills, preferences, and resume
- **Job Recommendation Engine**: AI-powered job matching based on skills, location, and preferences
- **Automated Job Application**: Intelligent web scraping and form filling for job applications
- **HR Email Integration**: Extract and contact HR directly with personalized messages
- **Background Processing**: Asynchronous task processing with Celery and Redis
- **RESTful API**: FastAPI-based API with automatic documentation
- **Database Integration**: PostgreSQL with SQLAlchemy ORM
- **Containerization**: Docker and Docker Compose for easy deployment
- **CI/CD Pipeline**: GitHub Actions for automated testing and deployment

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **Cache/Queue**: Redis
- **ORM**: SQLAlchemy
- **Task Queue**: Celery
- **Web Scraping**: Selenium, BeautifulSoup
- **Email**: SMTP
- **Containerization**: Docker, Docker Compose
- **Testing**: pytest, pytest-cov
- **Code Quality**: black, isort, flake8, mypy
- **Security**: bandit, safety
- **CI/CD**: GitHub Actions

## Project Structure

```
job-apply-recommendation-system/
│
├── src/                          # Source code
│   ├── api/                      # API routes and endpoints
│   ├── core/                     # Configuration and core functionality
│   ├── models/                   # Database models
│   ├── services/                 # Business logic services
│   ├── tasks/                    # Celery tasks
│   ├── utils/                    # Utility functions
│   ├── db/                       # Database connection and session
│   ├── schemas/                  # Pydantic schemas
│   ├── tests/                    # Unit and integration tests
│   └── main.py                   # Application entry point
│
├── docs/                         # Documentation
├── scripts/                      # Utility scripts
├── .github/workflows/            # CI/CD pipelines
├── ci/                           # CI/CD configuration
│
├── Dockerfile                    # Docker container configuration
├── docker-compose.yml            # Multi-container setup
├── requirements.txt              # Python dependencies
├── .env.sample                   # Environment variables template
├── .gitignore                    # Git ignore rules
├── README.md                     # Project documentation
├── TODO.md                       # Development roadmap
└── LICENSE                       # License information
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/job-apply-recommendation-system.git
cd job-apply-recommendation-system
```

2. Copy environment variables:
```bash
cp .env.sample .env
```

3. Update the `.env` file with your configuration.

4. Start the services:
```bash
docker-compose up -d
```

The API will be available at `http://localhost:8000`

### Development Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up pre-commit hooks:
```bash
pre-commit install
```

4. Run the application:
```bash
python src/main.py
```

### Run the FastAPI server (development)

If you want to run the newly added FastAPI backend, install dependencies and start uvicorn:

```bash
source venv/bin/activate  # if using a venv
pip install -r requirements.txt
uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
```

Then open the interactive API docs at: http://localhost:8000/docs

## API Documentation

Once the application is running, visit `http://localhost:8000/docs` for interactive API documentation.

## Testing

Run the test suite:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=src --cov-report=html
```

## Code Quality

Format code:
```bash
black src
isort src
```

Lint code:
```bash
flake8 src
mypy src
```

Security check:
```bash
bandit -r src
safety check
```

## Deployment

### Production Deployment

1. Build and run with Docker Compose:
```bash
docker-compose -f docker-compose.yml up -d
```

2. Or deploy to cloud platforms (AWS, GCP, Azure) using the provided CI/CD pipelines.

### Environment Variables

See `.env.sample` for all required environment variables.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes and add tests
4. Run the test suite: `pytest`
5. Commit your changes: `git commit -am 'Add your feature'`
6. Push to the branch: `git push origin feature/your-feature`
7. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Roadmap

See [TODO.md](TODO.md) for the development roadmap and upcoming features.
