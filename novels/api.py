"""
External API services for novels app
"""

import requests
import json
from docwn import settings
from django.utils.translation import gettext_lazy as _


class ImgBBAPI:
    """Handle image uploads to ImgBB service"""

    BASE_URL = "https://api.imgbb.com/1/upload"

    @classmethod
    def upload_image(cls, image_file):
        """
        Upload image to ImgBB and return the URL

        Args:
            image_file: Django UploadedFile object

        Returns:
            str: Image URL if successful, None if failed
        """
        try:
            api_key = getattr(settings, "IMGBB_API_KEY", None)
            if not api_key:
                print("Warning: IMGBB_API_KEY not found in settings")
                return None

            response = requests.post(
                cls.BASE_URL,
                params={"key": api_key},
                files={"image": image_file},
                timeout=30,
            )

            print(f"ImgBB Response Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                return data["data"]["image"]["url"]
            else:
                print(
                    f"ImgBB API Error: {response.status_code} - {response.text}"
                )
                return None

        except requests.exceptions.RequestException as e:
            print(f"Request error uploading to ImgBB: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error uploading to ImgBB: {e}")
            return None

    @classmethod
    def is_configured(cls):
        """Check if ImgBB API is properly configured"""
        return bool(getattr(settings, "IMGBB_API_KEY", None))


class ExternalAPIManager:
    """Manager for all external API services"""

    @staticmethod
    def upload_image(image_file):
        """Upload image using the configured image service"""
        return ImgBBAPI.upload_image(image_file)

    @staticmethod
    def is_image_service_available():
        """Check if image upload service is available"""
        return ImgBBAPI.is_configured()
