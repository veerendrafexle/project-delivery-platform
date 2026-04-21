import os

from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("MODEL", "mistral")
DATA_PATH = os.getenv("DATA_PATH", "data/")
INPUT_PATH = os.getenv("INPUT_PATH", "inputs/")
OUTPUT_PATH = os.getenv("OUTPUT_PATH", "outputs/")
LOCAL_LLM_URL = os.getenv("LOCAL_LLM_URL", "http://localhost:11434/api/generate")
API_URL = os.getenv("OPENROUTER_API_URL")
API_KEY = os.getenv("OPENROUTER_API_KEY")

SALESFORCE_CLIENT_ID = os.getenv("SALESFORCE_CLIENT_ID")
SALESFORCE_CLIENT_SECRET = os.getenv("SALESFORCE_CLIENT_SECRET")
SALESFORCE_USERNAME = os.getenv("SALESFORCE_USERNAME")
SALESFORCE_PASSWORD = os.getenv("SALESFORCE_PASSWORD")

JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_DOMAIN = os.getenv("JIRA_DOMAIN")
