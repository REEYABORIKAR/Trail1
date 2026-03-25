from dotenv import load_dotenv
import os

# Step 1: Clean environment BEFORE any other imports
load_dotenv()
_key = os.environ.get("GOOGLE_API_KEY", "")
if hasattr(_key, "get_secret_value"):
    _key = _key.get_secret_value()
os.environ["GOOGLE_API_KEY"] = str(_key)

from fastapi import FastAPI
from app.api import rag, auth
from app.models.database import init_db

app = FastAPI()
app.include_router(auth.router)
app.include_router(rag.router)

@app.on_event("startup")
def startup():
    init_db()