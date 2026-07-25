from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from bson import ObjectId
from typing import Optional
from database import db

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    phonenumber: Optional[str] = ""
    address: Optional[str] = ""

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    phonenumber: Optional[str] = None
    address: Optional[str] = None
    password: Optional[str] = None

@router.post("/register")
def register_user(user: UserRegister):
    try:
        existing_user = db.Users.find_one({"email": user.email})
        if existing_user:
            return {"status": "Error", "message": "Email already registered"}
        
        user_data = {
            "name": user.name,
            "email": user.email,
            "password": user.password,
            "role": "user",
            "phonenumber": user.phonenumber or "",
            "address": user.address or ""
        }
        db.Users.insert_one(user_data)
        return {"status": "Success", "message": "User registered successfully"}
    except Exception as e:
        return {"status": "Error", "details": str(e)}

@router.post("/login")
def login_user(user: UserLogin):
    try:
        found_user = db.Users.find_one({"email": user.email, "password": user.password})
        if found_user:
            return {
                "status": "Success",
                "message": "Login successful",
                "user": {
                    "_id": str(found_user["_id"]),
                    "username": found_user.get("name", ""),
                    "email": found_user.get("email", ""),
                    "phonenumber": found_user.get("phonenumber", ""),
                    "address": found_user.get("address", "")
                }
            }
        return {"status": "Error", "message": "Invalid email or password"}
    except Exception as e:
        return {"status": "Error", "details": str(e)}

@router.put("/users/{user_id}")
def update_user(user_id: str, user: UserUpdate):
    try:
        update_data = {}
        if user.username is not None:
            update_data["name"] = user.username
        if user.email is not None:
            update_data["email"] = user.email
        if user.phonenumber is not None:
            update_data["phonenumber"] = user.phonenumber
        if user.address is not None:
            update_data["address"] = user.address
        if user.password is not None and user.password.strip() != "":
            update_data["password"] = user.password

        if not update_data:
            db_user = db.Users.find_one({"_id": ObjectId(user_id)})
            if not db_user:
                return {"status": "Error", "message": "User not found"}
            return {
                "status": "Success",
                "message": "No changes to update",
                "user": {
                    "_id": str(db_user["_id"]),
                    "username": db_user.get("name", ""),
                    "email": db_user.get("email", ""),
                    "phonenumber": db_user.get("phonenumber", ""),
                    "address": db_user.get("address", "")
                }
            }

        res = db.Users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )

        db_user = db.Users.find_one({"_id": ObjectId(user_id)})
        if not db_user:
            return {"status": "Error", "message": "User not found"}

        return {
            "status": "Success",
            "message": "User updated successfully",
            "user": {
                "_id": str(db_user["_id"]),
                "username": db_user.get("name", ""),
                "email": db_user.get("email", ""),
                "phonenumber": db_user.get("phonenumber", ""),
                "address": db_user.get("address", "")
            }
        }
    except Exception as e:
        return {"status": "Error", "message": str(e)}

@router.get("/users")
def get_all_users():
    try:
        users = list(db.Users.find())
        user_list = []
        for user in users:
            user_list.append({
                "_id": str(user["_id"]),
                "username": user.get("name", user.get("username", "")),
                "email": user.get("email", ""),
                "phonenumber": user.get("phonenumber", ""),
                "address": user.get("address", "")
            })
        return {"status": "Success", "user": user_list}
    except Exception as e:
        return {"status": "Error", "details": str(e)}

@router.delete("/users/{user_id}")
def delete_user(user_id: str):
    try:
        res = db.Users.delete_one({"_id": ObjectId(user_id)})
        if res.deleted_count > 0:
            return {"status": "Success", "message": "User deleted successfully"}
        return {"status": "Error", "message": "User not found"}
    except Exception as e:
        return {"status": "Error", "details": str(e)}
