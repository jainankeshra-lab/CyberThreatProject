import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

print("🔍 Loaded .env from:", env_path)
print("Environment variables loaded successfully")
