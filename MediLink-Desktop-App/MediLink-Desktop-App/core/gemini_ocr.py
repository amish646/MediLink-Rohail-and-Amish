import os
import json
import base64
import urllib.request
import urllib.error

class OcrGeminiRunner:
    @classmethod
    def run_gemini_ai_ocr(cls, image_path, gemini_key):
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
        ext = os.path.splitext(image_path)[1].lower()
        mime_type = "image/jpeg"
        if ext == ".png":
            mime_type = "image/png"
        elif ext == ".webp":
            mime_type = "image/webp"
            
        prompt = (
            "Analyze this invoice image and extract all medicine line items. "
            "Return a valid JSON array of objects. Each object must contain these exact keys: "
            "brand_name, generic_formula, manufacturer, category, form, dosage, barcode, "
            "batch_number, expiry_date, pack_size, cost_price, retail_price, tax_rate, "
            "discount_allowed, quantity. "
            "Rules:\n"
            "- Extract clean strings. Brand name must not contain dosage or form.\n"
            "- Retail price and cost price must be numbers (floats). If cost_price is missing, default to 85% of retail_price.\n"
            "- Expiry date must be in MM/YY format.\n"
            "- Tax rate and discount allowed must be percentage float values (e.g. 10.0 or 0.0).\n"
            "- If any field is not visible, use a reasonable guess or default (e.g. category: 'General', manufacturer: 'Unknown', barcode: 'N/A', batch_number: 'N/A', pack_size: '10s').\n"
            "Return ONLY the raw JSON array of objects, with no markdown code blocks or wrapper text."
        )
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inlineData": {
                                "mimeType": mime_type,
                                "data": encoded_string
                            }
                        }
                    ]
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json"
            }
        }
        
        api_key = gemini_key.strip() or os.environ.get("GEMINI_API_KEY", "").strip() or os.environ.get("GOOGLE_API_KEY", "").strip()
        if not api_key:
            raise ValueError("Gemini API Key is missing. Configure Gemini key to enable AI scan.")
            
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        data_bytes = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={'Content-Type': 'application/json'}
        )
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                res_body = response.read().decode('utf-8')
                res_json = json.loads(res_body)
                
                text_content = res_json["candidates"][0]["content"]["parts"][0]["text"].strip()
                
                if text_content.startswith("```"):
                    lines = text_content.split("\n")
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines and lines[-1].strip() == "```":
                        lines = lines[:-1]
                    text_content = "\n".join(lines).strip()
                    
                items = json.loads(text_content)
                if not isinstance(items, list):
                    if isinstance(items, dict) and "items" in items:
                        items = items["items"]
                    else:
                        raise ValueError("Gemini response did not return a valid list")
                        
                normalized_items = []
                for item in items:
                    b_name = str(item.get("brand_name") or "").strip().title()
                    if not b_name:
                        continue
                    
                    try:
                        price = float(str(item.get("retail_price", 100.0)).replace(",","").replace("Rs","").strip())
                    except:
                        price = 100.0
                        
                    try:
                        cost = float(str(item.get("cost_price", price * 0.85)).replace(",","").replace("Rs","").strip())
                    except:
                        cost = round(price * 0.85, 2)
                        
                    try:
                        tax = float(str(item.get("tax_rate", 0.0)).replace("%","").strip())
                    except:
                        tax = 0.0
                        
                    try:
                        disc = float(str(item.get("discount_allowed", 0.0)).replace("%","").strip())
                    except:
                        disc = 0.0
                        
                    try:
                        qty = max(1, int(float(str(item.get("quantity", 10)).strip())))
                    except:
                        qty = 10
                        
                    normalized_items.append({
                        "brand_name": b_name,
                        "generic_formula": str(item.get("generic_formula") or "N/A").strip().title(),
                        "manufacturer": str(item.get("manufacturer") or "Unknown").strip().title(),
                        "category": str(item.get("category") or "General").strip().title(),
                        "form": str(item.get("form") or "Tablet").strip().title(),
                        "dosage": str(item.get("dosage") or "N/A").strip(),
                        "barcode": str(item.get("barcode") or "N/A").strip(),
                        "batch_number": str(item.get("batch_number") or "N/A").strip(),
                        "expiry_date": str(item.get("expiry_date") or "12/27").strip(),
                        "pack_size": str(item.get("pack_size") or "10s").strip(),
                        "cost_price": cost,
                        "retail_price": price,
                        "tax_rate": tax,
                        "discount_allowed": disc,
                        "quantity": qty
                    })
                return normalized_items
                
        except urllib.error.HTTPError as he:
            err_msg = he.read().decode('utf-8')
            raise RuntimeError(f"Gemini API HTTP Error: {he.code} - {err_msg}")
        except Exception as e:
            raise RuntimeError(f"Gemini parsing error: {e}")
