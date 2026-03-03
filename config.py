import os
from dotenv import load_dotenv

load_dotenv()

# TinyFish Configuration
TINYFISH_API_KEY = os.getenv("TINYFISH_API_KEY")
TINYFISH_API_BASE_URL = "https://agent.tinyfish.ai/v1" # Correct domain
TINYFISH_BULK_TIMEOUT = 300  # 5 minutes for bulk requests

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "google")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4-turbo")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Output Configuration
OUTPUT_DIR = "./output"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
