"""
Bank Statement Profiles and Configuration.
Defines column mappings, number formats, date parsing rules, and locale conventions.
Includes specific support for the Bank Muscat BRD requirements.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class ColumnDef:
    label: str
    role: str  # 'date', 'value_date', 'description', 'reference', 'debit', 'credit', 'amount', 'balance', 'counterparty'
    aliases: List[str] = field(default_factory=list)


@dataclass
class BankProfile:
    id: str
    name: str
    country: str
    currency: str
    currency_decimals: int = 2
    decimal_separator: str = "."
    thousands_separator: str = ","
    direction_derivation: str = "separate-columns"  # 'separate-columns', 'sign-derived'
    negative_sign: str = "leading-minus"            # 'leading-minus', 'parentheses', 'trailing-minus'
    sign_to_direction: str = "negative-is-debit"     # 'negative-is-debit', 'negative-is-credit'
    date_format: str = "DD/MM/YYYY"
    date_columns: List[str] = field(default_factory=lambda: ["Date"])
    header_keywords: List[str] = field(default_factory=list)
    description_embedded_date: bool = False
    multi_account: bool = False


# Supported Statement Profiles
PROFILES: Dict[str, BankProfile] = {
    # Bank Muscat BRD Requirements Profile (Sultanate of Oman)
    "bank_muscat": BankProfile(
        id="bank_muscat",
        name="Bank Muscat",
        country="OM",
        currency="OMR",
        currency_decimals=3,  # Omani Rial has 3 decimal places (1 OMR = 1000 Baiza)
        decimal_separator=".",
        thousands_separator=",",
        direction_derivation="separate-columns",
        date_format="DD/MM/YYYY",
        header_keywords=[
            "bank muscat", "bankmuscat", "بنك مسقط", "bank muscat saog"
        ],
        multi_account=False
    ),

    # Benchmark bsb-001: Straits Capital (Singapore)
    "straits_capital": BankProfile(
        id="straits_capital",
        name="Straits Capital",
        country="SG",
        currency="SGD",
        currency_decimals=2,
        decimal_separator=".",
        thousands_separator=",",
        direction_derivation="separate-columns",
        date_format="DD/MM/YYYY",
        header_keywords=["straits capital", "straits-capital", "sc savings account"],
        multi_account=False
    ),

    # Benchmark bsb-002: Liberty National Bank (US Credit Card)
    "liberty_national": BankProfile(
        id="liberty_national",
        name="Liberty National Bank",
        country="US",
        currency="USD",
        currency_decimals=2,
        decimal_separator=".",
        thousands_separator=",",
        direction_derivation="sign-derived",
        negative_sign="leading-minus",
        sign_to_direction="negative-is-credit",  # In credit card statements: positive = charge/debit, negative = credit/payment
        date_format="MM/DD",
        header_keywords=["liberty national bank", "post date", "trans date", "merchant name"],
        multi_account=False
    ),

    # Benchmark bsb-003: Continental Trust (Netherlands)
    "continental_trust": BankProfile(
        id="continental_trust",
        name="Continental Trust",
        country="NL",
        currency="EUR",
        currency_decimals=2,
        decimal_separator=",",
        thousands_separator=".",
        direction_derivation="sign-derived",
        negative_sign="leading-minus",
        sign_to_direction="negative-is-debit",
        date_format="D MMM",
        header_keywords=["continental trust", "rekeningafschrift", "tegenrekening", "counterparty"],
        multi_account=False
    ),

    # Benchmark bsb-004: Silk Road Banking (Hong Kong Multi-Account)
    "silk_road": BankProfile(
        id="silk_road",
        name="Silk Road Banking",
        country="HK",
        currency="HKD",
        currency_decimals=2,
        decimal_separator=".",
        thousands_separator=",",
        direction_derivation="separate-columns",
        date_format="D MMM",
        header_keywords=["silk road", "絲路銀行", "business direct statement", "進支詳情"],
        multi_account=True
    ),

    # Benchmark bsb-005: Harbour Bank (Canada - French)
    "harbour_bank": BankProfile(
        id="harbour_bank",
        name="Harbour Bank",
        country="CA",
        currency="CAD",
        currency_decimals=2,
        decimal_separator=",",
        thousands_separator=" ",
        direction_derivation="separate-columns",
        date_format="DD MMM YY",
        header_keywords=["harbour bank", "relevé bancaire", "chèques et débits", "dépôts et crédits"],
        description_embedded_date=True,
        multi_account=False
    ),

    # Generic Auto-Detect Profile
    "generic": BankProfile(
        id="generic",
        name="Generic Statement Parser",
        country="GLOBAL",
        currency="USD",
        currency_decimals=2,
        decimal_separator=".",
        thousands_separator=",",
        direction_derivation="separate-columns",
        date_format="DD/MM/YYYY",
        header_keywords=[],
        multi_account=False
    )
}


def get_profile(profile_id: str) -> BankProfile:
    """Retrieve profile by ID, falling back to generic."""
    return PROFILES.get(profile_id.lower(), PROFILES["generic"])


def detect_profile_from_text(text: str) -> BankProfile:
    """Detect matching profile from raw document text."""
    text_lower = text.lower()
    for pid, profile in PROFILES.items():
        if pid == "generic":
            continue
        for kw in profile.header_keywords:
            if kw.lower() in text_lower:
                return profile
    return PROFILES["generic"]
