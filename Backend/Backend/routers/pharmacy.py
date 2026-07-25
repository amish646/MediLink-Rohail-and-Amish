from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from bson import ObjectId
from database import db

router = APIRouter(
    prefix="/pharmacies",
    tags=["Pharmacies"]
)

class PharmacyCreate(BaseModel):
    name: str
    license_no: str
    latitude: float
    longitude: float

class PharmacyUpdate(BaseModel):
    name: Optional[str] = None
    license_no: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

@router.get("")
def get_all_pharmacies():
    try:
        pharmacies = list(db.Pharmacies.find())
        for p in pharmacies:
            p["_id"] = str(p["_id"])
        return {"status": "Success", "data": pharmacies}
    except Exception as e:
        return {"status": "Error", "details": str(e)}

@router.post("")
def add_pharmacy(pharmacy: PharmacyCreate):
    try:
        existing = db.Pharmacies.find_one({"license_no": pharmacy.license_no})
        if existing:
            return {"status": "Error", "message": f"Pharmacy with license {pharmacy.license_no} already exists"}
        
        pharmacy_data = {
            "name": pharmacy.name,
            "license_no": pharmacy.license_no,
            "location": {
                "type": "Point",
                "coordinates": [pharmacy.longitude, pharmacy.latitude]
            }
        }
        res = db.Pharmacies.insert_one(pharmacy_data)
        return {"status": "Success", "message": "Pharmacy added successfully", "id": str(res.inserted_id)}
    except Exception as e:
        return {"status": "Error", "details": str(e)}

@router.put("/{pharmacy_id}")
def update_pharmacy(pharmacy_id: str, pharmacy: PharmacyUpdate):
    try:
        update_data = {}
        if pharmacy.name is not None:
            update_data["name"] = pharmacy.name
        if pharmacy.license_no is not None:
            update_data["license_no"] = pharmacy.license_no
        if pharmacy.longitude is not None or pharmacy.latitude is not None:
            existing = db.Pharmacies.find_one({"_id": ObjectId(pharmacy_id)})
            if not existing:
                return {"status": "Error", "message": "Pharmacy not found"}
            
            coords = existing.get("location", {}).get("coordinates", [0.0, 0.0])
            lon = pharmacy.longitude if pharmacy.longitude is not None else coords[0]
            lat = pharmacy.latitude if pharmacy.latitude is not None else coords[1]
            update_data["location"] = {
                "type": "Point",
                "coordinates": [lon, lat]
            }
            
        if not update_data:
            return {"status": "Success", "message": "No changes to update"}
            
        res = db.Pharmacies.update_one(
            {"_id": ObjectId(pharmacy_id)},
            {"$set": update_data}
        )
        if res.modified_count > 0 or res.matched_count > 0:
            return {"status": "Success", "message": "Pharmacy updated successfully"}
        return {"status": "Error", "message": "Pharmacy not found or update failed"}
    except Exception as e:
        return {"status": "Error", "details": str(e)}

@router.delete("/{pharmacy_id}")
def delete_pharmacy(pharmacy_id: str):
    try:
        res = db.Pharmacies.delete_one({"_id": ObjectId(pharmacy_id)})
        if res.deleted_count > 0:
            return {"status": "Success", "message": "Pharmacy deleted successfully"}
        return {"status": "Error", "message": "Pharmacy not found"}
    except Exception as e:
        return {"status": "Error", "details": str(e)}
