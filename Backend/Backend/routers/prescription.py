from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import os
from datetime import datetime
from bson import ObjectId
from database import db

router = APIRouter(
    prefix="/prescription",
    tags=["Prescription"]
)

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.post("/upload")
async def upload_prescription(
    email: str = Form(...), 
    file: UploadFile = File(...),
    username: str = Form(None),
    phone: str = Form(None),
    address: str = Form(None)
):
    try:
        if not file.content_type.startswith("image/"):
            return {"status": "Error", "message": "Only image files are allowed"}

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        prescription_data = {
            "email": email,
            "filename": filename,
            "file_path": file_path,
            "upload_date": datetime.now(),
            "status": "Pending",
            "username": username,
            "phone": phone,
            "address": address
        }
        
        db.Prescriptions.insert_one(prescription_data)

        return {
            "status": "Success", 
            "message": "Prescription uploaded successfully",
            "file_url": f"/uploads/{filename}"
        }
    except Exception as e:
        return {"status": "Error", "details": str(e)}

def search_medicine_in_stock(medicine_name: str):
    import re
    try:
        inventory_matches = list(db.Inventory.find({
            "medicine_name": {"$regex": f"^{re.escape(medicine_name)}$", "$options": "i"},
            "quantity": {"$gt": 0}
        }))
        
        if not inventory_matches:
            return {"status": "Empty", "available_branches": []}

        available_at = []
        formula = inventory_matches[0].get("generic_formula", "N/A")
        
        for item in inventory_matches:
            lic = item.get("pharmacy_license", "Unknown License")
            pharmacy = db.Pharmacies.find_one({"license_no": lic})
            pharmacy_name = pharmacy["name"] if pharmacy else f"Pharmacy ({lic})"
            location_str = pharmacy["location"] if pharmacy and "location" in pharmacy else "Location not available"
            
            lat, lng = 0.0, 0.0
            if pharmacy and "location" in pharmacy and "coordinates" in pharmacy["location"]:
                coords = pharmacy["location"]["coordinates"]
                lng, lat = coords[0], coords[1]
            
            available_at.append({
                "pharmacy_name": pharmacy_name,
                "pharmacy_license": lic,
                "stock_available": item.get("quantity", 0),
                "price": item.get("price", 0),
                "formula": item.get("generic_formula", "N/A"),
                "expiry_date": item.get("expiry_date", "N/A"),
                "location": location_str,
                "lat": lat,
                "lng": lng,
                "discount": item.get("discount_allowed", 0.0),
                "manufacturer": item.get("manufacturer", "Unknown"),
                "dosage": item.get("dosage", "N/A")
            })
        return {
            "status": "Available",
            "formula": formula,
            "available_branches": available_at
        }
    except Exception:
        return {"status": "Empty", "available_branches": []}

@router.post("/upload-ocr")
async def upload_prescription_ocr(
    email: str = Form(...), 
    file: UploadFile = File(...),
    username: str = Form(None),
    phone: str = Form(None),
    address: str = Form(None)
):
    try:
        if not file.content_type.startswith("image/"):
            return {"status": "Error", "message": "Only image files are allowed"}

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # 1. Read key and perform Gemini OCR
        from utils.medicine_helpers import get_gemini_key
        import base64
        import urllib.request
        import urllib.error
        import json

        key = get_gemini_key()
        if not key:
            return {
                "status": "Success",
                "ocr_status": "KeyMissing",
                "message": "Prescription uploaded, but Gemini API Key is missing. OCR could not be performed.",
                "file_url": f"/uploads/{filename}",
                "medicines": []
            }

        # Base64 encode the image
        with open(file_path, "rb") as img_file:
            encoded_image = base64.b64encode(img_file.read()).decode("utf-8")

        ext = os.path.splitext(file_path)[1].lower()
        mime_type = "image/jpeg"
        if ext == ".png":
            mime_type = "image/png"
        elif ext == ".webp":
            mime_type = "image/webp"

        prompt = (
            "Extract all medicine/drug names from this medical prescription image. "
            "Return a valid JSON array of strings, where each element is a medicine name. "
            "Examples: [\"Panadol\", \"Augmentin\", \"Arinac\"]. "
            "Rules:\n"
            "- Extract only the medicine name (brand name or active ingredient), omit dosages, quantities, and frequencies.\n"
            "- If no medicines are found or the image is not a prescription, return an empty array [].\n"
            "Return ONLY the raw JSON array of strings, with no markdown code blocks or wrapper text."
        )

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inlineData": {
                                "mimeType": mime_type,
                                "data": encoded_image
                            }
                        }
                    ]
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json"
            }
        }

        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
        req_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            gemini_url,
            data=req_data,
            headers={"Content-Type": "application/json"}
        )

        extracted_medicines = []
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                res_body = response.read().decode("utf-8")
                res_json = json.loads(res_body)
                text_content = res_json["candidates"][0]["content"]["parts"][0]["text"].strip()
                
                # Clean up potential markdown formatting
                if text_content.startswith("```"):
                    lines = text_content.split("\n")
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines and lines[-1].strip() == "```":
                        lines = lines[:-1]
                    text_content = "\n".join(lines).strip()

                parsed = json.loads(text_content)
                if isinstance(parsed, list):
                    extracted_medicines = [str(m).strip() for m in parsed if m]
        except Exception as e_ocr:
            return {
                "status": "Error",
                "message": f"Gemini OCR scanning failed: {str(e_ocr)}",
                "details": str(e_ocr)
            }

        # 2. Search stock availability for each medicine
        from routers.search import get_ai_alternatives
        
        medicines_results = []
        for med in extracted_medicines:
            stock_info = search_medicine_in_stock(med)
            if stock_info["status"] == "Available":
                medicines_results.append({
                    "name": med,
                    "status": "Available",
                    "generic_formula": stock_info["formula"],
                    "available_branches": stock_info["available_branches"]
                })
            else:
                # Get alternatives if out of stock
                alternatives_data = {}
                try:
                    alt_res = get_ai_alternatives(med)
                    if alt_res.get("status") == "Success":
                        alternatives_data = alt_res
                except Exception:
                    pass
                
                medicines_results.append({
                    "name": med,
                    "status": "Out of Stock",
                    "generic_formula": alternatives_data.get("generic_formula", "N/A"),
                    "in_stock_alternatives": alternatives_data.get("in_stock_alternatives", []),
                    "global_suggestions": alternatives_data.get("global_suggestions", [])
                })

        # Save to database
        prescription_data = {
            "email": email,
            "filename": filename,
            "file_path": file_path,
            "upload_date": datetime.now(),
            "status": "Scanned",
            "username": username,
            "phone": phone,
            "address": address,
            "medication_names": ", ".join(extracted_medicines) if extracted_medicines else "None Found",
            "ocr_results": medicines_results
        }
        db.Prescriptions.insert_one(prescription_data)

        return {
            "status": "Success",
            "message": "Prescription uploaded and scanned successfully",
            "file_url": f"/uploads/{filename}",
            "medicines": medicines_results
        }
    except Exception as e:
        return {"status": "Error", "details": str(e)}

@router.get("/read")
def read_all_prescriptions():
    try:
        prescriptions = list(db.Prescriptions.find())
        formatted = []
        for p in prescriptions:
            p_id = str(p["_id"])
            email = p.get("email", "")
            
            username = p.get("username")
            phone = p.get("phone", "")
            address = p.get("address", "")
            
            if not username or not phone or not address:
                user = db.Users.find_one({"email": email})
                if user:
                    if not username:
                        username = user.get("name")
                    if not phone:
                        phone = user.get("phonenumber", "")
                    if not address:
                        address = user.get("address", "")
            
            first_name = email
            last_name = ""
            if username:
                parts = username.split(maxsplit=1)
                first_name = parts[0]
                last_name = parts[1] if len(parts) > 1 else ""
                
            formatted.append({
                "_id": p_id,
                "PrescriptionID": p_id,
                "firstName": first_name,
                "lastName": last_name,
                "email": email,
                "phone": phone,
                "address": address,
                "filename": p.get("filename", ""),
                "file_path": p.get("file_path", ""),
                "MedicationNames": p.get("medication_names", "Pending Review"),
                "units": p.get("units", 0),
                "createdAt": p.get("upload_date", datetime.now()).isoformat(),
                "status": p.get("status", "Pending")
            })
        return {"status": "Success", "prescription": formatted}
    except Exception as e:
        return {"status": "Error", "details": str(e)}

@router.put("/update/{id}")
def update_prescription_status(id: str, data: dict):
    try:
        db.Prescriptions.update_one(
            {"_id": ObjectId(id)},
            {"$set": data}
        )
        return {"status": "Success", "message": "Prescription updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/delete/{id}")
def delete_prescription(id: str):
    try:
        db.Prescriptions.delete_one({"_id": ObjectId(id)})
        return {"status": "Success", "message": "Prescription deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{email}")
def get_user_prescriptions(email: str):
    try:
        prescriptions = list(db.Prescriptions.find({"email": email}))
        
        for p in prescriptions:
            p["_id"] = str(p["_id"])
            
        return {"status": "Success", "prescriptions": prescriptions}
    except Exception as e:
        return {"status": "Error", "details": str(e)}
