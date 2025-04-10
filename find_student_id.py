import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Your parent token and Canvas URL
token = os.getenv("CANVAS_API_TOKEN")
canvas_url = os.getenv("CANVAS_URL")
headers = {"Authorization": f"Bearer {token}"}

# Fetch the list of students you're observing
url = f"{canvas_url}/api/v1/users/self/observees"
response = requests.get(url, headers=headers)
observees = response.json()

# Print their names and IDs
for observee in observees:
    print(f"Name: {observee['name']}, ID: {observee['id']}")
