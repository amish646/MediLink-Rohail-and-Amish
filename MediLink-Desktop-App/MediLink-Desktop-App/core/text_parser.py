import re
from core.fuzzy_matching import OcrFuzzyMatcher

class OcrTextParser:
    @staticmethod
    def is_inventory_line(line_text):
        line_low = line_text.lower().strip()
        if not line_low:
            return False
            
        ignore_keywords = [
            "total", "subtotal", "tax", "invoice", "receipt", "bill", "cashier",
            "customer", "address", "phone", "mobile", "cash", "change", "net amount", "balance",
            "b.no", "bno", "s.no", "sno", "page", "tel", "fax", "email", "website",
            "lic", "mfg", "client", "buyer", "seller", "patient", "slip", "payment",
            "sign", "signature", "received", "delivered", "terms", "conditions", "warranty", "thank", "visit"
        ]
        
        for kw in ignore_keywords:
            if kw in line_low:
                return False
                
        words = re.findall(r'\b[a-zA-Z]{3,}\b', line_low)
        if not words:
            return False
            
        if not re.search(r'\d', line_low):
            return False
            
        return True

    @staticmethod
    def clean_ocr_number(num_str):
        num_str = num_str.upper()
        corrections = {
            'O': '0', 'I': '1', 'L': '1', 'S': '5', 'Z': '2'
        }
        cleaned = ""
        for char in num_str:
            if char in corrections:
                cleaned += corrections[char]
            elif char.isdigit() or char == '.':
                cleaned += char
        return cleaned

    @classmethod
    def parse_fields_from_text(cls, text, known_brands, log_callback=None,
                                base_brand=None, base_formula=None, base_price=None, base_qty=None, base_expiry=None):
        original_text = text.strip()
        text = original_text
        
        text = re.sub(r'(?<=\d)[oO]', '0', text)
        text = re.sub(r'[oO](?=\d)', '0', text)
        text = re.sub(r'\.[oO]{2}', '.00', text)
        text = re.sub(r'\.[oO]', '.0', text)
        text = re.sub(r'[\u0000-\u001f\u007f-\u009f]S', 'Rs', text)
        
        expiry = base_expiry or ""
        expiry_match = re.search(r'\b(0[1-9]|1[0-2])[-/.](2[3-9]|3[0-9])\b', text)
        if expiry_match:
            if not expiry:
                expiry = expiry_match.group(0)
            text = text.replace(expiry_match.group(0), " ")
        if not expiry or expiry == "N/A":
            expiry = "12/27"
            
        dosage_match = re.search(r'\b\d+(?:\s*(?:mg|g|ml|mcg|iu|mg/ml|ug))\b', text, re.IGNORECASE)
        dosage = "N/A"
        if dosage_match:
            dosage = dosage_match.group(0)
            text = text.replace(dosage_match.group(0), " ")
        
        form_match = re.search(r'\b(tab|tabs|cap|caps|syp|syrup|inj|injection|susp|suspension|crm|cream|drp|drops|tablet|capsule)\b', text, re.IGNORECASE)
        form = "Tablet"
        if form_match:
            form = form_match.group(0).title()
            text = text.replace(form_match.group(0), " ")
        if form in ("Tabs", "Tab"):
            form = "Tablet"
        elif form in ("Caps", "Cap"):
            form = "Capsule"
        elif form in ("Syp", "Syrup"):
            form = "Syrup"
        elif form in ("Inj", "Injection"):
            form = "Injection"
            
        mfg_list = ["GSK", "Abbott", "Hilton", "Pfizer", "Getz", "Sami", "Searle", "Ferozsons", "Sanofi", "Novartis", "Bayer", "Wyeth", "Roche", "Martin Dow", "Bosch", "Barrett Hodgson", "Pharmatec", "Zafa"]
        manufacturer = "Unknown"
        for m in mfg_list:
            if re.search(r'\b' + re.escape(m) + r'\b', text, re.IGNORECASE):
                manufacturer = m
                text = re.sub(r'\b' + re.escape(m) + r'\b', ' ', text, flags=re.IGNORECASE)
                break
                
        category = "General"
        cat_map = {
            "Analgesic": ["panadol", "paracetamol", "calpol", "disprin", "brufen", "ibuprofen", "aspirin", "ponstan", "mefenamic"],
            "Antibiotic": ["amoxil", "amoxicillin", "augmentin", "cipro", "ciprofloxacin", "novidat", "klacid", "clarithromycin", "flagyl", "metronidazole"],
            "Vitamins": ["surbex", "fefol", "vit", "vitamin", "multivitamin"],
            "Antihistamine": ["zyrtec", "cetirizine", "avil", "pheniramine"],
            "Gastrointestinal": ["risek", "omeprazole", "gaviscon", "glucophage", "metformin"]
        }
        lower_line = original_text.lower()
        for cat, keywords in cat_map.items():
            for kw in keywords:
                if kw in lower_line:
                    category = cat
                    break
                    
        barcode_match = re.search(r'\b\d{12,13}\b', text)
        barcode = "N/A"
        if barcode_match:
            barcode = barcode_match.group(0)
            text = text.replace(barcode_match.group(0), " ")
        
        batch_match = re.search(r'\b(?:B\.?No|Batch|Lot)[:\s\-#]*([A-Z0-9\-]{3,12})\b', text, re.IGNORECASE)
        batch = "N/A"
        if batch_match:
            batch = batch_match.group(1)
            text = text.replace(batch_match.group(0), " ")
        else:
            fb_match = re.search(r'\b(?:B|L|LOT)\s*[-/]?\s*([0-9A-Z]{3,10})\b', text, re.IGNORECASE)
            if fb_match:
                batch = fb_match.group(1) if len(fb_match.groups()) > 0 else fb_match.group(0)
                text = text.replace(fb_match.group(0), " ")
                
        pack_match = re.search(r'\b(\d+\s*\'?s|pack\s*of\s*\d+)\b', text, re.IGNORECASE)
        pack_size = "10s"
        if pack_match:
            pack_size = pack_match.group(0)
            text = text.replace(pack_match.group(0), " ")
        
        cleaned_text = re.sub(r'\b(Rs|RS|PKR|pk|Price|\$)\.?\s*', '', text, flags=re.IGNORECASE)
        words = cleaned_text.split()
        raw_nums = []
        for w in words:
            if any(c.isdigit() for c in w):
                cleaned_num = cls.clean_ocr_number(w).strip('.')
                if cleaned_num:
                    try:
                        if '.' in cleaned_num:
                            raw_nums.append(float(cleaned_num))
                        else:
                            raw_nums.append(int(cleaned_num))
                    except ValueError:
                        pass
                        
        price = base_price or 0.0
        quantity = base_qty or 0
        
        matches = []
        if len(raw_nums) >= 3:
            for i in range(len(raw_nums)):
                for j in range(len(raw_nums)):
                    if i == j: continue
                    for k in range(len(raw_nums)):
                        if k == i or k == j: continue
                        q, p, s = raw_nums[i], raw_nums[j], raw_nums[k]
                        if isinstance(q, int) and 1 <= q <= 200 and p > 0:
                            if abs(q * p - s) < 2.0:
                                matches.append((q, p, s))
        if matches:
            matches.sort(key=lambda x: x[2], reverse=True)
            quantity, price, _ = matches[0]
            
        if price == 0.0 or quantity == 0:
            floats = [n for n in raw_nums if isinstance(n, float) or (isinstance(n, int) and n > 200)]
            ints   = [n for n in raw_nums if isinstance(n, int) and n <= 200]
            
            if price == 0.0:
                if floats:
                    price = float(max(floats))
                elif len(raw_nums) == 1 and raw_nums[0] > 200:
                    price = float(raw_nums[0])
                else:
                    price = 100.0
                    
            if quantity == 0:
                if ints:
                    quantity = int(ints[-1])
                elif len(raw_nums) == 1 and raw_nums[0] <= 200:
                    quantity = int(raw_nums[0])
                else:
                    quantity = 50
                    
        cost_price = round(price * 0.85, 2)
        
        tax_match = re.search(r'\b(\d+(?:\.\d+)?)\s*%\s*(?:tax|gst|vat)\b', original_text, re.IGNORECASE)
        tax_rate = 0.0
        if tax_match:
            tax_rate = float(tax_match.group(1))
        else:
            any_pct = re.findall(r'\b(\d+(?:\.\d+)?)\s*%\b', original_text)
            if len(any_pct) >= 1:
                tax_rate = float(any_pct[0])
                
        disc_match = re.search(r'\b(\d+(?:\.\d+)?)\s*%\s*(?:disc|discount|off)\b', original_text, re.IGNORECASE)
        discount = 0.0
        if disc_match:
            discount = float(disc_match.group(1))
            
        brand_name = base_brand or ""
        generic_formula = base_formula or ""
        
        if not brand_name:
            text_only = cleaned_text
            for w in words:
                if any(c.isdigit() for c in w):
                    text_only = text_only.replace(w, " ", 1)
            words_only = [w.strip() for w in re.split(r'[^a-zA-Z/]', text_only) if len(w.strip()) > 1]
            matched = False
            for word in words_only:
                match_res = OcrFuzzyMatcher.fuzzy_match_brand(word, known_brands, log_callback)
                if match_res:
                    brand_name, generic_formula = match_res
                    matched = True
                    break
            if not matched:
                if len(words_only) >= 2:
                    brand_name = words_only[0].title()
                    generic_formula = " ".join(words_only[1:]).title()
                elif len(words_only) == 1:
                    brand_name = words_only[0].title()
                    generic_formula = "Generic Formula"
                else:
                    brand_name = "Scanned Medicine"
                    generic_formula = "Generic Formula"
                    
        return {
            "brand_name": brand_name,
            "generic_formula": generic_formula,
            "manufacturer": manufacturer,
            "category": category,
            "form": form,
            "dosage": dosage,
            "barcode": barcode,
            "batch_number": batch,
            "expiry_date": expiry,
            "pack_size": pack_size,
            "cost_price": cost_price,
            "retail_price": price,
            "tax_rate": tax_rate,
            "discount_allowed": discount,
            "quantity": quantity
        }
