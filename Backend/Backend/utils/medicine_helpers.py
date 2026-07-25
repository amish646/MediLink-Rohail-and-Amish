import os
import re
import urllib.request
import urllib.parse
import json
from google import genai
from google.genai import types
import difflib
import logging

logger = logging.getLogger(__name__)

def get_gemini_key():
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if key:
        return key
    if os.path.exists("pharmacy_config.json"):
        try:
            with open("pharmacy_config.json", "r") as f:
                data = json.load(f)
                return data.get("gemini_key")
        except Exception:
            pass
    return None

def query_gemini_ai_details(medicine_name: str):
    key = get_gemini_key()
    if not key:
        return None
    try:
        client = genai.Client(api_key=key)
        system_prompt = (
            "You are a medical information assistant. Your job is only to list clinical usage and side effects as requested. "
            "Do not give medical advice or clinical diagnoses. Always include a short disclaimer to consult a doctor. "
            "Return ONLY a raw JSON object with keys: usage, side_effects."
        )
        safety_settings = [
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.BLOCK_NONE,
            )
        ]
        prompt = (
            f"Identify the clinical usage and side effects for the medicine: {medicine_name}. "
            f"Include the disclaimer in the usage or side_effects fields if appropriate, but ensure the JSON keys match: usage, side_effects."
        )
        response = client.models.generate_content(
            model='gemini-flash-latest',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                system_instruction=system_prompt,
                safety_settings=safety_settings,
                response_mime_type="application/json"
            )
        )
        text_resp = response.text.strip()
        clean_text = text_resp.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except Exception as e:
        logger.error(f"Gemini details query failed: {e}")
    return None

drug_db = {
    "panadol": "paracetamol",
    "calpol": "paracetamol",
    "febrol": "paracetamol",
    "disprol": "paracetamol",
    "parol": "paracetamol",
    "tylenol": "paracetamol",
    "acetaminophen": "paracetamol",
    "brufen": "ibuprofen",
    "advel": "ibuprofen",
    "nurofen": "ibuprofen",
    "advil": "ibuprofen",
    "motrin": "ibuprofen",
    "aleve": "naproxen",
    "synflex": "naproxen",
    "naprosyn": "naproxen",
    "arinac": "ibuprofen + pseudoephedrine",
    "sinutab": "ibuprofen + pseudoephedrine",
    "augmentin": "co-amoxiclav",
    "amoxil": "amoxicillin",
    "clavam": "co-amoxiclav",
    "novamox": "amoxicillin",
    "flemoxin": "amoxicillin",
    "velosef": "cephradine",
    "ceclor": "cefaclor",
    "keflex": "cephalexin",
    "cefspan": "cefixime",
    "caracef": "cefixime",
    "rocephin": "ceftriaxone",
    "leflox": "levofloxacin",
    "cravit": "levofloxacin",
    "disprin": "aspirin",
    "loprin": "aspirin",
    "ascard": "aspirin",
    "aspirin": "aspirin",
    "flagyl": "metronidazole",
    "metodine": "metronidazole",
    "entamizole": "metronidazole + diloxanide furoate",
    "prilosec": "omeprazole",
    "risek": "omeprazole",
    "rizek": "omeprazole",
    "omez": "omeprazole",
    "omega": "omeprazole",
    "lopraz": "omeprazole",
    "osral": "omeprazole",
    "omep": "omeprazole",
    "nexum": "esomeprazole",
    "esome": "esomeprazole",
    "eso": "esomeprazole",
    "nexium": "esomeprazole",
    "zyrtec": "cetirizine",
    "rigix": "cetirizine",
    "cetrine": "cetirizine",
    "reactine": "cetirizine",
    "clarityne": "loratadine",
    "claritin": "loratadine",
    "softin": "loratadine",
    "solvin": "loratadine",
    "lorin": "loratadine",
    "aerius": "desloratadine",
    "xyzal": "levocetirizine",
    "telfast": "fexofenadine",
    "fexet": "fexofenadine",
    "fexo": "fexofenadine",
    "allegra": "fexofenadine",
    "kestine": "ebastine",
    "lipitor": "atorvastatin",
    "lipirex": "atorvastatin",
    "lipiget": "atorvastatin",
    "lipocard": "atorvastatin",
    "liponorm": "atorvastatin",
    "crestor": "rosuvastatin",
    "rovista": "rosuvastatin",
    "zocor": "simvastatin",
    "glucophage": "metformin",
    "neodipar": "metformin",
    "glucovance": "metformin + glyburide",
    "novidat": "ciprofloxacin",
    "ciproxin": "ciprofloxacin",
    "cipro": "ciprofloxacin",
    "singulair": "montelukast",
    "montika": "montelukast",
    "voren": "diclofenac sodium",
    "voltarel": "diclofenac sodium",
    "voltaren": "diclofenac sodium",
    "dicloran": "diclofenac sodium",
    "caflam": "diclofenac potassium",
    "ponstan": "mefenamic acid",
    "ventolin": "salbutamol",
    "ventoline": "salbutamol",
    "proair": "salbutamol",
    "norvasc": "amlodipine",
    "amcard": "amlodipine",
    "cozaar": "losartan",
    "cardup": "losartan",
    "diovan": "valsartan",
    "concor": "bisoprolol",
    "inderal": "propranolol",
    "tenormin": "atenolol",
    "capoten": "captopril",
    "zestril": "lisinopril",
    "coversyl": "perindopril",
    "renitec": "enalapril",
    "epival": "divalproex sodium",
    "depakote": "divalproex sodium",
    "tegral": "carbamazepine",
    "tegretol": "carbamazepine",
    "xanax": "alprazolam",
    "alprax": "alprazolam",
    "lexotanil": "bromazepam",
    "lexotan": "bromazepam",
    "valium": "diazepam",
    "ativan": "lorazepam",
    "rivotril": "clonazepam",
    "klonopin": "clonazepam",
    "serc": "betahistine",
    "betaserc": "betahistine",
    "gravinate": "dimenhydrinate",
    "dramamine": "dimenhydrinate",
    "no-spa": "drotaverine",
    "buscopan": "hyoscine butylbromide",
    "motilium": "domperidone",
    "cac 1000": "calcium + vitamin c",
    "surbex z": "multivitamin + zinc",
    "surbex": "multivitamin",
    "theragran": "multivitamin",
    "sangobion": "iron + b complex",
    "fefol": "iron + folic acid",
    "iberet": "iron + vitamin c + b complex",
    "neurobion": "vitamin b complex",
    "azomax": "azithromycin",
    "zithromax": "azithromycin",
    "tramal": "tramadol",
    "ultram": "tramadol",
    "lowplat": "clopidogrel",
    "plavix": "clopidogrel",
    "copid": "clopidogrel",
    "cravit": "levofloxacin",
    "betnovate": "betamethasone",
    "solu-cortef": "hydrocortisone",
    "deltacortril": "prednisolone",
    "avil": "pheniramine",
    "zantac": "ranitidine",
    "pepcid": "famotidine",
    "aldactone": "spironolactone",
    "lasix": "furosemide",
    "neurontin": "gabapentin",
    "lyrica": "pregabalin",
    "cipralex": "escitalopram",
    "lexapro": "escitalopram",
    "zoloft": "sertraline",
    "prozac": "fluoxetine",
    "viagra": "sildenafil",
    "cialis": "tadalafil",
    "pulmicort": "budesonide",
    "symbicort": "budesonide + formoterol",
    "seretide": "salmeterol + fluticasone",
    "advair": "salmeterol + fluticasone",
    "flonase": "fluticasone",
    "canesten": "clotrimazole",
    "daktarin": "miconazole",
    "lamisil": "terbinafine",
    "zovirax": "acyclovir",
    "tamiflu": "oseltamivir",
    "avelox": "moxifloxacin",
    "diamicron": "gliclazide",
    "amaryl": "glimepiride",
    "januvia": "sitagliptin",
    "galvus": "vildagliptin",
    "actos": "pioglitazone",
    "caduet": "atorvastatin + amlodipine",
    "exforge": "valsartan + amlodipine",
    "lodoz": "bisoprolol + hydrochlorothiazide",
}

synonym_map = {
    "paracetamol": "acetaminophen",
    "acetaminophen": "paracetamol",
    "salbutamol": "albuterol",
    "albuterol": "salbutamol",
    "co-amoxiclav": "amoxicillin + clavulanate potassium",
    "amoxicillin + clavulanate potassium": "co-amoxiclav",
    "aspirin": "acetylsalicylic acid",
    "acetylsalicylic acid": "aspirin",
}

known_generics = set(drug_db.values())
known_generics.update([
    "paracetamol", "acetaminophen", "ibuprofen", "omeprazole", "esomeprazole", 
    "cetirizine", "loratadine", "fexofenadine", "atorvastatin", "metformin", 
    "ciprofloxacin", "montelukast", "amoxicillin", "co-amoxiclav", "salbutamol", 
    "alprazolam", "bromazepam", "diazepam", "clopidogrel", "levofloxacin", 
    "cefixime", "ceftriaxone", "rosuvastatin", "simvastatin"
])

def normalize_medicine_name(medicine_name: str) -> str:
    name_clean = medicine_name.lower().strip()
    name_clean = re.sub(r'\b\d+(?:\.\d+)?\s*(?:mg|g|ml|mcg|%|cc)\b', '', name_clean)
    name_clean = re.sub(r'\b\d+\b', '', name_clean)
    forms_patterns = [
        r'\btablets?\b', r'\bcapsules?\b', r'\bsyrups?\b', r'\bsuspensions?\b',
        r'\binjections?\b', r'\bdrops?\b', r'\binfusions?\b', r'\bcreams?\b',
        r'\bointments?\b', r'\bgels?\b', r'\bsprays?\b', r'\binhalers?\b',
        r'\bsolutions?\b', r'\bextra\b', r'\bplus\b', r'\bcf\b', r'\bds\b',
        r'\bfort\b', r'\bforte\b', r'\bliquid\b', r'\bpowder\b'
    ]
    for pattern in forms_patterns:
        name_clean = re.sub(pattern, '', name_clean)
    name_clean = re.sub(r'\s+', ' ', name_clean).strip()
    return name_clean

def resolve_formula_advanced(medicine_name: str):
    name_clean = normalize_medicine_name(medicine_name)
    if not name_clean:
        name_clean = medicine_name.lower().strip()
        
    if name_clean in drug_db:
        return drug_db[name_clean]
    
    close_matches = difflib.get_close_matches(name_clean, drug_db.keys(), n=1, cutoff=0.55)
    if close_matches:
        return drug_db[close_matches[0]]
    return None

def query_wikipedia_formula(medicine_name: str):
    try:
        quoted = urllib.parse.quote(medicine_name)
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quoted}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3) as res:
            if res.status == 200:
                data = json.loads(res.read().decode('utf-8'))
                extract = data.get("extract", "").lower()
                patterns = [
                    r"(?:brand name for|generic name of|active ingredient is|marketed as)\s+([a-z\-]+)",
                    r"([a-z\-]+)\s+is a\s+(?:non-steroidal|antihistamine|statin|antibiotic|medication|drug|calcium|vitamin)",
                    r"(?:contains|composed of)\s+([a-z\-]+)"
                ]
                for pattern in patterns:
                    match = re.search(pattern, extract)
                    if match:
                        matched_word = match.group(1).strip()
                        common_words = ["medication", "drug", "medicine", "brand", "generic", "active", "the", "an", "a"]
                        if matched_word not in common_words and len(matched_word) > 3:
                            return matched_word
                title = data.get("title", "").lower()
                desc = data.get("description", "").lower()
                if any(t in desc for t in ["medication", "drug", "inhibitor", "antibiotic", "compound", "treatment"]):
                    return title
    except Exception as e:
        logger.error(f"Wikipedia query failed: {e}")
    return None

def query_rxnav_formula(medicine_name: str):
    try:
        quoted = urllib.parse.quote(medicine_name)
        url_direct = f"https://rxnav.nlm.nih.gov/REST/rxcui.json?name={quoted}"
        req = urllib.request.Request(url_direct, headers={'User-Agent': 'Mozilla/5.0'})
        rxcui = None
        with urllib.request.urlopen(req, timeout=3) as res:
            if res.status == 200:
                data = json.loads(res.read().decode('utf-8'))
                rxnorm_id = data.get("idGroup", {}).get("rxnormId")
                if rxnorm_id:
                    rxcui = rxnorm_id[0]
                    
        if not rxcui:
            url_approx = f"https://rxnav.nlm.nih.gov/REST/approximateTerm.json?term={quoted}&maxEntries=1"
            req_approx = urllib.request.Request(url_approx, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req_approx, timeout=3) as res:
                if res.status == 200:
                    data = json.loads(res.read().decode('utf-8'))
                    candidate = data.get("approximateGroup", {}).get("candidate", [])
                    if candidate:
                        rxcui = candidate[0].get("rxcui")
                        
        if rxcui:
            rel_url = f"https://rxnav.nlm.nih.gov/REST/rxcui/{rxcui}/allrelated.json"
            rel_req = urllib.request.Request(rel_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(rel_req, timeout=3) as rel_res:
                if rel_res.status == 200:
                    rel_data = json.loads(rel_res.read().decode('utf-8'))
                    concept_groups = rel_data.get("allRelatedGroup", {}).get("conceptGroup", [])
                    ingredients = []
                    for cg in concept_groups:
                        if cg.get("tty") == "IN":
                            concept = cg.get("conceptProperties", [])
                            for c in concept:
                                name = c.get("name")
                                if name:
                                    ingredients.append(name.lower())
                    if ingredients:
                        return " + ".join(sorted(list(set(ingredients))))
    except Exception as e:
        logger.error(f"RxNav query failed: {e}")
    return None

def fetch_global_brand_alternatives(formula: str):
    suggestions = set()
    formulas_to_query = [formula]
    if formula in synonym_map:
        formulas_to_query.append(synonym_map[formula])
        
    for f in formulas_to_query:
        try:
            quoted = urllib.parse.quote(f)
            url_drugs = f"https://rxnav.nlm.nih.gov/REST/drugs.json?name={quoted}"
            req = urllib.request.Request(url_drugs, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3) as res:
                if res.status == 200:
                    data = json.loads(res.read().decode('utf-8'))
                    concept_groups = data.get("drugGroup", {}).get("conceptGroup", [])
                    for cg in concept_groups:
                        for prop in cg.get("conceptProperties", []):
                            name = prop.get("name", "")
                            match = re.search(r'\[(.*?)\]', name)
                            if match:
                                brand_name = match.group(1).split('/')[-1].split(' ')[0].strip()
                                brand_name = re.sub(r'[^a-zA-Z0-9\s-]', '', brand_name)
                                if len(brand_name) > 3 and not brand_name.lower().startswith(f.lower()[:4]):
                                    suggestions.add(brand_name.capitalize())
        except Exception as e:
            logger.error(f"RxNav drugs query failed for {f}: {e}")

        try:
            quoted = urllib.parse.quote(f)
            url_rxcui = f"https://rxnav.nlm.nih.gov/REST/rxcui.json?name={quoted}"
            req = urllib.request.Request(url_rxcui, headers={'User-Agent': 'Mozilla/5.0'})
            rxcui = None
            with urllib.request.urlopen(req, timeout=3) as res:
                if res.status == 200:
                    data = json.loads(res.read().decode('utf-8'))
                    rxnorm_id = data.get("idGroup", {}).get("rxnormId")
                    if rxnorm_id:
                        rxcui = rxnorm_id[0]
            
            if not rxcui:
                url_approx = f"https://rxnav.nlm.nih.gov/REST/approximateTerm.json?term={quoted}&maxEntries=1"
                req_approx = urllib.request.Request(url_approx, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req_approx, timeout=3) as res:
                    if res.status == 200:
                        data = json.loads(res.read().decode('utf-8'))
                        candidate = data.get("approximateGroup", {}).get("candidate", [])
                        if candidate:
                            rxcui = candidate[0].get("rxcui")
                            
            if rxcui:
                url_brands = f"https://rxnav.nlm.nih.gov/REST/Prescribe/brands.json?ingredientids={rxcui}"
                req_brands = urllib.request.Request(url_brands, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req_brands, timeout=3) as res:
                    if res.status == 200:
                        data = json.loads(res.read().decode('utf-8'))
                        brand_list = data.get("brandGroup", {}).get("conceptProperties", [])
                        for b in brand_list:
                            bname = b.get("name")
                            if bname and len(bname) > 3:
                                suggestions.add(bname.capitalize())
        except Exception as e:
            logger.error(f"RxNav Prescribe brands query failed for {f}: {e}")

    suggestions = {s for s in suggestions if s.lower() != formula.lower()}
    return list(suggestions)
