import os
from dotenv import load_dotenv

# Config starts here


# Load from .env file
load_dotenv()

# Assign Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")