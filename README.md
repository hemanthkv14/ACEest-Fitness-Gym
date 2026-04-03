# ACEest Fitness & Gym

A Flask-based web application for fitness and gym client management, featuring workout programming, nutrition planning, progress tracking, and body metrics analytics.

Built as part of the **Introduction to DevOps** course assignment demonstrating end-to-end CI/CD pipeline implementation with Git, Docker, GitHub Actions, Jenkins, and SonarQube.

---

## Features

- **Client Management** — Add, edit, delete, and view client profiles
- **Fitness Programs** — Pre-configured programs: Fat Loss (3-day/5-day), Muscle Gain (PPL), and Beginner
- **Calorie Estimation** — Automatic daily calorie calculation based on bodyweight and selected program
- **BMI Calculator** — Real-time BMI computation with health risk categorization
- **Workout Logging** — Track workout sessions with type, duration, and notes
- **Progress Tracking** — Log weekly adherence percentages and view history
- **Body Metrics** — Record weight, waist, and body fat measurements over time
- **REST API** — JSON endpoints for programs, clients, and BMI data
- **Health Check** — `/health` endpoint for container orchestration and monitoring

---

## Tech Stack

| Layer            | Technology                |
|------------------|---------------------------|
| Application      | Python 3.12, Flask 3.1    |
| Database         | SQLite                    |
| Testing          | Pytest (42 tests), flake8 |
| Containerization | Docker, Gunicorn          |
| CI/CD            | GitHub Actions, Jenkins   |
| Code Quality     | SonarQube 9.9             |
| Version Control  | Git, GitHub               |

---

## Project Structure

```
ACEest-Fitness-Gym/
├── app.py                          # Flask application (routes, models, logic)
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Container image definition
├── Jenkinsfile                     # Jenkins pipeline configuration
├── sonar-project.properties        # SonarQube scanner configuration
├── .dockerignore                   # Docker build exclusions
├── .gitignore                      # Git ignored files
├── .github/
│   └── workflows/
│       └── main.yml                # GitHub Actions CI/CD pipeline
├── templates/
│   ├── base.html                   # Base template with layout and styles
│   ├── index.html                  # Dashboard / client list page
│   └── client_detail.html          # Individual client profile page
├── tests/
│   ├── __init__.py                 # Test package initializer
│   └── test_app.py                 # Pytest test suite (42 tests)
└── README.md                       # This file
```

---

## Local Setup & Execution

### Prerequisites

- Python 3.10+
- pip package manager
- Docker (optional, for containerized execution)

### 1. Clone the Repository

```bash
git clone https://github.com/hemanthkv14/ACEest-Fitness-Gym.git
cd ACEest-Fitness-Gym
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
python app.py
```

The application will start at **http://localhost:5000**.

### 4. Run with Docker

```bash
# Build the image
docker build -t aceest-fitness-gym .

# Run the container
docker run -p 5000:5000 aceest-fitness-gym
```

Access the app at **http://localhost:5000**.

---

## Running Tests

### Run the full test suite

```bash
pytest tests/ -v
```

### Run with short traceback

```bash
pytest tests/ -v --tb=short
```

### Lint the source code

```bash
flake8 app.py --max-line-length=120 --statistics
```

### Run tests inside Docker

```bash
docker run --rm aceest-fitness-gym python -m pytest tests/ -v
```

---

## CI/CD Pipeline Overview

### GitHub Actions (`.github/workflows/main.yml`)

Triggers on every `push` to `main`, `master`, `develop`, and `feature/*` branches, and on `pull_request` to `main`/`master`.

```
push / PR → [Build & Lint] → [Automated Testing] → [Docker Image Assembly]
```

| Stage                    | Description                                                |
|--------------------------|------------------------------------------------------------|
| **Build & Lint**         | Installs dependencies, runs `flake8` for syntax/style errors |
| **Automated Testing**    | Executes the full Pytest suite (42 tests) with JUnit XML output |
| **Docker Image Assembly**| Builds the Docker image and runs tests inside the container |

### Jenkins (`Jenkinsfile`)

Jenkins pipeline is triggered via **SCM polling** (checks for changes every 2 minutes). It uses a declarative pipeline with the following stages:

```
push → [Checkout] → [SonarQube Analysis] → [Docker Build] → [Lint] → [Test] → [Export Docker Image]
```

| Stage                  | Description                                                     |
|------------------------|-----------------------------------------------------------------|
| **Checkout**           | Pulls the latest code from the GitHub repository                |
| **SonarQube Analysis** | Runs static code analysis using SonarQube Scanner               |
| **Docker Build**       | Builds the Docker container image and tags it                   |
| **Lint**               | Runs `flake8` linter inside the Docker container                |
| **Test**               | Executes Pytest suite inside the Docker container               |
| **Export Docker Image** | Saves the Docker image as a `.tar` artifact for download       |

### Jenkins Setup Instructions

1. Install Jenkins and ensure Docker is available on the build agent
2. Add the `jenkins` user to the `docker` group: `sudo usermod -aG docker jenkins`
3. Install the **SonarQube Scanner** plugin and configure the scanner tool as `SonarQubeScanner`
4. Configure the SonarQube server in **Manage Jenkins → System → SonarQube servers**:
   - **Name:** `SonarQube`
   - **URL:** `http://localhost:9000`
   - **Token:** Add a credential with a Global Analysis Token from SonarQube
5. Create a new **Pipeline** project in Jenkins
6. Under **Pipeline → Definition**, select **Pipeline script from SCM**
7. Set SCM to **Git** and enter the repository URL
8. Set the **Script Path** to `Jenkinsfile`
9. The pipeline uses `pollSCM` to automatically detect and build on new commits

### SonarQube Setup

1. Install and run SonarQube (Community Edition 9.9+)
2. Generate a **Global Analysis Token** in SonarQube (My Account → Security → Generate Tokens)
3. Add the token as a **Secret text** credential in Jenkins
4. The `sonar-project.properties` file configures the scanner with project settings

---

## API Endpoints

| Method | Endpoint                    | Description                      |
|--------|-----------------------------|----------------------------------|
| GET    | `/`                         | Dashboard with all clients       |
| POST   | `/client/add`               | Add a new client                 |
| GET    | `/client/<id>`              | View client profile              |
| POST   | `/client/<id>/edit`         | Update client details            |
| POST   | `/client/<id>/delete`       | Delete client and records        |
| POST   | `/client/<id>/progress`     | Log weekly adherence             |
| POST   | `/client/<id>/workout`      | Log a workout session            |
| POST   | `/client/<id>/metrics`      | Log body metrics                 |
| GET    | `/api/programs`             | List all programs (JSON)         |
| GET    | `/api/clients`              | List all clients (JSON)          |
| GET    | `/api/client/<id>/bmi`      | Get client BMI info (JSON)       |
| GET    | `/health`                   | Health check for CI/CD           |

---

## Docker Configuration

- **Base image:** `python:3.12-slim`
- **Non-root user:** Runs as `appuser` for security
- **WSGI server:** Gunicorn with 2 workers
- **Health check:** Built-in `HEALTHCHECK` pinging `/health` every 30s
- **Port:** 5000

### Download and run the Docker image from Jenkins

```bash
# Download the .tar artifact from Jenkins build artifacts page
# Then load and run:
docker load -i aceest-fitness-gym-build-<BUILD_NUMBER>.tar
docker run -p 5000:5000 aceest-fitness-gym:latest
```

---

## Version History

| Version | Description                                                     |
|---------|-----------------------------------------------------------------|
| 1.0     | Initial tkinter prototype with program display                  |
| 1.1     | Added client profile inputs and calorie estimation              |
| 1.1.2   | Added scrollable text blocks, CSV export, matplotlib charts     |
| 2.0.1   | Migrated to SQLite database for persistent storage              |
| 2.1.2   | Added progress charts with matplotlib                           |
| 2.2.1   | Added workout logging, body metrics, BMI calculator             |
| 2.2.4   | Added tabbed notebook UI, workout history treeview              |
| 3.0.1   | Added user authentication and AI program generator              |
| 3.1.2   | Refactored to modular dashboard with embedded charts            |
| 3.2.4   | **Migrated to Flask web app with full CI/CD pipeline**          |

---

## License

This project is developed for educational purposes as part of the BITS Pilani WILP DevOps course.
