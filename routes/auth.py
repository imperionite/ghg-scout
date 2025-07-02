from fastapi import APIRouter, HTTPException, Request, Depends
from bson.objectid import ObjectId
from datetime import datetime, timezone
from uuid import uuid4
from fastapi_cache import FastAPICache

from core.db import db
from models.schemas import *
from utils.security import hash_password, verify_password

router = APIRouter()


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


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(user: UserRegistration):
    if await db.users.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already exists")
    doc = user.dict(exclude={"password"})
    doc["password"] = hash_password(user.password)
    doc["created_at"] = doc["updated_at"] = datetime.now(timezone.utc)
    result = await db.users.insert_one(doc)
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
            city=new_user.get("city"),
        ),
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin):
    user = await db.users.find_one({"username": data.username})
    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Invalidate all cached data
    if FastAPICache.get_backend():
        await FastAPICache.clear()

    token = str(uuid4())
    await db.tokens.insert_one({"token": token, "username": data.username})
    return TokenResponse(
        token=token,
        user=UserInfo(
            id=str(user["_id"]),
            username=user["username"],
            community_type=user["community_type"],
            community_name=user["community_name"],
            region=user.get("region"),
            city=user.get("city"),
        ),
    )


@router.get("/me", response_model=UserInfo)
async def me(current_user=Depends(get_current_user)):
    return UserInfo(
        id=str(current_user["_id"]),
        username=current_user["username"],
        community_type=current_user["community_type"],
        community_name=current_user["community_name"],
        region=current_user.get("region"),
        city=current_user.get("city"),
    )


@router.patch("/user/{user_id}")
async def update_user(
    user_id: str, update: UserUpdate, current_user=Depends(get_current_user)
):
    if str(current_user["_id"]) != user_id:
        raise HTTPException(
            status_code=403, detail="You can only update your own account"
        )
    fields = {k: v for k, v in update.dict(exclude_unset=True).items()}
    fields["updated_at"] = datetime.now(timezone.utc)

    await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": fields})

    # Invalidate all cached data
    if FastAPICache.get_backend():
        await FastAPICache.clear()

    return {"message": "User updated successfully"}


@router.delete("/user/{user_id}")
async def delete_user(user_id: str, current_user=Depends(get_current_user)):
    if str(current_user["_id"]) != user_id:
        raise HTTPException(
            status_code=403, detail="You can only delete your own account"
        )
    await db.users.delete_one({"_id": ObjectId(user_id)})
    await db.tokens.delete_many({"username": current_user["username"]})

    # Invalidate all cached data
    if FastAPICache.get_backend():
        await FastAPICache.clear()

    return {"message": "User deleted successfully"}
