from abc import ABC, abstractmethod
from io import BytesIO

from time import sleep
from typing import List

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from webdriver_manager.firefox import GeckoDriverManager

from utils.config import Settings
from utils.logger import logger
from utils.utils import download_images


class ImageSearcher(ABC):
    HOST = "https://yandex.ru/images/"
    IMAGES = (By.XPATH, "(//div[contains(@role, 'listitem')])")
    MODAL_IMAGE = (By.XPATH, "//a[contains(@class, 'MMViewerButtons-OpenImage')]")
    MODAL_IMAGE_SRC_ATTR = "href"

    def __init__(self, _env_file=''):
        settings = Settings(_env_file=_env_file)
        self.IMAGES_COUNT = settings.IMAGES_COUNT

        if settings.WEBDRIVER == "CHROMIUM":
            self.DriverManager = ChromeDriverManager(chrome_type=ChromeType.CHROMIUM)
            self.options = webdriver.ChromeOptions()
            self.web_driver = webdriver.Chrome
        elif settings.WEBDRIVER == "CHROME":
            self.DriverManager = ChromeDriverManager()
            self.options = webdriver.ChromeOptions()
            self.web_driver = webdriver.Chrome
        else:
            self.DriverManager = GeckoDriverManager()
            self.options = webdriver.FirefoxOptions()
            self.web_driver = webdriver.Firefox

        self.service = Service(executable_path=self.DriverManager.install())

        self.options.add_argument(f"--disable-blink-features={settings.DISABLE_BLINK_FEATURES}")
        self.options.add_argument(f"--user-agent={settings.USER_AGENT}")
        self.options.add_argument(f"--window-size={settings.WINDOW_SIZE}")
        self.options.page_load_strategy = settings.LOAD_STRATEGY
        if settings.NO_SANDBOX:
            self.options.add_argument(f"--no-sandbox")
        if settings.DISABLE_DEV_SHM_USAGE:
            self.options.add_argument(f"--disable-dev-shm-usage")
        if settings.HEADLESS:
            self.options.add_argument("--headless")
        if settings.DISABLE_CACHE:
            self.options.add_argument("--disable-cache")

    def initialize_driver(self) -> WebDriver:
        """Initializing and configuring the web browser driver."""
        logger.info("Initializing web driver")
        return self.web_driver(service=self.service, options=self.options)

    def yandex_image_search(self, request: str):
        """The main method for performing image search on Yandex and extracting their URLs."""
        logger.info(f"Starting Yandex image search, request: {request}")
        with self.initialize_driver() as driver:
            driver.implicitly_wait(5)
            self.search_images(driver, request)
            images = self.extract_image_urls(driver)
        logger.info(f"Finished Yandex image search, request: {request}")
        return images

    def extract_image_urls(self, driver: WebDriver) -> List[str]:
        """Extracting image URLs from search results."""
        logger.info(f"Extracting image URLs, count: {self.IMAGES_COUNT}")
        images: List[str] = []
        image_elements = driver.find_elements(*self.IMAGES)
        for i in range(self.IMAGES_COUNT):
            image_elements[i].click()
            sleep(0.2)

            image_element = driver.find_element(*self.MODAL_IMAGE)
            images.append(image_element.get_attribute(self.MODAL_IMAGE_SRC_ATTR))

            driver.back()
            sleep(0.2)

        return images

    @abstractmethod
    def search_images(self, driver: WebDriver, request: str) -> None:
        """
        Searches for images on Yandex using the specified request.

        This method must be redefined in subclasses to perform specific search logic.

        Parameters:
        - driver: WebDriver, an instance of the web driver used to interact with the browser.
        - request: str, a request to search for images.
                    In the context of a text search, this will be a query string.
                    In the context of image search, this may be the path to the image file.

        Returns:
        - None, because the method must modify the state of the web driver by performing a search and
            redirecting the user to the search results.
        """
        pass

    def search_and_download_images(self, request: str) -> List[BytesIO]:
        """Asynchronously downloads images based on a search request using Yandex image search."""
        logger.info(f"Search images on request: {request}")
        image_links: List[str] = self.yandex_image_search(request)
        downloaded_images: List[BytesIO] = download_images(image_links)
        return downloaded_images


class QueryImageSearcher(ImageSearcher):
    INPUT_TEXT = (By.XPATH, "(//input[@type='text'])[1]")
    SUBMIT = (By.XPATH, "(//button[contains(@class, 'websearch-button')])[1]/div[3]")

    @staticmethod
    def slow_type(element: WebElement, text: str, delay: float = 0.2) -> None:
        """Slow text input with a delay between characters."""
        for char in text:
            element.send_keys(char)
            sleep(delay)

    def search_images(self, driver: WebDriver, request: str) -> None:
        """Performing image search on Yandex using the specified query."""
        logger.info(f"Searching images on Yandex: {request}")
        driver.get(self.HOST)

        input_text = driver.find_element(*self.INPUT_TEXT)
        self.slow_type(input_text, request)

        submit_elem = driver.find_element(*self.SUBMIT)
        submit_elem.click()
        sleep(1)


class ImageFileImageSearcher(ImageSearcher):
    INPUT_FILE = (By.XPATH, "(//input[contains(@type, 'file')])[1]")
    MORE_BUTTON = (By.XPATH, "(//a[contains(@class, 'CbirSimilar-MoreButton')])")

    def search_images(self, driver: WebDriver, request: str) -> None:
        """Performing image search on Yandex using the photo."""
        logger.info(f"Searching images on Yandex, photo: {request}")
        driver.get(self.HOST)

        input_file = driver.find_element(*self.INPUT_FILE)
        input_file.send_keys(request)
        sleep(0.5)

        more_button = driver.find_element(*self.MORE_BUTTON)
        more_button.click()
        sleep(2)
