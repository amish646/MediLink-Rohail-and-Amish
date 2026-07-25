from fastapi import APIRouter, BackgroundTasks
import re
import os
import urllib.parse
import urllib.request
import json
import threading
import time
from google import genai
from google.genai import types
from database import db
from utils.medicine_helpers import (
    normalize_medicine_name,
    known_generics,
    synonym_map,
    get_gemini_key,
    resolve_formula_advanced,
    query_wikipedia_formula,
    query_rxnav_formula,
    fetch_global_brand_alternatives,
    drug_db
)

# -------------------------------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------------------------------

def normalize_formula_to_tokens(formula: str) -> set:
    if not formula:
        return set()
    formula = formula.lower()
    parts = re.split(r'\s*\+\s*|\s*/\s*|\s+and\s+|\s*,\s*', formula)
    tokens = set()
    for part in parts:
        part = part.strip()
        part = re.sub(
            r'\b(?:hcl|hydrochloride|dihydrochloride|fumarate|dipropionate|extended release|er|xr|sr|soluble|succinate|sodium|potassium|calcium|maleate|hydrate|anhydrous|phosphate|sulfate|acetate)\b', 
            '', 
            part
        )
        part = part.strip()
        if part:
            tokens.add(part)
    return tokens

def score_formula_match(search_tokens: set, db_tokens: set) -> float:
    if not search_tokens or not db_tokens:
        return 0.0
    if search_tokens == db_tokens:
        return 1.0
    if search_tokens.issubset(db_tokens) or db_tokens.issubset(search_tokens):
        return 0.8
    intersection = search_tokens.intersection(db_tokens)
    if intersection:
        return 0.5 * (len(intersection) / max(len(search_tokens), len(db_tokens)))
    return 0.0

def query_gemini_ai_details(medicine_name: str) -> dict:
    """Helper function to fetch usage and side effects safely via Gemini"""
    try:
        gemini_key = get_gemini_key()
        if not gemini_key:
            return {}
        
        # FIXED: Correct initialization for google-genai SDK
        client = genai.Client(api_key=gemini_key)
        prompt = f"Provide brief usage and side effects for {medicine_name} in JSON with keys 'usage' and 'side_effects'."
        
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text.strip())
    except Exception:
        return {}

# Concurrency Locks
active_locks = {}
locks_mutex = threading.Lock()

router = APIRouter(tags=["Search & Inventory"])

# -------------------------------------------------------------------------
# API ENDPOINTS
# -------------------------------------------------------------------------

@router.get("/search/{medicine_name}")
def search_medicine(medicine_name: str):
    try:
        result = db.GlobalMedicines.find_one(
            {"brand_name": {"$regex": f"^{medicine_name}$", "$options": "i"}}
        )
        if result:
            return {
                "status": "Found",
                "brand_name": result["brand_name"],
                "formula": result.get("generic_formula", "N/A")
            }
        return {"status": "Not Found", "message": "Medicine not in global catalog"}
    except Exception as e:
        return {"status": "Error", "details": str(e)}

def fetch_and_save_ai_details(medicine_name: str, formula: str):
    try:
        ai_data = query_gemini_ai_details(medicine_name)
        if ai_data:
            usage = ai_data.get("usage", "Not Specified")
            side_effects = ai_data.get("side_effects", "Not Specified")
            db.GlobalMedicines.update_one(
                {"brand_name": medicine_name},
                {"$set": {
                    "brand_name": medicine_name,
                    "generic_formula": formula,
                    "usage": usage,
                    "side_effects": side_effects,
                    "source": "Google Gemini AI"
                }},
                upsert=True
            )
    except Exception as e:
        print(f"Error fetching AI details in background: {e}")

@router.get("/availability/{medicine_name}")
def check_availability(medicine_name: str, background_tasks: BackgroundTasks):
    try:
        inventory_matches = list(db.Inventory.find({
            "medicine_name": {"$regex": f"^{medicine_name}$", "$options": "i"},
            "quantity": {"$gt": 0}
        }))
        
        if not inventory_matches:
            return {"status": "Empty", "message": f"Sorry, {medicine_name} is out of stock in all branches."}

        available_at = []
        formula = inventory_matches[0].get("generic_formula", "N/A") if inventory_matches else "N/A"
        
        usage = "Not Specified"
        side_effects = "Not Specified"
        
        global_med = db.GlobalMedicines.find_one(
            {"brand_name": {"$regex": f"^{re.escape(medicine_name)}$", "$options": "i"}}
        )
        if global_med and global_med.get("usage") and global_med.get("usage") != "N/A" and global_med.get("usage") != "Not Specified":
            usage = global_med.get("usage")
            side_effects = global_med.get("side_effects", "Not Specified")
        else:
            background_tasks.add_task(fetch_and_save_ai_details, medicine_name, formula)
        
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
                "price": item.get("price", "N/A"),
                "formula": item.get("generic_formula", "N/A"),
                "expiry_date": item.get("expiry_date", "N/A"),
                "location": location_str,
                "lat": lat,
                "lng": lng,
                "last_updated": item.get("last_updated", "N/A"),
                "discount": item.get("discount_allowed", 0.0),
                "manufacturer": item.get("manufacturer", "Unknown"),
                "dosage": item.get("dosage", "N/A")
            })
            
        return {
            "medicine": medicine_name, 
            "status": "Available", 
            "formula": formula, 
            "usage": usage,
            "side_effects": side_effects,
            "available_branches": available_at
        }
    except Exception as e:
        return {"status": "Error", "details": str(e)}

@router.get("/local-inventory")
def get_global_inventory():
    try:
        inventory = list(db.Inventory.find({"quantity": {"$gt": 0}}))
        pharmacies = {p.get("license_no", ""): p for p in db.Pharmacies.find()}
        
        data = []
        for item in inventory:
            lic = item.get("pharmacy_license", "Unknown Pharmacy")
            pharmacy = pharmacies.get(lic)
            lat, lng = 0.0, 0.0
            p_name = f"Pharmacy ({lic})"
            if pharmacy:
                p_name = pharmacy.get("name", p_name)
                if "location" in pharmacy and "coordinates" in pharmacy["location"]:
                    coords = pharmacy["location"]["coordinates"]
                    lng, lat = coords[0], coords[1]
                
            data.append({
                "brand_name": item.get("medicine_name", "Unknown"),
                "quantity": item.get("quantity", 0),
                "purchase_price": item.get("price", 0),
                "pharmacy_license": lic,
                "pharmacy_name": p_name,
                "lat": lat,
                "lng": lng,
                "discount": item.get("discount_allowed", 0.0)
            })
            
        return {"status": "Success", "data": data}
    except Exception as e:
        return {"status": "Error", "details": str(e)}

@router.get("/api/ai-alternatives/{medicine_name}")
def get_ai_alternatives(medicine_name: str):
    try:
        name_clean = normalize_medicine_name(medicine_name)
        if not name_clean:
            name_clean = medicine_name.lower().strip()
            
        with locks_mutex:
            if name_clean not in active_locks:
                active_locks[name_clean] = threading.Lock()
                
        with active_locks[name_clean]:
            formula = None
            ai_alternatives_list = None
            usage = "N/A"
            side_effects = "N/A"
            
            global_med = db.GlobalMedicines.find_one(
                {"brand_name": {"$regex": f"^{re.escape(name_clean)}$", "$options": "i"}}
            )
            if not global_med:
                global_med = db.GlobalMedicines.find_one(
                    {"brand_name": {"$regex": f"^{re.escape(medicine_name)}$", "$options": "i"}}
                )
                
            if global_med:
                formula = global_med.get("generic_formula")
                usage = global_med.get("usage", "N/A")
                side_effects = global_med.get("side_effects", "N/A")
                if "alternatives" in global_med:
                    ai_alternatives_list = global_med.get("alternatives")
                    if ai_alternatives_list is None:
                        ai_alternatives_list = []

            if not formula or ai_alternatives_list is None:
                gemini_key = get_gemini_key()
                gemini_success = False
                if gemini_key:
                    for attempt in range(3):
                        try:
                            # FIXED: Correct client syntax for new google-genai library
                            client = genai.Client(api_key=gemini_key)
                            
                            system_prompt = (
                                "You are a medical information assistant. Your job is only to list alternative brand names "
                                "that share the exact same active pharmaceutical ingredient (salt) and dosage strength as requested. "
                                "Do not give medical advice or clinical diagnoses. Always include a short disclaimer to consult a doctor. "
                                "Return ONLY a raw JSON object with keys: generic_formula, usage, side_effects, alternatives (list of strings)."
                            )
                            safety_settings = [
                                types.SafetySetting(
                                    category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                                    threshold=types.HarmBlockThreshold.BLOCK_NONE,
                                )
                            ]
                            prompt = (
                                f"Identify the generic formula/active ingredient, usage, side effects, "
                                f"and 5 alternative brand names for the medicine: {medicine_name}. "
                                f"For generic_formula, return only the primary active ingredient generic name (e.g., 'paracetamol', 'ibuprofen') without brand synonyms or parentheses. "
                                f"Include the disclaimer in the usage or side_effects fields if appropriate, but ensure the JSON keys match: generic_formula, usage, side_effects, alternatives."
                            )
                            
                            # FIXED: Swapped out 'gemini-flash-latest' string name for standard 'gemini-1.5-flash'
                            response = client.models.generate_content(
                                model='gemini-1.5-flash',
                                contents=prompt,
                                config=types.GenerateContentConfig(
                                    temperature=0.2,
                                    system_instruction=system_prompt,
                                    safety_settings=safety_settings,
                                    response_mime_type="application/json"
                                )
                            )
                            text_resp = response.text.strip()
                            
                            # FIXED: Protection against both wrapped markdown codeblocks and raw json responses
                            if text_resp.startswith("```"):
                                clean_text = text_resp.replace("```json", "").replace("```", "").strip()
                            else:
                                clean_text = text_resp
                                
                            ai_info = json.loads(clean_text)
                            
                            formula = ai_info.get("generic_formula")
                            usage = ai_info.get("usage", "N/A")
                            side_effects = ai_info.get("side_effects", "N/A")
                            ai_alternatives_list = ai_info.get("alternatives", [])
                            if ai_alternatives_list is None:
                                ai_alternatives_list = []
                            
                            if formula:
                                db.GlobalMedicines.update_one(
                                    {"brand_name": {"$regex": f"^{re.escape(medicine_name)}$", "$options": "i"}},
                                    {"$set": {
                                        "brand_name": medicine_name.capitalize(),
                                        "generic_formula": formula,
                                        "usage": usage,
                                        "side_effects": side_effects,
                                        "alternatives": ai_alternatives_list,
                                        "source": "Google Gemini AI"
                                    }},
                                    upsert=True
                                )
                                gemini_success = True
                                break
                        except Exception as e:
                            time.sleep(1.5)
                                
                    if not gemini_success or not formula or ai_alternatives_list is None:
                        if not formula:
                            formula = resolve_formula_advanced(name_clean)
                        if not formula:
                            formula = query_rxnav_formula(name_clean)
                        if not formula:
                            formula = query_wikipedia_formula(name_clean)
                            
                        if formula:
                            rx_brands = fetch_global_brand_alternatives(formula)
                            local_alts = []
                            for brand, form in drug_db.items():
                                if form.lower() == formula.lower() and brand.lower() != medicine_name.lower() and brand.lower() != name_clean.lower():
                                    local_alts.append(brand.capitalize())
                                    
                            combined_alts = list(set(rx_brands + local_alts))
                            ai_alternatives_list = combined_alts[:5]
                            
                            db.GlobalMedicines.update_one(
                                {"brand_name": {"$regex": f"^{re.escape(medicine_name)}$", "$options": "i"}},
                                {"$set": {
                                    "brand_name": medicine_name.capitalize(),
                                    "generic_formula": formula,
                                    "usage": "Clinical usage information (refer to physician).",
                                    "side_effects": "Refer to physician for clinical details.",
                                    "alternatives": ai_alternatives_list,
                                    "source": "Online Clinical Database (Gemini Fallback)"
                                }},
                                upsert=True
                            )

            if not formula:
                return {
                    "status": "Not Found",
                    "message": f"Could not determine generic formula or alternatives for '{medicine_name}'."
                }

            # Smart formula matching with overlap scoring (First Scheme)
            unique_db_formulas = db.Inventory.distinct("generic_formula")
            search_formulas = [formula]
            if formula in synonym_map:
                search_formulas.append(synonym_map[formula])
                
            search_token_sets = [normalize_formula_to_tokens(f) for f in search_formulas]
            
            matched_formulas = []
            for db_f in unique_db_formulas:
                if not db_f:
                    continue
                db_tokens = normalize_formula_to_tokens(db_f)
                max_score = 0.0
                for s_tokens in search_token_sets:
                    score = score_formula_match(s_tokens, db_tokens)
                    if score > max_score:
                        max_score = score
                if max_score > 0.0:
                    matched_formulas.append((db_f, max_score))
                    
            matched_formulas.sort(key=lambda x: x[1], reverse=True)
            formulas_to_query = [item[0] for item in matched_formulas]
            formula_scores = {item[0]: item[1] for item in matched_formulas}

            alternatives = []
            if formulas_to_query:
                alternatives = list(db.Inventory.find({
                    "generic_formula": {"$in": formulas_to_query},
                    "medicine_name": {"$ne": medicine_name},
                    "brand_name": {
                        "$nin": [
                            re.compile(f"^{re.escape(medicine_name)}$", re.IGNORECASE), 
                            re.compile(f"^{re.escape(name_clean)}$", re.IGNORECASE)
                        ]
                    },
                    "quantity": {"$gt": 0}
                }))
                alternatives.sort(key=lambda x: formula_scores.get(x.get("generic_formula"), 0.0), reverse=True)

            in_stock_alts = []
            pharmacies = {p.get("license_no", ""): p for p in db.Pharmacies.find()}
            for item in alternatives:
                lic = item.get("pharmacy_license", "Unknown")
                p_name = pharmacies.get(lic, {}).get("name", f"Pharmacy ({lic})")
                db_formula = item.get("generic_formula", formula)
                score = formula_scores.get(db_formula, 1.0)
                
                if score == 1.0:
                    status_label = "In Stock"
                elif score >= 0.8:
                    status_label = "In Stock (Strong Formulation Match)"
                else:
                    status_label = "In Stock (Combination Alternative)"

                in_stock_alts.append({
                    "brand_name": item.get("medicine_name"),
                    "generic_formula": db_formula,
                    "price": item.get("price", 0),
                    "quantity": item.get("quantity", 0),
                    "pharmacy_name": p_name,
                    "pharmacy_license": lic,
                    "discount": item.get("discount_allowed", 0.0),
                    "status": status_label
                })

            global_suggestions = []
            if ai_alternatives_list:
                for alt_name in ai_alternatives_list:
                    if alt_name.lower() != medicine_name.lower() and alt_name.lower() != name_clean.lower():
                        global_suggestions.append({
                            "brand_name": alt_name,
                            "generic_formula": formula,
                            "status": "Suggested by AI Assistant"
                        })

            # FIXED: Added fallback checking for .capitalize() call to avoid NoneType errors
            formatted_formula = formula.capitalize() if formula else "Unknown Formula"

            return {
                "status": "Success",
                "searched_medicine": medicine_name,
                "generic_formula": formatted_formula,
                "in_stock_alternatives": in_stock_alts,
                "global_suggestions": global_suggestions[:6]
            }
    except Exception as e:
        return {"status": "Error", "details": str(e)}