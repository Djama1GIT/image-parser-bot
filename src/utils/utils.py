from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
from typing import List

import requests

from .config import Settings
from .logger import logger


def download_image(image_link: str) -> BytesIO | None:
    """Downloads an image from a given URL and returns it as a BytesIO object."""
    logger.info(f"Downloading image: {image_link}")
    settings = Settings()
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


def download_images(image_links: List[str]) -> List[BytesIO]:
    downloaded_images: List[BytesIO] = []

    with ThreadPoolExecutor() as executor:
        future_to_url = {executor.submit(download_image, url): url for url in image_links}
        for future in as_completed(future_to_url):
            downloaded_image = future.result()
            if downloaded_image is not None:
                downloaded_images.append(downloaded_image)

    return downloaded_images
