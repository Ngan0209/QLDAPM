import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv

load_dotenv()
print(os.getenv("CLOUDINARY_NAME"))
print(os.getenv("CLOUDINARY_API_KEY"))
print(os.getenv("CLOUDINARY_API_SECRET"))
      
cloudinary.config(
    
    cloud_name=os.getenv("CLOUDINARY_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)




def upload_avatar(file):
    try:
        upload_result = cloudinary.uploader.upload(
            file,
            folder="avatars", 
            resource_type="auto"
        )
        return upload_result.get("secure_url") 
    except Exception as e:
        raise e