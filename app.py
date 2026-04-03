"""
ACEest Fitness & Gym - Flask Web Application
A fitness and gym management system for client tracking,
workout programming, nutrition planning, and progress analytics.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import os
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "aceest-dev-secret-key")

DB_NAME = os.environ.get("DATABASE_NAME", "aceest_fitness.db")

PROGRAMS = {
    "Fat Loss (FL) - 3 day": {
        "factor": 22,
        "desc": "3-day full-body fat loss program",
        "workout": (
            "Mon: Back Squat 5x5 + Core AMRAP\n"
            "Wed: Bench Press + 21-15-9 WOD\n"
            "Fri: Zone 2 Cardio 30min + Deadlift 4x6"
        ),
        "diet": (
            "Breakfast: Egg Whites + Oats\n"
            "Lunch: Grilled Chicken + Brown Rice\n"
            "Dinner: Fish Curry + Millet Roti\n"
            "Target: ~2000 kcal"
        ),
    },
    "Fat Loss (FL) - 5 day": {
        "factor": 24,
        "desc": "5-day split, higher volume fat loss",
        "workout": (
            "Mon: Back Squat 5x5 + Core\n"
            "Tue: EMOM 20min Assault Bike\n"
            "Wed: Bench Press + 21-15-9\n"
            "Thu: Deadlift + Box Jumps\n"
            "Fri: Zone 2 Cardio 30min"
        ),
        "diet": (
            "Breakfast: 3 Egg Whites + Oats Idli\n"
            "Lunch: Grilled Chicken + Brown Rice\n"
            "Dinner: Fish Curry + Millet Roti\n"
            "Target: ~2200 kcal"
        ),
    },
    "Muscle Gain (MG) - PPL": {
        "factor": 35,
        "desc": "Push/Pull/Legs hypertrophy program",
        "workout": (
            "Mon: Squat 5x5 + Leg Press 4x10\n"
            "Tue: Bench 5x5 + Incline Press 4x10\n"
            "Wed: Deadlift 4x6 + Barbell Rows 4x10\n"
            "Thu: Front Squat 4x8\n"
            "Fri: Incline Press 4x10\n"
            "Sat: Barbell Rows 4x10"
        ),
        "diet": (
            "Breakfast: 4 Eggs + PB Oats\n"
            "Lunch: Chicken Biryani (250g Chicken)\n"
            "Dinner: Mutton Curry + Jeera Rice\n"
            "Target: ~3200 kcal"
        ),
    },
    "Beginner (BG)": {
        "factor": 26,
        "desc": "3-day simple beginner full-body program",
        "workout": (
            "Full Body Circuit:\n"
            "- Air Squats 3x12\n"
            "- Ring Rows 3x10\n"
            "- Push-ups 3x10\n"
            "- Plank 3x30s\n"
            "Focus: Technique Mastery & Consistency"
        ),
        "diet": (
            "Balanced Tamil Meals:\n"
            "Idli / Dosa / Rice + Dal\n"
            "Protein Target: 120g/day"
        ),
    },
}


def get_db():
    """Create a database connection and return it."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables."""
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            age INTEGER,
            height REAL,
            weight REAL,
            program TEXT,
            calories INTEGER,
            target_weight REAL,
            target_adherence INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            week TEXT NOT NULL,
            adherence INTEGER,
            FOREIGN KEY (client_name) REFERENCES clients(name)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            date TEXT NOT NULL,
            workout_type TEXT,
            duration_min INTEGER,
            notes TEXT,
            FOREIGN KEY (client_name) REFERENCES clients(name)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            date TEXT NOT NULL,
            weight REAL,
            waist REAL,
            bodyfat REAL,
            FOREIGN KEY (client_name) REFERENCES clients(name)
        )
    """)

    conn.commit()
    conn.close()


def calculate_calories(weight, program_name):
    """Calculate estimated daily calories based on weight and program."""
    if weight and weight > 0 and program_name in PROGRAMS:
        factor = PROGRAMS[program_name]["factor"]
        return int(weight * factor)
    return None


def calculate_bmi(weight, height_cm):
    """Calculate BMI from weight (kg) and height (cm)."""
    if not weight or not height_cm or weight <= 0 or height_cm <= 0:
        return None, None
    h_m = height_cm / 100.0
    bmi = round(weight / (h_m * h_m), 1)
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"
    return bmi, category


# ---- Routes ----

@app.route("/")
def index():
    """Home page showing all clients."""
    conn = get_db()
    clients = conn.execute(
        "SELECT * FROM clients ORDER BY name"
    ).fetchall()
    conn.close()
    return render_template("index.html", clients=clients, programs=PROGRAMS)


@app.route("/client/add", methods=["POST"])
def add_client():
    """Add a new client."""
    name = request.form.get("name", "").strip()
    if not name:
        flash("Client name is required.", "error")
        return redirect(url_for("index"))

    age = request.form.get("age", type=int)
    height = request.form.get("height", type=float)
    weight = request.form.get("weight", type=float)
    program = request.form.get("program", "")
    target_weight = request.form.get("target_weight", type=float)
    target_adherence = request.form.get("target_adherence", type=int)

    calories = calculate_calories(weight, program)

    conn = get_db()
    try:
        conn.execute(
            """INSERT INTO clients
               (name, age, height, weight, program, calories,
                target_weight, target_adherence)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (name, age, height, weight, program, calories,
             target_weight, target_adherence),
        )
        conn.commit()
        flash(f"Client '{name}' added successfully.", "success")
    except sqlite3.IntegrityError:
        flash(f"Client '{name}' already exists.", "error")
    finally:
        conn.close()

    return redirect(url_for("index"))


@app.route("/client/<int:client_id>")
def client_detail(client_id):
    """Show detailed client profile with progress and metrics."""
    conn = get_db()
    client = conn.execute(
        "SELECT * FROM clients WHERE id = ?", (client_id,)
    ).fetchone()

    if not client:
        flash("Client not found.", "error")
        conn.close()
        return redirect(url_for("index"))

    progress = conn.execute(
        "SELECT * FROM progress WHERE client_name = ? ORDER BY id DESC",
        (client["name"],),
    ).fetchall()

    workouts = conn.execute(
        "SELECT * FROM workouts WHERE client_name = ? ORDER BY date DESC LIMIT 10",
        (client["name"],),
    ).fetchall()

    metrics = conn.execute(
        "SELECT * FROM metrics WHERE client_name = ? ORDER BY date DESC LIMIT 10",
        (client["name"],),
    ).fetchall()

    avg_adherence = conn.execute(
        "SELECT AVG(adherence) FROM progress WHERE client_name = ?",
        (client["name"],),
    ).fetchone()[0]

    conn.close()

    bmi, bmi_category = calculate_bmi(client["weight"], client["height"])
    program_info = PROGRAMS.get(client["program"], {})

    return render_template(
        "client_detail.html",
        client=client,
        progress=progress,
        workouts=workouts,
        metrics=metrics,
        avg_adherence=round(avg_adherence, 1) if avg_adherence else 0,
        bmi=bmi,
        bmi_category=bmi_category,
        program_info=program_info,
        programs=PROGRAMS,
    )


@app.route("/client/<int:client_id>/edit", methods=["POST"])
def edit_client(client_id):
    """Update an existing client."""
    conn = get_db()
    client = conn.execute(
        "SELECT * FROM clients WHERE id = ?", (client_id,)
    ).fetchone()

    if not client:
        flash("Client not found.", "error")
        conn.close()
        return redirect(url_for("index"))

    age = request.form.get("age", type=int)
    height = request.form.get("height", type=float)
    weight = request.form.get("weight", type=float)
    program = request.form.get("program", "")
    target_weight = request.form.get("target_weight", type=float)
    target_adherence = request.form.get("target_adherence", type=int)

    calories = calculate_calories(weight, program)

    conn.execute(
        """UPDATE clients
           SET age=?, height=?, weight=?, program=?, calories=?,
               target_weight=?, target_adherence=?
           WHERE id=?""",
        (age, height, weight, program, calories,
         target_weight, target_adherence, client_id),
    )
    conn.commit()
    conn.close()
    flash("Client updated successfully.", "success")
    return redirect(url_for("client_detail", client_id=client_id))


@app.route("/client/<int:client_id>/delete", methods=["POST"])
def delete_client(client_id):
    """Delete a client and all associated records."""
    conn = get_db()
    client = conn.execute(
        "SELECT name FROM clients WHERE id = ?", (client_id,)
    ).fetchone()

    if client:
        name = client["name"]
        conn.execute("DELETE FROM progress WHERE client_name = ?", (name,))
        conn.execute("DELETE FROM workouts WHERE client_name = ?", (name,))
        conn.execute("DELETE FROM metrics WHERE client_name = ?", (name,))
        conn.execute("DELETE FROM clients WHERE id = ?", (client_id,))
        conn.commit()
        flash(f"Client '{name}' deleted.", "success")

    conn.close()
    return redirect(url_for("index"))


@app.route("/client/<int:client_id>/progress", methods=["POST"])
def add_progress(client_id):
    """Log weekly adherence progress for a client."""
    conn = get_db()
    client = conn.execute(
        "SELECT name FROM clients WHERE id = ?", (client_id,)
    ).fetchone()

    if not client:
        flash("Client not found.", "error")
        conn.close()
        return redirect(url_for("index"))

    week = request.form.get("week", datetime.now().strftime("Week %U - %Y"))
    adherence = request.form.get("adherence", type=int, default=0)

    conn.execute(
        "INSERT INTO progress (client_name, week, adherence) VALUES (?, ?, ?)",
        (client["name"], week, adherence),
    )
    conn.commit()
    conn.close()
    flash("Progress logged successfully.", "success")
    return redirect(url_for("client_detail", client_id=client_id))


@app.route("/client/<int:client_id>/workout", methods=["POST"])
def add_workout(client_id):
    """Log a workout session for a client."""
    conn = get_db()
    client = conn.execute(
        "SELECT name FROM clients WHERE id = ?", (client_id,)
    ).fetchone()

    if not client:
        flash("Client not found.", "error")
        conn.close()
        return redirect(url_for("index"))

    workout_date = request.form.get("date", date.today().isoformat())
    workout_type = request.form.get("workout_type", "")
    duration = request.form.get("duration", type=int, default=60)
    notes = request.form.get("notes", "")

    conn.execute(
        """INSERT INTO workouts
           (client_name, date, workout_type, duration_min, notes)
           VALUES (?, ?, ?, ?, ?)""",
        (client["name"], workout_date, workout_type, duration, notes),
    )
    conn.commit()
    conn.close()
    flash("Workout logged successfully.", "success")
    return redirect(url_for("client_detail", client_id=client_id))


@app.route("/client/<int:client_id>/metrics", methods=["POST"])
def add_metrics(client_id):
    """Log body metrics for a client."""
    conn = get_db()
    client = conn.execute(
        "SELECT name FROM clients WHERE id = ?", (client_id,)
    ).fetchone()

    if not client:
        flash("Client not found.", "error")
        conn.close()
        return redirect(url_for("index"))

    metric_date = request.form.get("date", date.today().isoformat())
    weight = request.form.get("weight", type=float)
    waist = request.form.get("waist", type=float)
    bodyfat = request.form.get("bodyfat", type=float)

    conn.execute(
        """INSERT INTO metrics
           (client_name, date, weight, waist, bodyfat)
           VALUES (?, ?, ?, ?, ?)""",
        (client["name"], metric_date, weight, waist, bodyfat),
    )
    conn.commit()
    conn.close()
    flash("Metrics logged successfully.", "success")
    return redirect(url_for("client_detail", client_id=client_id))


# ---- API Endpoints ----

@app.route("/api/programs")
def api_programs():
    """Return all available fitness programs as JSON."""
    return jsonify(PROGRAMS)


@app.route("/api/clients")
def api_clients():
    """Return all clients as JSON."""
    conn = get_db()
    clients = conn.execute("SELECT * FROM clients ORDER BY name").fetchall()
    conn.close()
    return jsonify([dict(c) for c in clients])


@app.route("/api/client/<int:client_id>/bmi")
def api_bmi(client_id):
    """Return BMI info for a client."""
    conn = get_db()
    client = conn.execute(
        "SELECT weight, height FROM clients WHERE id = ?", (client_id,)
    ).fetchone()
    conn.close()

    if not client:
        return jsonify({"error": "Client not found"}), 404

    bmi, category = calculate_bmi(client["weight"], client["height"])
    return jsonify({"bmi": bmi, "category": category})


@app.route("/health")
def health():
    """Health check endpoint for CI/CD pipelines."""
    return jsonify({"status": "healthy", "app": "ACEest Fitness & Gym"})


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
