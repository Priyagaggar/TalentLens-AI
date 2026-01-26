
import re
from datetime import datetime

class BiasDetector:
    def __init__(self):
        # Trigger words
        self.gender_indicators = {
            "masculine": ["he", "him", "his", "man", "men", "male", "chairman", "waiter", "steward", "policeman"],
            "feminine": ["she", "her", "hers", "woman", "women", "female", "chairwoman", "waitress", "stewardess", "policewoman"]
        }
        
    def analyze_bias(self, text: str) -> dict:
        """
        Analyzes the text for potential sources of bias.
        """
        bias_report = {
            "detected_issues": [],
            "recommendations": [],
            "anonymization_suggestions": []
        }
        
        # 1. Gender Bias Check
        gender_issues = self._check_gender_cues(text)
        if gender_issues:
            bias_report["detected_issues"].extend(gender_issues)
            bias_report["recommendations"].append("Consider using gender-neutral pronouns (they/them) or titles (Chairperson, Server).")

        # 2. Age Bias Check
        age_issues = self._check_age_indicators(text)
        if age_issues:
            bias_report["detected_issues"].extend(age_issues)
            bias_report["recommendations"].append("Remove graduation dates older than 10-15 years to prevent age bias.")
            bias_report["anonymization_suggestions"].extend([f"Remove '{issue}'" for issue in age_issues])

        return bias_report

    def _check_gender_cues(self, text: str) -> list:
        found_cues = []
        lower_text = text.lower()
        words = re.findall(r'\b\w+\b', lower_text)
        
        for word in words:
            if word in self.gender_indicators["masculine"]:
                found_cues.append(f"Masculine Term: {word}")
            elif word in self.gender_indicators["feminine"]:
                found_cues.append(f"Feminine Term: {word}")
        
        # Deduplicate
        return list(set(found_cues))

    def _check_age_indicators(self, text: str) -> list:
        found_indicators = []
        
        # Check for graduation years explicitly
        # Look for patterns like "Class of 1990", "Graduated 1990", "BS 1990"
        # Or just 4 digit years.
        
        current_year = datetime.now().year
        # Find all years 1950-2015 (Assuming 2015 is ~10 years ago, roughly)
        # Actually finding any year implies potential bias if it's the graduation year.
        # Let's search for "19\d{2}"
        
        years = re.findall(r'\b(19\d{2}|20[0-1][0-9])\b', text)
        for year in years:
            year_int = int(year)
            # If year is seemingly a graduation year (e.g. older than 15 years from now)
            # 2026 - 15 = 2011.
            if year_int < (current_year - 15):
                found_indicators.append(f"Year {year} (Potential Age Trigger)")
                
        return list(set(found_indicators))
