
import re
import logging
from datetime import datetime
from typing import List, Optional

from dateutil import parser
from dateutil.relativedelta import relativedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_experience(text: str) -> float:
    """
    Extracts the total years of experience from the resume text.
    It combines regex pattern matching for explicit mentions and 
    date duration calculation.
    
    Args:
        text (str): Resume text.
        
    Returns:
        float: Total years of experience (rounded to 1 decimal). Returns 0.0 if fresher.
    """
    regex_exp = extract_experience_from_regex(text)
    date_exp = extract_experience_from_dates(text)
    
    logger.info(f"Experience Extraction - Regex: {regex_exp}, Date-Calculated: {date_exp}")
    
    # Return the maximum reasonable value found
    # If explicit mention is "5+" but dates show "8", usually dates are more reliable if parsed correctly.
    # However, dates often have overlaps or gaps.
    # If difference is huge (e.g. 5 vs 20), rely on dates if > 0? 
    # Or simply take the maximum as resumes often summarize "Total 5 years" but dates might sum to 4.8.
    
    final_exp = max(regex_exp, date_exp)
    return round(final_exp, 1)

def extract_experience_from_regex(text: str) -> float:
    """
    Finds explicit mentions like "5 years experience", "5+ years".
    """
    # Pattern designed to capture:
    # "5 years", "5.5 years", "10+ years"
    # Usually at start of lines or phrases like "Total Experience: 5 years"
    
    # We look for digits followed by "year"
    # but filter out "2020 year" or "3 year degree" which are common false positives.
    
    # Look for specific phrases first
    phrases = [
        r'total experience[:\s-]*(\d+(?:\.\d+)?)\+?\s*years?',
        r'(\d+(?:\.\d+)?)\+?\s*years? of experience',
        r'experience[:\s-]*(\d+(?:\.\d+)?)\+?\s*years?'
    ]
    
    for pattern in phrases:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1))
            
    # Fallback: Just look for "X years" but be careful contextually?
    # Maybe too risky. "I am 20 years old" -> 20 years exp? NO.
    # Stick to specific phrases for regex.
    return 0.0

def extract_experience_from_dates(text: str) -> float:
    """
    Finds date ranges and sums up the duration.
    Text often contains: "Jan 2020 - Present", "01/2019 to 12/2021"
    """
    # Normalize text slightly for dates
    # Replace "Present", "Current", "Till Date" with current date text for parsing
    now = datetime.now()
    current_date_str = now.strftime("%b %Y") # e.g. "Jan 2026"
    
    normalized_text = re.sub(r'\b(present|current|till date|now)\b', current_date_str, text, flags=re.IGNORECASE)
    
    # Regex for finding date ranges
    # Supporting formats: 
    # Jan 2020 - Feb 2021
    # 01/2020 - 02/2021
    # 2020 - 2021
    
    month_regex = r'(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
    
    # Pattern 1: Month Year - Month Year
    # e.g. "Jan 2020 - Feb 2022" or "Jan 2020 to Feb 2022"
    pattern1 = rf'({month_regex}\s*\.?\s*\d{{4}})\s*(?:-|to)\s*({month_regex}\s*\.?\s*\d{{4}})'
    
    # Pattern 2: MM/YYYY - MM/YYYY
    pattern2 = r'(\d{1,2}/\d{4})\s*(?:-|to)\s*(\d{1,2}/\d{4})'
    
    # Pattern 3: YYYY - YYYY (Less accurate, assumes full years)
    pattern3 = r'\b(\d{4})\s*(?:-|to)\s*(\d{4})\b'
    
    matches = []
    matches.extend(re.findall(pattern1, normalized_text, re.IGNORECASE))
    matches.extend(re.findall(pattern2, normalized_text))
    # pattern3 often matches phone numbers (1234-5678), skip unless strictly surrounded?
    
    total_months = 0
    
    for start_str, end_str in matches:
        try:
            start_date = parser.parse(start_str)
            end_date = parser.parse(end_str)
            
            # Simple validity check
            if start_date > end_date:
                continue # Skip invalid ranges
                
            # Calculate difference in months
            diff = relativedelta(end_date, start_date)
            months = diff.years * 12 + diff.months
            
            # Minimum 1 month if stated
            if months == 0: months = 1
            
            total_months += months
            
        except (ValueError, TypeError):
            continue

    return total_months / 12.0

if __name__ == "__main__":
    # Test cases
    test_resume1 = """
    John Doe
    Total Experience: 5.5 years
    Employment History:
    Jan 2020 - Present: Senior Dev
    Jan 2018 - Dec 2019: Junior Dev
    """
    
    test_resume2 = """
    Jane Smith
    Fresher, recently graduated using Python.
    """
    
    test_resume3 = """
    Work Experience:
    01/2019 - 01/2022: Company A
    """
    
    print(f"Resume 1 Exp: {extract_experience(test_resume1)} (Expected ~ >5)")
    print(f"Resume 2 Exp: {extract_experience(test_resume2)} (Expected 0.0)")
    print(f"Resume 3 Exp: {extract_experience(test_resume3)} (Expected 3.0)")
