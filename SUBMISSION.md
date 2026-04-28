# ACEest Fitness & Gym — DevOps CI/CD Assignment Submission

**Course:** Introduction to DevOps  
**Institution:** BITS Pilani (WILP)  
**GitHub Repository:** https://github.com/hemanthkv14/ACEest-Fitness-Gym

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Application Architecture](#2-application-architecture)
3. [Version Control Strategy (Git)](#3-version-control-strategy-git)
4. [Flask Web Application](#4-flask-web-application)
5. [Testing with Pytest](#5-testing-with-pytest)
6. [Docker Containerization](#6-docker-containerization)
7. [GitHub Actions CI/CD Pipeline](#7-github-actions-cicd-pipeline)
8. [Jenkins BUILD Pipeline](#8-jenkins-build-pipeline)
9. [SonarQube Code Quality Analysis](#9-sonarqube-code-quality-analysis)
10. [Deliverables Summary](#10-deliverables-summary)

---

## 1. Project Overview

**ACEest Fitness & Gym** is a full-stack web application for gym and fitness client management. It was originally built as a tkinter desktop application and progressively evolved through 10 versions before being migrated to a Flask-based web application with a complete DevOps CI/CD pipeline.

### Key Features

- Client profile management (CRUD operations)
- Pre-configured fitness programs (Fat Loss, Muscle Gain, Beginner)
- Automatic calorie estimation based on bodyweight and program type
- BMI calculator with health risk categorization
- Workout session logging with type, duration, and notes
- Weekly adherence progress tracking
- Body metrics recording (weight, waist, body fat)
- REST API endpoints for programmatic access
- Health check endpoint for container orchestration

### Tech Stack

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

## 2. Application Architecture

### Project Structure

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
└── README.md                       # Project documentation
```

### Application Flow

```
User Browser  →  Flask Routes (app.py)  →  SQLite Database (aceest_fitness.db)
                      ↓
              Jinja2 Templates (templates/)
                      ↓
              HTML Response → User Browser
```

### API Endpoints

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

## 3. Version Control Strategy (Git)

### Branching Strategy

The project uses a **feature-branch workflow**:

- `main` — Production-ready code, all CI/CD pipelines run here
- `feature/flask-migration` — Used for the tkinter-to-Flask migration, merged into `main`

### Commit History

The commit history demonstrates a logical, versioned progression from the initial prototype through the final CI/CD-enabled web application:

```
* docs: update README and tighten project configurations
* ci: add SonarQube scanner configuration
* ci: add GitHub Actions CI/CD workflow
* ci: add Jenkins declarative pipeline with SonarQube and Docker
* test: expand test suite to 42 tests with edge-case coverage
* fix: correct test client name in dashboard template
* fix: initialize database on module import for Gunicorn compatibility
*   merge: integrate Flask web application from feature/flask-migration
|\  
| * refactor: remove legacy tkinter app (replaced by Flask)
| * feat: migrate from tkinter to Flask web application
|/  
* refactor(v3.2.4): modular dashboard with embedded charts and workout tab
* feat(v3.1.2): add user authentication, AI program generator, and PDF reports
* feat(v2.2.4): add workout logging, body metrics, BMI, and tabbed UI
* feat(v2.2.1): add progress chart and matplotlib visualization
* feat(v2.0.1): migrate to SQLite database for persistent storage
* feat(v1.1.2): add multi-client table, CSV export, and progress chart
* feat(v1.1): add client profile inputs and calorie estimation
* feat(v1.0): initial tkinter prototype with program display
```

**Commit message conventions used:**
- `feat:` — New feature or capability
- `fix:` — Bug fix
- `refactor:` — Code restructuring without behavior change
- `ci:` — CI/CD pipeline changes
- `test:` — Test additions or improvements
- `docs:` — Documentation updates

> **Screenshot: GitHub repository commit history**
>
> _[Insert screenshot of GitHub commits page showing the commit history]_

> **Screenshot: GitHub repository branch graph**
>
> _[Insert screenshot showing the feature branch merge in the network graph]_

---

## 4. Flask Web Application

### Application Description

The Flask application (`app.py`) is a 466-line Python web server that provides:

- **Database layer**: SQLite with 4 tables (clients, progress, workouts, metrics)
- **Business logic**: Calorie estimation using program-specific factors, BMI calculation with health categories
- **Web routes**: Full CRUD for clients, plus logging endpoints for progress/workouts/metrics
- **REST API**: JSON endpoints for programs, clients, and BMI data
- **Health check**: `/health` endpoint returning `{"status": "healthy"}` for container orchestration

### Key Code Highlights

**Calorie Estimation:**
```python
def calculate_calories(weight, program_name):
    if weight and weight > 0 and program_name in PROGRAMS:
        factor = PROGRAMS[program_name]["factor"]
        return int(weight * factor)
    return None
```

**BMI Calculator:**
```python
def calculate_bmi(weight, height_cm):
    if not weight or not height_cm or weight <= 0 or height_cm <= 0:
        return None, None
    h_m = height_cm / 100.0
    bmi = round(weight / (h_m * h_m), 1)
    # Categories: Underweight (<18.5), Normal (18.5-25), Overweight (25-30), Obese (30+)
```

**Dependencies (`requirements.txt`):**
```
Flask==3.1.0
pytest==8.3.4
pytest-cov==6.0.0
flake8==7.1.1
gunicorn==23.0.0
```

> **Screenshot: Application dashboard (home page)**
>
> _[Insert screenshot of the Flask app running at localhost:5000 showing the client dashboard]_

> **Screenshot: Client detail page**
>
> _[Insert screenshot of a client profile page with workout/progress/metrics sections]_

> **Screenshot: REST API response (`/api/programs`)**
>
> _[Insert screenshot of the JSON response from the /api/programs endpoint]_

---

## 5. Testing with Pytest

### Test Suite Overview

The test suite (`tests/test_app.py`) contains **42 tests** organized into class-based groups covering both unit and integration testing:

| Test Class               | Tests | What it covers                                |
|--------------------------|-------|-----------------------------------------------|
| TestCalculateCalories    | 7     | Calorie estimation for all programs + edge cases |
| TestCalculateBMI         | 6     | BMI calculation for all categories + edge cases  |
| TestProgramData          | 5     | Program data structure validation             |
| TestHealthEndpoint       | 2     | Health check endpoint status and JSON response |
| TestIndexPage            | 2     | Dashboard page rendering                      |
| TestAddClient            | 3     | Client creation, validation, duplicate handling |
| TestClientDetail         | 2     | Client profile view + nonexistent client      |
| TestEditClient           | 2     | Client update + nonexistent client            |
| TestDeleteClient         | 2     | Client deletion + nonexistent client          |
| TestProgress             | 2     | Progress logging + nonexistent client         |
| TestWorkout              | 2     | Workout logging + nonexistent client          |
| TestMetrics              | 2     | Metrics logging + nonexistent client          |
| TestAPIEndpoints         | 5     | REST API responses, data, and 404 handling    |
| **Total**                | **42**|                                               |

### Test Execution

```bash
# Run locally
pytest tests/ -v --tb=short

# Run inside Docker container
docker run --rm aceest-fitness-gym python -m pytest tests/ -v --tb=short
```

### Test Design

- Uses a **temporary SQLite database** per test (pytest fixture with `tempfile.mkstemp`)
- Flask **test client** for integration tests (simulates HTTP requests)
- Tests cover both **happy paths** and **error paths** (nonexistent clients, empty inputs, duplicates)
- Follows `Arrange-Act-Assert` pattern

> **Screenshot: Pytest output showing all 42 tests passing**
>
> _[Insert screenshot of terminal showing `pytest tests/ -v` with all 42 tests PASSED]_

> **Screenshot: Pytest running inside Docker container**
>
> _[Insert screenshot of `docker run --rm aceest-fitness-gym python -m pytest tests/ -v` output]_

---

## 6. Docker Containerization

### Dockerfile

```dockerfile
FROM python:3.12-slim

LABEL maintainer="ACEest Fitness & Gym"
LABEL description="Flask web application for gym and fitness management"

WORKDIR /app

RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chown -R appuser:appgroup /app
USER appuser

EXPOSE 5000

ENV FLASK_APP=app.py
ENV FLASK_ENV=production

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
```

### Docker Optimization & Security Features

| Feature                     | Implementation                                        |
|-----------------------------|-------------------------------------------------------|
| **Small base image**        | `python:3.12-slim` (~120MB vs ~900MB full image)      |
| **Non-root user**           | Runs as `appuser` (not root) for security             |
| **Layer caching**           | `COPY requirements.txt` before `COPY .` for faster builds |
| **No pip cache**            | `--no-cache-dir` reduces image size                   |
| **Health check**            | Built-in `HEALTHCHECK` pinging `/health` every 30s    |
| **Production WSGI server**  | Gunicorn with 2 workers (not Flask dev server)        |
| **`.dockerignore`**         | Excludes .git, IDE files, tests docs from build context |

### Docker Commands

```bash
# Build
docker build -t aceest-fitness-gym .

# Run
docker run -p 5000:5000 aceest-fitness-gym

# Run tests inside container
docker run --rm aceest-fitness-gym python -m pytest tests/ -v

# Export image
docker save aceest-fitness-gym -o aceest-fitness-gym.tar
```

> **Screenshot: Docker build output**
>
> _[Insert screenshot of `docker build -t aceest-fitness-gym .` output]_

> **Screenshot: Docker container running and accessible at localhost:5000**
>
> _[Insert screenshot of browser showing the app running from the Docker container]_

> **Screenshot: Docker image listing (`docker images`)**
>
> _[Insert screenshot of `docker images aceest-fitness-gym` showing image size]_

---

## 7. GitHub Actions CI/CD Pipeline

### Pipeline Configuration (`.github/workflows/main.yml`)

**Trigger:** On every `push` to `main`, `master`, `develop`, `feature/*` branches and on `pull_request` to `main`/`master`.

### Pipeline Stages

```
push / PR  →  [Build & Lint]  →  [Automated Testing]  →  [Docker Image Assembly]
```

| Stage                    | Description                                                   |
|--------------------------|---------------------------------------------------------------|
| **Build & Lint**         | Sets up Python 3.12, installs dependencies, runs `flake8`     |
| **Automated Testing**    | Executes 42 Pytest tests with JUnit XML report output         |
| **Docker Image Assembly**| Builds Docker image, verifies it, runs tests inside container |

### Stage Details

**Stage 1: Build & Lint**
- Checks out code using `actions/checkout@v4`
- Sets up Python 3.12 using `actions/setup-python@v5`
- Installs dependencies from `requirements.txt`
- Runs `flake8` for critical errors (E9, F63, F7, F82) and style checks

**Stage 2: Automated Testing**
- Depends on Stage 1 (`needs: build-and-lint`)
- Runs full Pytest suite with verbose output
- Generates JUnit XML report (`test-results.xml`)

**Stage 3: Docker Image Assembly**
- Depends on Stage 2 (`needs: test`)
- Builds Docker image tagged with commit SHA
- Verifies image was created
- Runs Pytest inside the container to validate the packaged application

### Workflow YAML

```yaml
name: ACEest CI/CD Pipeline

on:
  push:
    branches: [ main, master, develop, "feature/*" ]
  pull_request:
    branches: [ main, master ]

jobs:
  build-and-lint:
    name: Build & Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: flake8 app.py --count --select=E9,F63,F7,F82 --show-source --statistics

  test:
    name: Automated Testing
    runs-on: ubuntu-latest
    needs: build-and-lint
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v --tb=short --junitxml=test-results.xml

  docker-build:
    name: Docker Image Assembly
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t aceest-fitness-gym:${{ github.sha }} .
      - run: docker run --rm aceest-fitness-gym:${{ github.sha }} python -m pytest tests/ -v --tb=short
```

> **Screenshot: GitHub Actions workflow runs page**
>
> _[Insert screenshot of the Actions tab showing successful workflow runs]_

> **Screenshot: GitHub Actions pipeline — all 3 stages passed (green checkmarks)**
>
> _[Insert screenshot of a workflow run detail showing Build & Lint, Test, and Docker stages all green]_

> **Screenshot: Build & Lint stage output**
>
> _[Insert screenshot of the flake8 lint output in the GitHub Actions log]_

> **Screenshot: Automated Testing stage output (42 tests passed)**
>
> _[Insert screenshot of the Pytest output in the GitHub Actions log showing all tests passed]_

> **Screenshot: Docker Image Assembly stage output**
>
> _[Insert screenshot of Docker build and in-container test output in GitHub Actions]_

---

## 8. Jenkins BUILD Pipeline

### Pipeline Configuration (`Jenkinsfile`)

**Trigger:** SCM Polling (`pollSCM('H/2 * * * *')`) — checks for new commits every 2 minutes.

### Pipeline Stages

```
Commit  →  [Checkout]  →  [SonarQube Analysis]  →  [Docker Build]  →  [Lint]  →  [Test]  →  [Export Docker Image]
```

| Stage                  | Description                                                     |
|------------------------|-----------------------------------------------------------------|
| **Checkout**           | Pulls the latest code from the GitHub repository                |
| **SonarQube Analysis** | Runs static code analysis using SonarQube Scanner               |
| **Docker Build**       | Builds the Docker container image and tags as `latest`          |
| **Lint**               | Runs `flake8` linter inside the Docker container                |
| **Test**               | Executes 42 Pytest tests inside the Docker container            |
| **Export Docker Image** | Saves Docker image as a `.tar` artifact for download           |

### Key Design Decisions

1. **Containerized linting and testing** — All lint and test stages run inside the Docker container, ensuring consistency between development and CI environments.
2. **Downloadable artifact** — The pipeline exports the Docker image as a `.tar` file, available for download from Jenkins build artifacts.
3. **SonarQube integration** — Static code analysis runs before Docker build to catch code quality issues early.

### Jenkins Setup

1. Install Jenkins with Docker available on the build agent
2. Add `jenkins` user to docker group: `sudo usermod -aG docker jenkins`
3. Install **SonarQube Scanner** plugin
4. Configure SonarQube server in Manage Jenkins → System → SonarQube servers
5. Create Pipeline project → Pipeline script from SCM → Git → Script Path: `Jenkinsfile`

> **Screenshot: Jenkins dashboard showing the pipeline project**
>
> _[Insert screenshot of the Jenkins dashboard with the ACEest-Fitness-Gym pipeline]_

> **Screenshot: Jenkins pipeline stage view (all stages green)**
>
> _[Insert screenshot of the Jenkins pipeline visualization showing all 6 stages passed]_

> **Screenshot: Jenkins build console output — Checkout stage**
>
> _[Insert screenshot of the Checkout stage logs]_

> **Screenshot: Jenkins build console output — SonarQube Analysis stage**
>
> _[Insert screenshot of the SonarQube scanner output in Jenkins]_

> **Screenshot: Jenkins build console output — Docker Build stage**
>
> _[Insert screenshot of the Docker build output in Jenkins]_

> **Screenshot: Jenkins build console output — Test stage (42 tests passed)**
>
> _[Insert screenshot of Pytest running inside Docker in Jenkins showing all tests passed]_

> **Screenshot: Jenkins build artifact — Docker .tar file available for download**
>
> _[Insert screenshot of the Jenkins build artifacts page showing the .tar file]_

> **Screenshot: Jenkins SCM polling configuration**
>
> _[Insert screenshot showing the pollSCM configuration in Jenkins pipeline settings]_

---

## 9. SonarQube Code Quality Analysis

### Configuration

SonarQube is integrated into the Jenkins pipeline for static code analysis. The scanner is configured via `sonar-project.properties`:

```properties
sonar.projectKey=aceest-fitness-gym
sonar.projectName=ACEest Fitness & Gym
sonar.projectVersion=3.2.4

sonar.sources=.
sonar.inclusions=app.py
sonar.tests=tests
sonar.test.inclusions=tests/test_app.py

sonar.language=python
sonar.python.version=3.12
```

### What SonarQube Analyzes

- **Code Smells** — Maintainability issues in the codebase
- **Bugs** — Potential runtime errors or incorrect behavior
- **Vulnerabilities** — Security weaknesses in the code
- **Code Duplication** — Repeated code blocks that should be refactored
- **Complexity** — Cyclomatic complexity of functions

### Jenkins Integration

The SonarQube stage in Jenkins uses `withSonarQubeEnv` to securely pass the authentication token and runs the scanner before Docker build, so code quality issues are detected early in the pipeline.

```groovy
stage('SonarQube Analysis') {
    steps {
        withSonarQubeEnv('SonarQube') {
            sh "${SCANNER_HOME}/bin/sonar-scanner \
                -Dsonar.projectKey=${APP_NAME} \
                -Dsonar.login=\${SONAR_AUTH_TOKEN}"
        }
    }
}
```

> **Screenshot: SonarQube dashboard showing project analysis results**
>
> _[Insert screenshot of the SonarQube project dashboard with quality metrics]_

> **Screenshot: SonarQube code analysis details (bugs, vulnerabilities, code smells)**
>
> _[Insert screenshot of the SonarQube measures/issues page]_

---

## 10. Deliverables Summary

| Deliverable                  | File / Location                      | Status |
|------------------------------|--------------------------------------|--------|
| Flask Web Application        | `app.py`                             | Done   |
| Python Dependencies          | `requirements.txt`                   | Done   |
| Pytest Test Suite            | `tests/test_app.py` (42 tests)      | Done   |
| Dockerfile                   | `Dockerfile`                         | Done   |
| GitHub Actions Workflow      | `.github/workflows/main.yml`         | Done   |
| Jenkins Pipeline             | `Jenkinsfile`                        | Done   |
| SonarQube Configuration      | `sonar-project.properties`           | Done   |
| Project Documentation        | `README.md`                          | Done   |
| Version Control (Git/GitHub) | https://github.com/hemanthkv14/ACEest-Fitness-Gym | Done |

### Evaluation Criteria Mapping

| Criteria               | How it is addressed                                                                 |
|------------------------|-------------------------------------------------------------------------------------|
| **Application Integrity** | Flask app with 12 routes, 4 database tables, REST API, and health check endpoint |
| **VCS Maturity**       | 18 meaningful commits with conventional prefixes, feature branch merge workflow      |
| **Testing Coverage**   | 42 Pytest tests covering unit logic, all routes, API endpoints, and edge cases       |
| **Docker Efficiency**  | Slim base image, non-root user, layer caching, health check, production WSGI server  |
| **Pipeline Reliability** | GitHub Actions (3-stage) and Jenkins (6-stage) pipelines with SonarQube analysis  |
| **Documentation Clarity** | Comprehensive README with setup, API reference, CI/CD docs, and version history  |

---

*End of submission document.*
