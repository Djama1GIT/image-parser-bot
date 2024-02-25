from io import BytesIO

import requests

from .config import settings
from .logger import logger


def download_image(image_link):
    logger.info(f"Downloading image: {image_link}")
    try:
        response = requests.get(
            image_link,
            stream=True,
            headers={
                'User-Agent': settings.USER_AGENT,
            }
        )
        response.raise_for_status()
        image_data = BytesIO(response.content)
        return image_data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading the image: {image_link}. Error: {e}")
        return None
