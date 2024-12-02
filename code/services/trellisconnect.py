import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key
TRELLIS_API_KEY = os.getenv("TRELLIS_API_KEY")
if not TRELLIS_API_KEY:
    raise ValueError("TRELLIS_API_KEY environment variable is not set.")

# Set project name
YOUR_PROJ_NAME = "InterviewProject"

# Define headers
headers = {
    "Authorization":TRELLIS_API_KEY,
    "Content-Type": "application/json"
}

# Create a new project
project_url = "https://api.runtrellis.com/v1/projects/create"
project_payload = {"name": YOUR_PROJ_NAME}

try:
    project_response = requests.post(project_url, json=project_payload, headers=headers)
    project_response.raise_for_status()  # Raise an exception for HTTP errors
    proj_id = project_response.json().get("data", {}).get("proj_id")
    if not proj_id:
        raise ValueError("Failed to retrieve 'proj_id' from the project creation response.")
    print(f"Project ID: {proj_id}")
except requests.exceptions.RequestException as e:
    print(f"Error creating project: {e}")
    print(f"Response: {project_response.text}")
    raise

# Create a transform
transform_url = "https://api.runtrellis.com/v1/transforms/create"
transform_payload = {
    "proj_id": proj_id,
    "transform_name": "course_analysis",
    "transform_params": {
        "model": "trellis-premium",
        "mode": "document",
        "operations": [
            {
                "column_name": "course_name",
                "column_type": "text",
                "transform_type": "extraction",
                "task_description": "Extract the name of the course."
            },
            {
                "column_name": "course_description",
                "column_type": "text",
                "transform_type": "extraction",
                "task_description": "Extract the description of the course."
            },
            {
                "column_name": "course_tags",
                "column_type": "text[]",
                "transform_type": "extraction",
                "task_description": "Extract a list of tags associated with the course."
            },
            {
                "column_name": "is_online",
                "column_type": "boolean",
                "transform_type": "classification",
                "task_description": "Determine if the course is conducted online.",
                "output_values": {
                    "True": "The course is conducted online.",
                    "False": "The course is conducted in-person."
                }
            },
            {
                "column_name": "course_price",
                "column_type": "numeric",  # Corrected from "decimal"
                "transform_type": "extraction",
                "task_description": "Extract the price of the course."
            },
            {
                "column_name": "course_category",
                "column_type": "text",
                "transform_type": "classification",
                "task_description": "Classify the category of the course based on its description and tags.",
                "output_values": {
                    "Science": "Courses related to science topics.",
                    "Arts": "Courses in arts and humanities.",
                    "Technology": "Courses about technology and computing.",
                    "Business": "Courses on business and management.",
                    "Health": "Courses related to health and wellness.",
                    "Education": "Courses about education and teaching.",
                    "Sports": "Courses related to physical activities and sports.",
                    "Other": "Courses that do not fit into the above categories."
                }
            },
            {
                "column_name": "course_summary",
                "column_type": "text",
                "transform_type": "generation",
                "task_description": "Provide a concise summary of the course."
            },
            {
                "column_name": "course_rating",
                "column_type": "numeric",  # Corrected from "float"
                "transform_type": "extraction",
                "task_description": "Extract the rating of the course."
            },
            {
                "column_name": "emotional_tone",
                "column_type": "text",
                "transform_type": "classification",
                "task_description": "Identify the type of course.",
                "output_values": {
                    "Casual": "The course seems like it's casual recreational.",
                    "Serious": "The course seems for serious/competition level stuff."
                }
            }
        ]
    }
}

try:
    transform_response = requests.post(transform_url, json=transform_payload, headers=headers)
    transform_id = transform_response.json()["data"]["transform_id"]
    transform_response.raise_for_status()
    transform_data = transform_response.json()
    print(f"Transform creation response: {transform_data}")
except requests.exceptions.RequestException as e:
    print(f"Error creating transform: {e}")
    print(f"Response: {transform_response.text}")
    raise



url = f"https://api.runtrellis.com/v1/events/subscriptions/actions/bulk"
payload = { "events_with_actions": [
        {
            "event_type": "asset_uploaded",
            "proj_id": proj_id,
            "actions": [
                {
                    "type": "run_extraction",
                    "proj_id": proj_id
                }
            ],
        },
        {
            "event_type": "asset_extracted",
            "proj_id": proj_id,
            "actions": [
                {
                    "type": "refresh_transform",
                    "transform_id": transform_id
                }
            ]
        }
    ] }
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "Authorization": TRELLIS_API_KEY
}

response = requests.post(url, json=payload, headers=headers)

print(response.text)


