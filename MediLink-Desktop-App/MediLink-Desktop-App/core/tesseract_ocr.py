import os
import re
import cv2
import pytesseract
from PIL import Image
from core.fuzzy_matching import OcrFuzzyMatcher
from core.text_parser import OcrTextParser

class OcrTesseractRunner:
    @classmethod
    def run_tesseract_ocr(cls, image_path, known_brands, log_callback):
        tess_cmd = pytesseract.pytesseract.tesseract_cmd
        if not os.path.exists(tess_cmd):
            raise FileNotFoundError(
                f"Tesseract engine executable not found at: {tess_cmd}\n"
                "Please configure and install Tesseract OCR."
            )

        img_cv = cv2.imread(image_path)
        if img_cv is not None:
            img_h, img_w = img_cv.shape[:2]
            target_h = 1500
            scale = target_h / img_h
            target_w = int(img_w * scale)
            resized = cv2.resize(img_cv, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            denoised = cv2.fastNlMeansDenoising(gray, h=10, templateWindowSize=7, searchWindowSize=21)
            img = Image.fromarray(denoised)
            img_w, img_h = img.size
        else:
            img = Image.open(image_path).convert("RGB")
            img_w, img_h = img.size
            if img_w < 1200:
                scale = 1200 / img_w
                img = img.resize((int(img_w * scale), int(img_h * scale)), Image.LANCZOS)
                img_w, img_h = img.size

        if log_callback:
            log_callback(f"Tesseract scanning {img_w}x{img_h} image using PSM 3 & Y-clustering...")

        data = pytesseract.image_to_data(
            img,
            config="--psm 3",
            output_type=pytesseract.Output.DICT
        )

        n = len(data['text'])
        words = []
        for i in range(n):
            conf = int(data['conf'][i])
            text = str(data['text'][i]).strip()
            if conf < 30 or not text:
                continue
            words.append({
                'text':     text,
                'left':     data['left'][i],
                'top':      data['top'][i],
                'width':    data['width'][i],
                'height':   data['height'][i],
                'xcenter':  data['left'][i] + data['width'][i] / 2,
                'ycenter':  data['top'][i]  + data['height'][i] / 2,
            })

        if not words:
            if log_callback:
                log_callback("Tesseract returned no words.")
            return []

        words_sorted = sorted(words, key=lambda w: w['top'])
        clustered_rows = []

        for w in words_sorted:
            y_center = w['ycenter']
            h = w['height']
            tolerance = max(12, h * 0.6)

            placed = False
            for row in clustered_rows:
                avg_y = sum(word['ycenter'] for word in row) / len(row)
                if abs(y_center - avg_y) <= tolerance:
                    row.append(w)
                    placed = True
                    break

            if not placed:
                clustered_rows.append([w])

        sorted_rows = []
        for row in clustered_rows:
            row_sorted = sorted(row, key=lambda w: w['left'])
            sorted_rows.append(row_sorted)

        sorted_rows = sorted(sorted_rows, key=lambda r: sum(w['ycenter'] for w in r) / len(r))
        if log_callback:
            log_callback(f"Aligned words into {len(sorted_rows)} line rows.")

        skip_kw = {
            'total','subtotal','invoice','receipt','bill','cashier','customer',
            'address','phone','mobile','cash','change','balance','page','tel',
            'fax','email','website','signature','received','delivered','thank',
            'visit','tax','due','discount','disc','net','gross','vat','gst',
            'batch','b.no','serial','s.no','mfg','lic','buyer','seller',
            'patient','slip','payment','terms','conditions','warranty',
        }

        items = []
        for row in sorted_rows:
            full_text = ' '.join(w['text'] for w in row)
            full_text_low = full_text.lower().strip()

            if not full_text or any(k in full_text_low for k in skip_kw):
                continue

            if not re.search(r'[A-Za-z]{3,}', full_text) or not re.search(r'\d', full_text):
                continue

            parsed = OcrTextParser.parse_fields_from_text(full_text, known_brands, log_callback)

            fuzzy_brand = parsed["brand_name"]
            for w in row:
                match = OcrFuzzyMatcher.fuzzy_match_brand(w['text'], known_brands, log_callback)
                if match:
                    fuzzy_brand, parsed["generic_formula"] = match
                    break

            parsed["brand_name"] = fuzzy_brand
            if parsed["brand_name"] == "Scanned Medicine" and parsed["retail_price"] == 100.0:
                continue

            items.append(parsed)
            if log_callback:
                log_callback(f"  ✔ {parsed['brand_name']} | Rs {parsed['retail_price']} | Qty {parsed['quantity']} | Exp {parsed['expiry_date']}")

        return items
