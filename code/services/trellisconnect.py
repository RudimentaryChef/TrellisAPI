import os
import requests
from dotenv import load_dotenv


class TrellisAPIClient:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        self.api_key = os.getenv("TRELLIS_API_KEY")
        if not self.api_key:
            raise ValueError("The environment variable TRELLIS_API_KEY is not set.")
        self.headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }
        self.base_url = "https://api.runtrellis.com/v1"
        self.project_id = None
        self.transform_id = None

    def create_project(self, project_name):
        url = f"{self.base_url}/projects/create"
        payload = {"name": project_name}
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            self.project_id = response.json().get("data", {}).get("proj_id")
            if not self.project_id:
                raise ValueError("Failed to retrieve 'proj_id' from the project creation response.")
            print(f"Project created with ID: {self.project_id}")
        except requests.exceptions.RequestException as exception:
            print(f"Error creating project: {exception}")
            raise

    def create_transform(self, transform_name, transform_parameters):
        if not self.project_id:
            raise ValueError("The project ID is not set. Please create a project first.")
        url = f"{self.base_url}/transforms/create"
        payload = {
            "proj_id": self.project_id,
            "transform_name": transform_name,
            "transform_params": transform_parameters
        }
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            self.transform_id = response.json().get("data", {}).get("transform_id")
            if not self.transform_id:
                raise ValueError("Failed to retrieve 'transform_id' from the transform creation response.")
            print(f"Transform created with ID: {self.transform_id}")
        except requests.exceptions.RequestException as exception:
            print(f"Error creating transform: {exception}")
            raise

    def create_event_subscriptions(self):
        if not self.project_id or not self.transform_id:
            raise ValueError("The project ID or transform ID is not set. Ensure both are created.")
        url = f"{self.base_url}/events/subscriptions/actions/bulk"
        payload = {
            "events_with_actions": [
                {
                    "event_type": "asset_uploaded",
                    "proj_id": self.project_id,
                    "actions": [
                        {"type": "run_extraction", "proj_id": self.project_id}
                    ],
                },
                {
                    "event_type": "asset_extracted",
                    "proj_id": self.project_id,
                    "actions": [
                        {"type": "refresh_transform", "transform_id": self.transform_id}
                    ]
                }
            ]
        }
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            print("Event subscriptions created successfully.")
        except requests.exceptions.RequestException as exception:
            print(f"Error creating event subscriptions: {exception}")
            raise

    def upload_assets(self, asset_urls):
        if not self.project_id:
            raise ValueError("The project ID is not set. Please create a project first.")
        url = f"{self.base_url}/assets/upload"
        payload = {
            "proj_id": self.project_id,
            "urls": asset_urls
        }
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            asset_ids = [data["asset_id"] for data in response.json()["data"]]
            print(f"Assets uploaded with IDs: {asset_ids}")
        except requests.exceptions.RequestException as exception:
            print(f"Error uploading assets: {exception}")
            raise


if __name__ == "__main__":
    # Example usage
    trellis_client = TrellisAPIClient()

    # Create a project
    project_name = "InterviewProject"
    trellis_client.create_project(project_name)

    # Define transform parameters
    transform_parameters = {
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
                "column_type": "numeric",
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
                "column_type": "numeric",
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
    trellis_client.create_transform("course_analysis", transform_parameters)

    # Create event subscriptions
    trellis_client.create_event_subscriptions()

    # Upload assets
    asset_urls = ["https://storage.googleapis.com/imagestorageclasshopper/UmangFlyer.png"]
    trellis_client.upload_assets(asset_urls)
