import requests
import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Your Canvas Info
token = os.getenv("CANVAS_API_TOKEN")
canvas_url = os.getenv("CANVAS_URL")
course_ids = os.getenv("COURSE_IDS").split(",")
student_id = os.getenv("STUDENT_ID")
headers = {"Authorization": f"Bearer {token}"}

# Today’s date and time windows (UTC for Canvas)
today = datetime.datetime.now(datetime.timezone.utc)
next_week = today + datetime.timedelta(days=7)
two_weeks_ago = today - datetime.timedelta(days=14)
print(f"[INFO] Looking for upcoming assignments between {today.strftime('%Y-%m-%d %H:%M')} and {next_week.strftime('%Y-%m-%d %H:%M')} UTC")
print(f"[INFO] Looking for missing assignments between {two_weeks_ago.strftime('%Y-%m-%d %H:%M')} and {today.strftime('%Y-%m-%d %H:%M')} UTC")

# Course names for printing
course_names = {
    "4559": "Algebra II",
    "4579": "Chemistry",
    "4531": "English II",
    "4519": "Spanish II",
    "4900": "Classical Civilizations"
}

for course_id in course_ids:
    course_name = course_names.get(course_id, f"Course {course_id}")

    # Print the course header
    print(f"\n=== {course_name} ===")

    # Step 1: Fetch upcoming assignments using ?bucket=upcoming
    print("Upcoming Assignments (Next 7 Days):")
    has_upcoming = False
    upcoming_url = f"{canvas_url}/api/v1/courses/{course_id}/assignments?bucket=upcoming"
    try:
        upcoming_response = requests.get(upcoming_url, headers=headers)
        upcoming_response.raise_for_status()  # Raise an error if the request fails
        upcoming_assignments = upcoming_response.json()
    except requests.exceptions.RequestException as e:
        print(f"  Error fetching upcoming assignments: {e}")
        upcoming_assignments = []

    if not isinstance(upcoming_assignments, list):
        print("  Something’s funky with the API for upcoming assignments—check your token or course ID!")
    else:
        for assignment in upcoming_assignments:
            due_date = assignment.get("due_at")
            if not due_date:
                print(f"  [DEBUG] Skipped upcoming: {assignment['name']} (No due date)")
                continue

            try:
                due = datetime.datetime.strptime(due_date, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
            except ValueError:
                print(f"  [DEBUG] Skipped upcoming: {assignment['name']} (Invalid due date: {due_date})")
                continue

            # Only show if it’s in our 7-day window
            if today <= due <= next_week:
                # Check submission status
                sub_url = f"{canvas_url}/api/v1/courses/{course_id}/assignments/{assignment['id']}/submissions/{student_id}"
                try:
                    sub_response = requests.get(sub_url, headers=headers)
                    sub_response.raise_for_status()
                    submission = sub_response.json()
                    submitted = submission.get("submitted_at") is not None
                except requests.exceptions.RequestException as e:
                    print(f"  [DEBUG] Error checking submission for {assignment['name']}: {e}")
                    submitted = False  # Assume not submitted if we can’t check

                status = " (Submitted)" if submitted else " (Not Submitted)"
                print(f"- {assignment['name']} (Due: {due.strftime('%Y-%m-%d %H:%M')}{status})")
                has_upcoming = True
            else:
                print(f"  [DEBUG] Skipped upcoming: {assignment['name']} (Due: {due.strftime('%Y-%m-%d %H:%M')})")

        if not has_upcoming:
            print("  None coming up—smooth sailing ahead!")

    # Step 2: Fetch unsubmitted, past-due assignments using ?bucket=unsubmitted
    print("\nMissing Assignments (Past Due, Last 2 Weeks):")
    has_missing = False
    unsubmitted_url = f"{canvas_url}/api/v1/courses/{course_id}/assignments?bucket=unsubmitted"
    try:
        unsubmitted_response = requests.get(unsubmitted_url, headers=headers)
        unsubmitted_response.raise_for_status()
        unsubmitted_assignments = unsubmitted_response.json()
    except requests.exceptions.RequestException as e:
        print(f"  Error fetching unsubmitted assignments: {e}")
        unsubmitted_assignments = []

    if not isinstance(unsubmitted_assignments, list):
        print("  Something’s funky with the API for unsubmitted assignments—check your token or course ID!")
    else:
        for assignment in unsubmitted_assignments:
            due_date = assignment.get("due_at")
            if not due_date:
                continue  # Skip if no due date

            try:
                due = datetime.datetime.strptime(due_date, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
            except ValueError:
                continue  # Skip invalid dates

            # Only show if it’s in the last 2 weeks
            if two_weeks_ago <= due < today:
                print(f"- {assignment['name']} (Due: {due.strftime('%Y-%m-%d %H:%M')})")
                has_missing = True

        if not has_missing:
            print("  No missing assignments in the last 2 weeks!(sigh of relief)")
