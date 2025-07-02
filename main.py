import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from contextlib import asynccontextmanager

from routes.auth import router as auth_router
from routes import ghg

load_dotenv()

# Lifespan event for startup and shutdown tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
    yield
    # Shutdown


# Create app with lifespan
app = FastAPI(title="GHG Scout PH - API", lifespan=lifespan)

# CORS config
origins_str = os.getenv("ORIGINS", "[]")
origins = json.loads(origins_str)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(auth_router, prefix="/api")
app.include_router(ghg.router, prefix="/api/ghg", tags=["GHG"])
