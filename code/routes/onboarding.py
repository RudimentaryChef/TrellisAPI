from fastapi import APIRouter, UploadFile, HTTPException, Form
from typing import List
import shutil
from pathlib import Path
import os
from trellis_client import \
    TrellisAPIClient  # Assuming the TrellisAPIClient is in a separate file named trellis_client.py

router = APIRouter()

# Initialize TrellisAPIClient
trellis_client = TrellisAPIClient()

UPLOAD_FOLDER = "uploaded_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@router.post("/create_project/")
async def create_project(project_name: str = Form(...)):
    """
    Route to create a project.
    """
    try:
        trellis_client.create_project(project_name)
        return {"message": "Project created successfully", "project_id": trellis_client.project_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/create_transform/")
async def create_transform(
        transform_name: str = Form(...),
        transform_parameters: dict = Form(...)
):
    """
    Route to create a transform.
    """
    try:
        trellis_client.create_transform(transform_name, transform_parameters)
        return {"message": "Transform created successfully", "transform_id": trellis_client.transform_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/create_event_subscriptions/")
async def create_event_subscriptions():
    """
    Route to create event subscriptions.
    """
    try:
        trellis_client.create_event_subscriptions()
        return {"message": "Event subscriptions created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/upload/")
async def upload_file(file: UploadFile):
    """
    Route to upload a file and use TrellisAPIClient to upload assets.
    """
    try:
        # Save uploaded file locally
        file_path = Path(UPLOAD_FOLDER) / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Simulate asset URL generation (replace this with actual URL generation logic if available)
        gcp_url = f"https://storage.googleapis.com/fake-bucket/{file.filename}"

        # Upload assets via TrellisAPIClient
        trellis_client.upload_assets([gcp_url])

        return {"message": "File uploaded and assets created successfully", "file_url": gcp_url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/project_info/")
async def get_project_info():
    """
    Route to fetch current project and transform IDs.
    """
    if not trellis_client.project_id:
        raise HTTPException(status_code=404, detail="No project ID found. Create a project first.")
    if not trellis_client.transform_id:
        raise HTTPException(status_code=404, detail="No transform ID found. Create a transform first.")
    return {
        "project_id": trellis_client.project_id,
        "transform_id": trellis_client.transform_id
    }


@router.post("/upload_assets/")
async def upload_assets(asset_urls: List[str]):
    """
    Route to upload multiple asset URLs.
    """
    try:
        trellis_client.upload_assets(asset_urls)
        return {"message": "Assets uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
