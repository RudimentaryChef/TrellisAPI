from dotenv import load_dotenv
import os
load_dotenv()

# Access environment variables
TRELLIS_API_KEY = os.getenv("TRELLIS_API_KEY")
DB_USERNAME = os.getenv("DATABASE_USER")
DB_PASSWORD = os.getenv("DATABASE_PASSWORDI")

print(f"Trellis API Key: {TRELLIS_API_KEY}")
print(f"Database User: {DB_USERNAME}")
from fastapi import FastAPI
from routes import onboarding  # Example route module

# Initialize the FastAPI app
app = FastAPI()

# Include routes
app.include_router(onboarding.router, prefix="/onboarding", tags=["Onboarding"])
