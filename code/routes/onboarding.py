from fastapi import APIRouter, UploadFile


router = APIRouter()

@router.post("/upload/")
async def upload_file(file: UploadFile):
    print("hi")

    return {"message": "Poster generated and uploaded successfully", "url": gcp_url}
