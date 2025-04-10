# Grade Checker

Grade Checker is a Flask-based web application designed to fetch and display upcoming and missing assignments from the Canvas Learning Management System for a specified student. The application provides a user-friendly interface to view assignments across multiple courses, with a secure login system to protect access.

## Features

- Displays upcoming assignments due within the next 7 days.
- Lists missing assignments from the past 2 weeks.
- Supports multiple courses, with course names configurable via environment variables.
- Includes a secure login system with session management.
- Mobile-friendly design for easy access on smartphones.

## Prerequisites

Before running the application, ensure you have the following installed:

- Python 3.6 or higher
- `pip` (Python package manager)
- A Canvas API token with observer access to the student’s data

## Setup Instructions

### 1. Clone the Repository

Clone this repository to your local machine:

```bash
git clone https://github.com/your-username/grade_checker.git
cd grade_checker
Replace your-username with your GitHub username.
```

### 2. Install Dependencies

Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```
The requirements.txt file includes the following dependencies:

- requests
- python-dotenv
- flask
- flask-login

### 3. Configure Environment Variables

Create a .env file in the project root directory to store sensitive configuration details. Use the following template:

```plaintext
CANVAS_API_TOKEN=your-canvas-api-token
CANVAS_URL=https://your-canvas-instance.instructure.com
COURSE_IDS=comma-separated-course-ids
STUDENT_ID=student-id
COURSE_NAMES='{"course_id_1": "Course Name 1", "course_id_2": "Course Name 2"}'
USERS='{"username1": "password1", "username2": "password2"}'
APP_SECRET_KEY=your-random-secret-key
```

- CANVAS_API_TOKEN: Your Canvas API token with observer access.
- CANVAS_URL: The base URL of your Canvas instance (e.g., https://school.instructure.com).
- COURSE_IDS: A comma-separated list of course IDs to monitor (e.g., 4559,4579,4531).
- STUDENT_ID: The Canvas ID of the student whose assignments are being checked.
- COURSE_NAMES: A JSON string mapping course IDs to their names (e.g., {"4559": "Algebra II", "4579": "Chemistry"}).
- USERS: A JSON string defining the usernames and passwords for authorized users (e.g., {"user1": "securepassword1", "user2": "securepassword2"}).
- APP_SECRET_KEY: A random, secure key for Flask session management (e.g., generate with python -c "import secrets; print(secrets.token_hex(16))").

### 4. Run the Application Locally

Start the Flask application:

```bash
python canvas_scraper.py
```

The app will run on http://127.0.0.1:5000 by default. Open this URL in your browser to access the login page.

### 5. Log In

Use the credentials defined in the USERS environment variable to log in. Upon successful login, you will be redirected to the main page, which displays upcoming and missing assignments for the configured courses.

## Project Structure

- canvas_scraper.py: The main Flask application script.
- templates/: Directory containing HTML templates.
    - login.html: The login page template.
    - index.html: The main page template displaying assignments.
- requirements.txt: List of Python dependencies.
- .env: Environment variable file (not included in version control).
- .gitignore: Git ignore file to exclude sensitive files like .env.

