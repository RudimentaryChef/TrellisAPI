from fastapi import APIRouter, UploadFile
from code.services.trellis_service import TrellisService
from code.services.gcp_service import GCPService
from code.utilities.poster_generator import generate_poster

router = APIRouter()

@router.post("/upload/")
async def upload_file(file: UploadFile):
    # Step 1: Process file with Trellis API
    trellis_service = TrellisService()
    trellis_response = trellis_service.upload_file(file)

    # Step 2: Generate a poster
    poster_path = generate_poster(trellis_response["data"])

    # Step 3: Upload poster to GCP
    gcp_service = GCPService()
    gcp_url = gcp_service.upload_file(poster_path)

    return {"message": "Poster generated and uploaded successfully", "url": gcp_url}
