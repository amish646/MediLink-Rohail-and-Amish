class OcrFuzzyMatcher:
    @staticmethod
    def levenshtein_distance(s1, s2):
        if len(s1) < len(s2):
            return OcrFuzzyMatcher.levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
            
        return previous_row[-1]

    @staticmethod
    def fuzzy_match_brand(word, known_brands, log_callback=None):
        word_low = word.lower().strip()
        if not word_low or len(word_low) < 3:
            return None
            
        best_match = None
        min_dist = 999
        
        for brand in known_brands.keys():
            dist = OcrFuzzyMatcher.levenshtein_distance(word_low, brand)
            threshold = 2 if len(brand) > 5 else 1
            if dist <= threshold and dist < min_dist:
                min_dist = dist
                best_match = brand
                
        if best_match:
            matched_brand, matched_formula = known_brands[best_match]
            if min_dist > 0 and log_callback:
                log_callback(f"Fuzzy Auto-Corrected: '{word}' -> '{matched_brand}' (edit distance: {min_dist})")
            return matched_brand, matched_formula
        return None
