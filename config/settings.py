import os
from dotenv import load_dotenv

load_dotenv()

DATA_PATH = os.getenv("DATA_PATH", "data/test.csv")

CACHE_HOST = os.getenv("CACHE_HOST", "localhost")
CACHE_PORT = int(os.getenv("CACHE_PORT", "6379"))
CACHE_DB = int(os.getenv("CACHE_DB", "0"))
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "3600"))
CACHE_POLICY = os.getenv("CACHE_POLICY", "LRU")
CACHE_MAX_SIZE = int(os.getenv("CACHE_MAX_SIZE", "10000"))

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "OLLAMA")  

# Gemini (Google)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.0-flash-exp")

# Ollama (Local)
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "llama3.2")  

# Groq 
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL_NAME = os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile")

DB_TYPE = os.getenv("DB_TYPE", "SQLITE")
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "data/results.db")

# POSTGRES_DB_USER = os.getenv("POSTGRES_DB_USER")
# POSTGRES_DB_PASSWORD = os.getenv("POSTGRES_DB_PASSWORD")
# POSTGRES_DB_HOST = os.getenv("POSTGRES_DB_HOST")
# POSTGRES_DB_PORT = int(os.getenv("POSTGRES_DB_PORT", "5432"))
# POSTGRES_DB_NAME = os.getenv("POSTGRES_DB_NAME")

TRAFFIC_DISTRIBUTION_TYPE = os.getenv("TRAFFIC_DISTRIBUTION_TYPE", "POISSON")
TRAFFIC_LAMBDA = float(os.getenv("TRAFFIC_LAMBDA", "0.1"))
TRAFFIC_NUM_REQUESTS = int(os.getenv("TRAFFIC_NUM_REQUESTS", "50"))
TRAFFIC_MAX_DELAY_SECONDS = int(os.getenv("TRAFFIC_MAX_DELAY_SECONDS", "20"))
