import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_NAME"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET")
)

def upload_avatar(file):
    try:
        upload_result = cloudinary.uploader.upload(
            file,
            folder="avatars",   # tạo folder avatars trên cloudinary
            resource_type="auto"
        )
        return upload_result.get("secure_url")  # link ảnh https
    except Exception as e:
        raise e