from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from supabase import create_client
import os
import uuid
from slowapi import Limiter
from fastapi import Request
from app.services.limiter import limiter 

router = APIRouter()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@router.post("/upload-image")
@limiter.limit("1/minute")
async def upload_image(request:Request, file: UploadFile = File(...)):
    file_ext = file.filename.split('.')[-1].lower()
    if file_ext not in ['jpg', 'jpeg', 'png']:
        raise HTTPException(status_code=400, detail="Only JPG or PNG images allowed")

    unique_filename = f"{uuid.uuid4()}.{file_ext}"
    file_content = await file.read()

    try:
        res = supabase.storage.from_("images").upload(
            unique_filename,
            file_content,
            {"content-type": file.content_type}
        )

        # Optional: check for error if returned
        if hasattr(res, "error") and res.error:
            raise HTTPException(status_code=500, detail=res.error.message)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    public_url = supabase.storage.from_("images").get_public_url(unique_filename)
    return {"message": "Image uploaded successfully", "image_url": public_url}
