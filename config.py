import os

from dotenv import load_dotenv

load_dotenv()

SZURUBOORU_URL = os.getenv("SZURUBOORU_URL")
SZURUBOORU_USERNAME = os.getenv("SZURUBOORU_USERNAME")
SZURUBOORU_API_TOKEN = os.getenv("SZURUBOORU_API_TOKEN")
