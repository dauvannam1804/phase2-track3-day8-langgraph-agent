from dotenv import load_dotenv
import os

# Load .env file at the package level to ensure LangSmith tracing and other 
# environment variables are available to all modules.
load_dotenv()
