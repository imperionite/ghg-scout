import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.auth import router as auth_router
from routes import ghg
from dotenv import load_dotenv

load_dotenv()


app = FastAPI(title="GHG Scout PH - API")

origins_str = os.getenv("ORIGINS", "[]")  # Default to empty list string if not set
origins = json.loads(origins_str)  # Convert JSON string to list

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(ghg.router, prefix="/api/ghg", tags=["GHG"])
