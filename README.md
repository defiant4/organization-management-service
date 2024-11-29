# Organization Management Backend Service

## 🚀 Project Overview
A robust backend service for organization management, designed to provide scalable and secure organization creation and management.

## 📋 Prerequisites

### System Requirements
- **Python**: 3.12
- **PostgreSQL**: 13+
- **Poetry**: Latest version
- **Docker**: Latest version
- **Operating System**: Linux/macOS/Windows

### 🛠 Development Environment Setup

#### 1. Install Python 3.12
- **macOS**:
  ```bash
  brew install python@3.12

Linux (Ubuntu/Debian):
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-dev

Windows:
Download from Python Official Website

2. Install Poetry
- curl -sSL https://install.python-poetry.org | python3 -
🔧 Local Development Setup
* Create Virtual Environment
- `poetry env use 3.12`
- `poetry install`
* Activate Virtual Environment
- `poetry shell`
* To simplify setup, use the Makefile:
- `make venv`  (Sets up the virtual environment)
- `source .venv/bin/activate`  (Activates the virtual environment)

### Run the service:
- `make run`

* Open the API documentation in your browser:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

🐳 Docker Deployment
Build and Run
Production Deployment Commands
### Stop any existing containers
- `make docker-stop`

### Build Docker image
- `make docker-build`

### Verify image is created
- `docker images`

### Run in dev mode
- `make docker-dev-run`

### Run in production mode
- `make docker-run-prod`

### Verify running containers
- `docker ps`
### Stop Production Container
- `make docker-stop-prod`

🛡️ Security Notes

Ensure you have a secure .env file for sensitive configurations
Never commit secrets or sensitive information to version control

📦 Dependencies

Managed via Poetry

Core dependencies listed in pyproject.toml

🚧 Development Workflow

- Create a virtual environment
- Install dependencies
- Start local development server

🤝 Contributing

- Fork the repository
- Create your feature branch (git checkout -b feature/AmazingFeature)
- Commit your changes (git commit -m 'Add some AmazingFeature')
- Push to the branch (git push origin feature/AmazingFeature)
- Open a Pull Request

## Versioning

Currently, there is only 1 active version of this project.

## Author

* **Arnab Adhikari** - *Complete E2E Development*

## 📄 License

This project is currently not licensed and is free to use subject to clearance from the author.

💬 Support

For any queries or issues, please open a GitHub issue in the repository or contact arnabadhikari93@gmail.com