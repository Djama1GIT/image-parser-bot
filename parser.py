from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO

from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

from utils.config import settings
from utils.logger import logger
from utils.utils import download_image

IMAGES_COUNT = settings.IMAGES_COUNT

HOST = "https://yandex.ru/images/"
INPUT_TEXT = (By.XPATH, "(//input[@type='text'])[1]")
SUBMIT = (By.XPATH, "(//button[contains(@class, 'websearch-button')])[1]/div[3]")
IMAGES = (By.XPATH, "(//div[contains(@role, 'listitem')])")
MODAL_IMAGE = (By.XPATH, "//a[contains(@class, 'MMViewerButtons-OpenImage')]")
MODAL_IMAGE_SRC_ATTR = "href"

service = Service(executable_path=ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())

options = webdriver.ChromeOptions()
options.add_argument(f"--disable-blink-features={settings.DISABLE_BLINK_FEATURES}")
options.add_argument(f"--user-agent={settings.USER_AGENT}")
options.add_argument(f"--window-size={settings.WINDOW_SIZE}")
options.page_load_strategy = settings.LOAD_STRATEGY
if settings.HEADLESS:
    options.add_argument("--headless")
if settings.DISABLE_CACHE:
    options.add_argument("--disable-cache")


def yandex_image_search(query: str, count=IMAGES_COUNT) -> list[str]:
    with webdriver.Chrome(service=service, options=options) as driver:
        logger.info(f"Search images on query via Yandex: {query}")

        driver.implicitly_wait(5)
        driver.get(HOST)

        input_elem = driver.find_element(*INPUT_TEXT)
        input_elem.click()

        for char in query:
            input_elem.send_keys(char)
            sleep(0.2)

        submit_elem = driver.find_element(*SUBMIT)
        submit_elem.click()
        sleep(1)

        images: list[str] = []
        image_elements = driver.find_elements(*IMAGES)
        for i in range(count):
            image_elements[i].click()
            sleep(0.2)

            image_element = driver.find_element(*MODAL_IMAGE)
            images.append(image_element.get_attribute(MODAL_IMAGE_SRC_ATTR))

            driver.back()
            sleep(0.2)

        return images


def search_images(query: str) -> list[BytesIO]:
    logger.info(f"Search images on query: {query}")

    image_links: list[str] = yandex_image_search(query)

    downloaded_images: list[BytesIO] = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(download_image, url): url for url in image_links}
        for future in as_completed(future_to_url):
            downloaded_image = future.result()
            if downloaded_image is not None:
                downloaded_images.append(downloaded_image)

    return downloaded_images
