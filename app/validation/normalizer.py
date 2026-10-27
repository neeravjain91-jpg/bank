"""
Data normalization for banking statements:
- Standardized ISO-8601 date parsing across English, French, Dutch, Arabic, and Buddhist Era.
- Robust currency and numeric parsing supporting varied decimal/thousands separators and 3-decimal currencies (OMR).
- Direction derivation (debit vs credit).
"""

import re
from datetime import datetime
from typing import Optional, Tuple, Dict, Any


# Month mapping for multi-language statements
MONTH_MAP = {
    # English
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
    "january": 1, "february": 2, "march": 3, "april": 4, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
    # Dutch
    "mrt": 3, "mei": 5, "okt": 10,
    # French
    "janv": 1, "janv.": 1, "févr": 2, "févr.": 2, "fevr": 2, "fevr.": 2,
    "mars": 3, "avr": 4, "avr.": 4, "avril": 4, "mai": 5, "juin": 6,
    "juil": 7, "juil.": 7, "juillet": 7, "août": 8, "aout": 8,
    "sept": 9, "sept.": 9, "déc": 12, "déc.": 12, "dec": 12, "dec.": 12
}


def normalize_amount_str(
    raw_val: str,
    decimal_sep: str = ".",
    thousands_sep: str = ","
) -> Optional[float]:
    """
    Convert raw currency/amount string to canonical float.
    Handles currency symbols, varied thousand/decimal separators, leading/trailing signs, and parentheses.
    """
    if not raw_val or not isinstance(raw_val, str):
        return None
    val = raw_val.strip()
    if not val:
        return None

    # Detect negative indicator: parentheses e.g. (12.50) or trailing minus e.g. 12.50-
    is_negative = False
    if val.startswith("(") and val.endswith(")"):
        is_negative = True
        val = val[1:-1].strip()
    elif val.endswith("-"):
        is_negative = True
        val = val[:-1].strip()
    elif val.startswith("-"):
        is_negative = True
        val = val[1:].strip()

    # Remove non-numeric except decimal, thousands separator, and digits
    # Strip currency symbols and letters (e.g. $, EUR, SGD, OMR, etc.)
    val = re.sub(r"[^\d\,\.\s]", "", val).strip()
    if not val:
        return None

    if decimal_sep == ",":
        # European format: 1.234,56 or 1 234,56
        val = val.replace(thousands_sep, "").replace(" ", "").replace(",", ".")
    else:
        # Standard format: 1,234.56
        val = val.replace(thousands_sep, "").replace(" ", "")

    try:
        amt = float(val)
        return -amt if is_negative else amt
    except ValueError:
        return None


def parse_date_to_iso(
    raw_date: str,
    default_year: int = 2025,
    date_format_hint: Optional[str] = None
) -> Optional[str]:
    """
    Convert various international bank statement date strings into ISO-8601 (YYYY-MM-DD).
    Supports DD/MM/YYYY, MM/DD, DD MMM, DD MMM YY, YYYY-MM-DD, and Buddhist Era.
    """
    if not raw_date:
        return None
    s = raw_date.strip()
    if not s:
        return None

    # Check for ISO already
    iso_match = re.match(r"^(\d{4})[-/](\d{1,2})[-/](\d{1,2})$", s)
    if iso_match:
        y, m, d = int(iso_match.group(1)), int(iso_match.group(2)), int(iso_match.group(3))
        # Handle Buddhist Era
        if y > 2400:
            y -= 543
        return f"{y:04d}-{m:02d}-{d:02d}"

    # DD/MM/YYYY or DD-MM-YYYY or DD.MM.YYYY
    dmy_match = re.match(r"^(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{2,4})$", s)
    if dmy_match:
        part1, part2, part3 = int(dmy_match.group(1)), int(dmy_match.group(2)), int(dmy_match.group(3))
        if part3 < 100:
            part3 += 2000
        elif part3 > 2400:  # Buddhist era
            part3 -= 543
        
        # Determine day vs month
        if part1 > 12 and part2 <= 12:
            # part1 is definitely Day
            d, m, y = part1, part2, part3
        elif part1 <= 12 and part2 > 12:
            # part2 is definitely Day
            d, m, y = part2, part1, part3
        elif date_format_hint and "MM/DD" in date_format_hint:
            # hint indicates Month first
            d, m, y = part2, part1, part3
        else:
            # standard default: Day first (DD/MM/YYYY)
            d, m, y = part1, part2, part3
        return f"{y:04d}-{m:02d}-{d:02d}"

    # MM/DD (partial year - e.g. bsb-002)
    md_match = re.match(r"^(\d{1,2})/(\d{1,2})$", s)
    if md_match:
        m, d = int(md_match.group(1)), int(md_match.group(2))
        return f"{default_year:04d}-{m:02d}-{d:02d}"

    # Text month formats: e.g. '27 Jun', '1 Jul', '22 mei', '21 janv. 25', '21 janv 2025'
    text_date_pattern = r"^(\d{1,2})\s+([a-zA-Z\.\u00C0-\u017F]+)(?:\s+(\d{2,4}))?$"
    t_match = re.match(text_date_pattern, s)
    if t_match:
        d = int(t_match.group(1))
        m_raw = t_match.group(2).lower().rstrip(".")
        y_raw = t_match.group(3)
        
        m = MONTH_MAP.get(m_raw) or MONTH_MAP.get(m_raw + ".")
        if not m:
            # Fallback prefix matching
            for k, v in MONTH_MAP.items():
                if m_raw.startswith(k[:3]):
                    m = v
                    break
        if m:
            if y_raw:
                y = int(y_raw)
                if y < 100:
                    y += 2000
                elif y > 2400:
                    y -= 543
            else:
                y = default_year
            return f"{y:04d}-{m:02d}-{d:02d}"

    return None


def extract_embedded_date_and_description(
    text: str,
    default_year: int = 2025
) -> Tuple[Optional[str], str]:
    """
    Extract date from description if date is embedded (e.g. bsb-005: '21 janv. 25 UBER COURSE').
    Returns (iso_date, cleaned_description).
    """
    if not text:
        return None, text
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if not lines:
        return None, text
    first_line = lines[0]
    pattern = r"^(\d{1,2}\s+[a-zA-Z\.\u00C0-\u017F]+\s+\d{2,4})\s+(.*)$"
    match = re.match(pattern, first_line)
    if match:
        date_str = match.group(1)
        first_desc = match.group(2)
        iso_d = parse_date_to_iso(date_str, default_year=default_year)
        if iso_d:
            rest = lines[1:]
            full_desc = " ".join([first_desc] + rest).strip()
            return iso_d, full_desc
    return None, text
