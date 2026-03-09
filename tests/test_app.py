"""
Test suite for ACEest Fitness & Gym Flask application.
Uses pytest to validate all core functionalities.
"""

import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import app, init_db, calculate_calories, calculate_bmi, PROGRAMS, DB_NAME


@pytest.fixture
def client():
    """Create a test client with a temporary database."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")

    app.config["TESTING"] = True

    import app as app_module
    original_db = app_module.DB_NAME
    app_module.DB_NAME = db_path

    init_db()

    with app.test_client() as test_client:
        yield test_client

    app_module.DB_NAME = original_db
    os.close(db_fd)
    os.unlink(db_path)


# ---- Unit Tests for Helper Functions ----

class TestCalculateCalories:
    def test_fat_loss_3day(self):
        result = calculate_calories(70, "Fat Loss (FL) - 3 day")
        assert result == 70 * 22

    def test_fat_loss_5day(self):
        result = calculate_calories(80, "Fat Loss (FL) - 5 day")
        assert result == 80 * 24

    def test_muscle_gain(self):
        result = calculate_calories(75, "Muscle Gain (MG) - PPL")
        assert result == 75 * 35

    def test_beginner(self):
        result = calculate_calories(60, "Beginner (BG)")
        assert result == 60 * 26

    def test_zero_weight_returns_none(self):
        result = calculate_calories(0, "Fat Loss (FL) - 3 day")
        assert result is None

    def test_none_weight_returns_none(self):
        result = calculate_calories(None, "Beginner (BG)")
        assert result is None

    def test_invalid_program_returns_none(self):
        result = calculate_calories(70, "Nonexistent Program")
        assert result is None


class TestCalculateBMI:
    def test_normal_bmi(self):
        bmi, category = calculate_bmi(70, 175)
        assert bmi == 22.9
        assert category == "Normal"

    def test_underweight_bmi(self):
        bmi, category = calculate_bmi(45, 175)
        assert bmi < 18.5
        assert category == "Underweight"

    def test_overweight_bmi(self):
        bmi, category = calculate_bmi(85, 170)
        assert 25 <= bmi < 30
        assert category == "Overweight"

    def test_obese_bmi(self):
        bmi, category = calculate_bmi(120, 170)
        assert bmi >= 30
        assert category == "Obese"

    def test_zero_height_returns_none(self):
        bmi, category = calculate_bmi(70, 0)
        assert bmi is None
        assert category is None

    def test_none_values_returns_none(self):
        bmi, category = calculate_bmi(None, None)
        assert bmi is None
        assert category is None


class TestProgramData:
    def test_all_programs_have_factor(self):
        for name, data in PROGRAMS.items():
            assert "factor" in data, f"Program '{name}' missing 'factor'"

    def test_all_programs_have_desc(self):
        for name, data in PROGRAMS.items():
            assert "desc" in data, f"Program '{name}' missing 'desc'"

    def test_all_programs_have_workout(self):
        for name, data in PROGRAMS.items():
            assert "workout" in data, f"Program '{name}' missing 'workout'"

    def test_all_programs_have_diet(self):
        for name, data in PROGRAMS.items():
            assert "diet" in data, f"Program '{name}' missing 'diet'"

    def test_program_count(self):
        assert len(PROGRAMS) == 4


# ---- Integration Tests for Routes ----

class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_json(self, client):
        response = client.get("/health")
        data = response.get_json()
        assert data["status"] == "healthy"
        assert data["app"] == "ACEest Fitness & Gym"


class TestIndexPage:
    def test_index_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_index_contains_app_name(self, client):
        response = client.get("/")
        assert b"ACEest" in response.data


class TestAddClient:
    def test_add_client_success(self, client):
        response = client.post("/client/add", data={
            "name": "Ravi Kumar",
            "age": 25,
            "height": 175,
            "weight": 70,
            "program": "Fat Loss (FL) - 3 day",
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b"Ravi Kumar" in response.data

    def test_add_client_no_name(self, client):
        response = client.post("/client/add", data={
            "name": "",
            "age": 25,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b"required" in response.data

    def test_add_duplicate_client(self, client):
        client.post("/client/add", data={
            "name": "Duplicate User",
            "program": "Beginner (BG)",
        })
        response = client.post("/client/add", data={
            "name": "Duplicate User",
            "program": "Beginner (BG)",
        }, follow_redirects=True)
        assert b"already exists" in response.data


class TestClientDetail:
    def test_view_client(self, client):
        client.post("/client/add", data={
            "name": "Test User",
            "age": 30,
            "weight": 80,
            "height": 180,
            "program": "Muscle Gain (MG) - PPL",
        })
        response = client.get("/client/1")
        assert response.status_code == 200
        assert b"Test User" in response.data

    def test_view_nonexistent_client(self, client):
        response = client.get("/client/999", follow_redirects=True)
        assert response.status_code == 200
        assert b"not found" in response.data


class TestEditClient:
    def test_edit_client(self, client):
        client.post("/client/add", data={
            "name": "Edit User",
            "weight": 70,
            "program": "Beginner (BG)",
        })
        response = client.post("/client/1/edit", data={
            "age": 28,
            "height": 170,
            "weight": 75,
            "program": "Fat Loss (FL) - 5 day",
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b"updated" in response.data


class TestDeleteClient:
    def test_delete_client(self, client):
        client.post("/client/add", data={
            "name": "Delete Me",
            "program": "Beginner (BG)",
        })
        response = client.post("/client/1/delete", follow_redirects=True)
        assert response.status_code == 200
        assert b"deleted" in response.data


class TestProgress:
    def test_add_progress(self, client):
        client.post("/client/add", data={
            "name": "Progress User",
            "program": "Beginner (BG)",
        })
        response = client.post("/client/1/progress", data={
            "week": "Week 10 - 2026",
            "adherence": 85,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b"Progress logged" in response.data


class TestWorkout:
    def test_add_workout(self, client):
        client.post("/client/add", data={
            "name": "Workout User",
            "program": "Muscle Gain (MG) - PPL",
        })
        response = client.post("/client/1/workout", data={
            "date": "2026-03-09",
            "workout_type": "Strength",
            "duration": 60,
            "notes": "Heavy squat day",
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b"Workout logged" in response.data


class TestMetrics:
    def test_add_metrics(self, client):
        client.post("/client/add", data={
            "name": "Metrics User",
            "program": "Fat Loss (FL) - 3 day",
        })
        response = client.post("/client/1/metrics", data={
            "date": "2026-03-09",
            "weight": 69.5,
            "waist": 80,
            "bodyfat": 18.5,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b"Metrics logged" in response.data


class TestAPIEndpoints:
    def test_api_programs(self, client):
        response = client.get("/api/programs")
        assert response.status_code == 200
        data = response.get_json()
        assert "Fat Loss (FL) - 3 day" in data

    def test_api_clients_empty(self, client):
        response = client.get("/api/clients")
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)

    def test_api_clients_with_data(self, client):
        client.post("/client/add", data={
            "name": "API User",
            "program": "Beginner (BG)",
        })
        response = client.get("/api/clients")
        data = response.get_json()
        assert len(data) == 1
        assert data[0]["name"] == "API User"

    def test_api_bmi(self, client):
        client.post("/client/add", data={
            "name": "BMI User",
            "weight": 70,
            "height": 175,
            "program": "Beginner (BG)",
        })
        response = client.get("/api/client/1/bmi")
        data = response.get_json()
        assert data["bmi"] == 22.9
        assert data["category"] == "Normal"

    def test_api_bmi_not_found(self, client):
        response = client.get("/api/client/999/bmi")
        assert response.status_code == 404
