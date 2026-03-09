# ACEest Fitness & Gym

A Flask-based web application for fitness and gym client management, featuring workout programming, nutrition planning, progress tracking, and body metrics analytics.

Built as part of the **Introduction to DevOps** course assignment demonstrating end-to-end CI/CD pipeline implementation with Git, Docker, GitHub Actions, and Jenkins.

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

| Layer           | Technology              |
|-----------------|-------------------------|
| Application     | Python 3.12, Flask      |
| Database        | SQLite                  |
| Testing         | Pytest, flake8          |
| Containerization| Docker                  |
| CI/CD           | GitHub Actions, Jenkins |
| WSGI Server     | Gunicorn                |

---

## Project Structure

```
ACEest-Fitness-Gym/
├── app.py                          # Flask application (routes, models, logic)
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Container image definition
├── Jenkinsfile                     # Jenkins pipeline configuration
├── .dockerignore                   # Docker build exclusions
├── .github/
│   └── workflows/
│       └── main.yml                # GitHub Actions CI/CD pipeline
├── templates/
│   ├── base.html                   # Base template with layout and styles
│   ├── index.html                  # Dashboard / client list page
│   └── client_detail.html          # Individual client profile page
├── tests/
│   └── test_app.py                 # Pytest test suite
└── README.md                       # This file
```

---

## Local Setup & Execution

### Prerequisites

- Python 3.10+ installed
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

### Run the full test suite locally

```bash
pytest tests/ -v
```

### Run with coverage details

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

The pipeline triggers on every `push` and `pull_request` to the `main` branch and executes three stages:

```
push / PR → [Build & Lint] → [Automated Testing] → [Docker Image Assembly]
```

| Stage                  | Description                                                |
|------------------------|------------------------------------------------------------|
| **Build & Lint**       | Installs dependencies and runs `flake8` for syntax errors  |
| **Automated Testing**  | Executes the Pytest suite to validate application logic    |
| **Docker Image Assembly** | Builds the Docker image and runs tests inside the container |

### Jenkins (`Jenkinsfile`)

Jenkins is configured as a secondary BUILD and quality gate. The pipeline:

1. **Checkout** — Pulls the latest code from the GitHub repository
2. **Setup Environment** — Installs Python dependencies
3. **Lint** — Runs flake8 for code quality checks
4. **Test** — Executes the Pytest test suite
5. **Docker Build** — Builds the Docker container image
6. **Docker Verify** — Runs tests inside the built container

#### Jenkins Setup

1. Install Jenkins and ensure Python 3.12+ and Docker are available on the build agent
2. Create a new **Pipeline** project in Jenkins
3. Under **Pipeline → Definition**, select **Pipeline script from SCM**
4. Set SCM to **Git** and enter the repository URL
5. Set the **Script Path** to `Jenkinsfile`
6. Configure a webhook or poll SCM to trigger builds on push

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
