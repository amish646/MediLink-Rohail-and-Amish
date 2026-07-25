from core.fuzzy_matching import OcrFuzzyMatcher
from core.text_parser import OcrTextParser
from core.tesseract_ocr import OcrTesseractRunner
from core.gemini_ocr import OcrGeminiRunner

class OcrEngine:
    def __init__(self):
        pass

    @staticmethod
    def levenshtein_distance(s1, s2):
        return OcrFuzzyMatcher.levenshtein_distance(s1, s2)

    @staticmethod
    def fuzzy_match_brand(word, known_brands, log_callback=None):
        return OcrFuzzyMatcher.fuzzy_match_brand(word, known_brands, log_callback)

    @staticmethod
    def is_inventory_line(line_text):
        return OcrTextParser.is_inventory_line(line_text)

    @staticmethod
    def clean_ocr_number(num_str):
        return OcrTextParser.clean_ocr_number(num_str)

    @staticmethod
    def parse_fields_from_text(text, known_brands, log_callback=None,
                                base_brand=None, base_formula=None, base_price=None, base_qty=None, base_expiry=None):
        return OcrTextParser.parse_fields_from_text(
            text, known_brands, log_callback, base_brand, base_formula, base_price, base_qty, base_expiry
        )

    @staticmethod
    def run_tesseract_ocr(image_path, known_brands, log_callback):
        return OcrTesseractRunner.run_tesseract_ocr(image_path, known_brands, log_callback)

    @staticmethod
    def run_gemini_ai_ocr(image_path, gemini_key):
        return OcrGeminiRunner.run_gemini_ai_ocr(image_path, gemini_key)
