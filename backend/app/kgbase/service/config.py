import os

from dotenv import load_dotenv

load_dotenv()

BACKEND_BASE_URL = os.getenv('BACKEND_BASE_URL')
