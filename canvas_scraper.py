import requests
import datetime
import os
from dotenv import load_dotenv
import json
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# Load environment variables from .env file
load_dotenv()

# Flask app setup
app = Flask(__name__)
app.secret_key = "supersecretkey123"  # Change this to a random string for production

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, username):
        self.id = username
        self.username = username

# Hardcoded users (you and her mama)
users = {
    "justin": "password123",  # Change these to secure passwords
    "mama": "password456"
}

@login_manager.user_loader
def load_user(username):
    if username in users:
        return User(username)
    return None

# Canvas API configuration
token = os.getenv("CANVAS_API_TOKEN")
canvas_url = os.getenv("CANVAS_URL")
course_ids = os.getenv("COURSE_IDS").split(",")
student_id = os.getenv("STUDENT_ID")
headers = {"Authorization": f"Bearer {token}"}
course_names = json.loads(os.getenv("COURSE_NAMES"))

# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        if username in users and users[username] == password:
            user = User(username)
            login_user(user, remember=True)  # Set cookie to remember user
            flash("Logged in successfully!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password", "error")
    
    return render_template("login.html")

# Logout route
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect(url_for("login"))

# Main route to display assignments
@app.route("/")
@login_required
def index():
    # Today’s date and time windows (UTC for Canvas)
    today = datetime.datetime.now(datetime.timezone.utc)
    next_week = today + datetime.timedelta(days=7)
    two_weeks_ago = today - datetime.timedelta(days=14)
    
    courses = []
    for course_id in course_ids:
        course_name = course_names.get(course_id, f"Course {course_id}")
        course_data = {"name": course_name, "upcoming": [], "missing": []}
        
        # Fetch upcoming assignments using ?bucket=upcoming
        has_upcoming = False
        upcoming_url = f"{canvas_url}/api/v1/courses/{course_id}/assignments?bucket=upcoming"
        try:
            upcoming_response = requests.get(upcoming_url, headers=headers)
            upcoming_response.raise_for_status()
            upcoming_assignments = upcoming_response.json()
        except requests.exceptions.RequestException as e:
            course_data["upcoming"].append(f"Error fetching upcoming assignments: {e}")
            upcoming_assignments = []

        if not isinstance(upcoming_assignments, list):
            course_data["upcoming"].append("Something’s funky with the API for upcoming assignments—check your token or course ID!")
        else:
            for assignment in upcoming_assignments:
                due_date = assignment.get("due_at")
                if not due_date:
                    continue

                try:
                    due = datetime.datetime.strptime(due_date, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
                except ValueError:
                    continue

                if today <= due <= next_week:
                    sub_url = f"{canvas_url}/api/v1/courses/{course_id}/assignments/{assignment['id']}/submissions/{student_id}"
                    try:
                        sub_response = requests.get(sub_url, headers=headers)
                        sub_response.raise_for_status()
                        submission = sub_response.json()
                        submitted = submission.get("submitted_at") is not None
                    except requests.exceptions.RequestException as e:
                        submitted = False

                    status = " (Submitted)" if submitted else " (Not Submitted)"
                    course_data["upcoming"].append(f"- {assignment['name']} (Due: {due.strftime('%Y-%m-%d %H:%M')}{status})")
                    has_upcoming = True

            if not has_upcoming:
                course_data["upcoming"].append("None coming up—smooth sailing ahead!")

        # Fetch unsubmitted, past-due assignments using ?bucket=unsubmitted
        has_missing = False
        unsubmitted_url = f"{canvas_url}/api/v1/courses/{course_id}/assignments?bucket=unsubmitted"
        try:
            unsubmitted_response = requests.get(unsubmitted_url, headers=headers)
            unsubmitted_response.raise_for_status()
            unsubmitted_assignments = unsubmitted_response.json()
        except requests.exceptions.RequestException as e:
            course_data["missing"].append(f"Error fetching unsubmitted assignments: {e}")
            unsubmitted_assignments = []

        if not isinstance(unsubmitted_assignments, list):
            course_data["missing"].append("Something’s funky with the API for unsubmitted assignments—check your token or course ID!")
        else:
            for assignment in unsubmitted_assignments:
                due_date = assignment.get("due_at")
                if not due_date:
                    continue

                try:
                    due = datetime.datetime.strptime(due_date, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
                except ValueError:
                    continue

                if two_weeks_ago <= due < today:
                    course_data["missing"].append(f"- {assignment['name']} (Due: {due.strftime('%Y-%m-%d %H:%M')})")
                    has_missing = True

            if not has_missing:
                course_data["missing"].append("No missing assignments in the last 2 weeks!(sigh of relief)")

        courses.append(course_data)

    return render_template("index.html", courses=courses, today=today.strftime('%Y-%m-%d %H:%M'), next_week=next_week.strftime('%Y-%m-%d %H:%M'), two_weeks_ago=two_weeks_ago.strftime('%Y-%m-%d %H:%M'))

if __name__ == "__main__":
    app.run(debug=True)