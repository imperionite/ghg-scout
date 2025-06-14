from fastapi import FastAPI, HTTPException, Request, Depends, Path, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from uuid import uuid4
from hashlib import sha256
from typing import Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="GHG Scout PH - Auth API")

origins = [
    "http://localhost:3000",
    "https://ghg-scout-ph.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client.ghg_scout

# ----------------------- MODELS -----------------------

class UserRegistration(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)
    community_type: str = Field(..., pattern="^(LGU|School|University)$")
    community_name: str
    region: Optional[str] = None
    city: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserInfo(BaseModel):
    id: str
    username: str
    community_type: str
    community_name: str
    region: Optional[str] = None
    city: Optional[str] = None

class TokenResponse(BaseModel):
    token: str
    user: UserInfo

class UserUpdate(BaseModel):
    community_type: Optional[str] = None
    community_name: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None

    class Config:
        extra = "forbid"

# ----------------------- UTILITY FUNCTIONS -----------------------

def hash_password(password: str) -> str:
    return sha256(password.encode()).hexdigest()

def verify_password(raw_password: str, hashed: str) -> bool:
    return hash_password(raw_password) == hashed

async def get_current_user(request: Request):
    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token format")

    token_value = token.split(" ")[1]
    token_doc = await db.tokens.find_one({"token": token_value})
    if not token_doc:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await db.users.find_one({"username": token_doc["username"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

# ----------------------- ROUTES -----------------------

@app.post("/api/register", response_model=TokenResponse, status_code=201)
async def register(user: UserRegistration):
    if await db.users.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already exists")

    user_doc = {
        "username": user.username,
        "password": hash_password(user.password),
        "community_type": user.community_type,
        "community_name": user.community_name,
        "region": user.region,
        "city": user.city,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    result = await db.users.insert_one(user_doc)
    new_user = await db.users.find_one({"_id": result.inserted_id})

    token = str(uuid4())
    await db.tokens.insert_one({"token": token, "username": user.username})

    return TokenResponse(
        token=token,
        user=UserInfo(
            id=str(new_user["_id"]),
            username=new_user["username"],
            community_type=new_user["community_type"],
            community_name=new_user["community_name"],
            region=new_user.get("region"),
            city=new_user.get("city")
        )
    )

@app.post("/api/login", response_model=TokenResponse)
async def login(login_data: UserLogin):
    user = await db.users.find_one({"username": login_data.username})
    if not user or not verify_password(login_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = str(uuid4())
    await db.tokens.insert_one({"token": token, "username": login_data.username})

    return TokenResponse(
        token=token,
        user=UserInfo(
            id=str(user["_id"]),
            username=user["username"],
            community_type=user["community_type"],
            community_name=user["community_name"],
            region=user.get("region"),
            city=user.get("city")
        )
    )

@app.get("/api/me", response_model=UserInfo)
async def get_user_info(current_user=Depends(get_current_user)):
    return UserInfo(
        id=str(current_user["_id"]),
        username=current_user["username"],
        community_type=current_user["community_type"],
        community_name=current_user["community_name"],
        region=current_user.get("region"),
        city=current_user.get("city")
    )

@app.patch("/api/user/{user_id}")
async def update_user(user_id: str, update: UserUpdate, current_user=Depends(get_current_user)):
    try:
        object_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    if str(current_user["_id"]) != user_id:
        raise HTTPException(status_code=403, detail="You can only update your own account")

    updated_fields = {k: v for k, v in update.dict(exclude_unset=True).items() if v is not None}
    updated_fields["updated_at"] = datetime.utcnow()

    result = await db.users.update_one({"_id": object_id}, {"$set": updated_fields})
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="No changes applied")

    return {"message": "User updated successfully"}

@app.delete("/api/user/{user_id}")
async def delete_user(user_id: str, current_user=Depends(get_current_user)):
    try:
        object_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    if str(current_user["_id"]) != user_id:
        raise HTTPException(status_code=403, detail="You can only delete your own account")

    result = await db.users.delete_one({"_id": object_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    # Optionally delete the token too
    await db.tokens.delete_many({"username": current_user["username"]})

    return {"message": "User deleted successfully"}
