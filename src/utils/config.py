import os

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    class Config:
        env_file = '.env'

    TOKEN: str = os.getenv('TOKEN')

    WELCOME_MESSAGE: str = os.getenv("WELCOME_MESSAGE")

    IMAGES_COUNT: int = os.getenv("IMAGES_COUNT")

    WEBDRIVER: str = os.getenv("WEBDRIVER")
    LOAD_STRATEGY: str = os.getenv("LOAD_STRATEGY")
    WINDOW_SIZE: str = os.getenv("WINDOW_SIZE")
    DISABLE_CACHE: bool = os.getenv("DISABLE_CACHE")
    NO_SANDBOX: bool = os.getenv("NO_SANDBOX")
    DISABLE_DEV_SHM_USAGE: bool = os.getenv("DISABLE_DEV_SHM_USAGE")
    HEADLESS: bool = os.getenv("HEADLESS")
    DISABLE_BLINK_FEATURES: str = os.getenv("DISABLE_BLINK_FEATURES")
    USER_AGENT: str = os.getenv("USER_AGENT")
