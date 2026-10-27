"""
Unit tests for data normalization and parsing routines.
"""

import pytest
from app.validation.normalizer import (
    normalize_amount_str,
    parse_date_to_iso,
    extract_embedded_date_and_description
)


def test_normalize_amount_standard():
    assert normalize_amount_str("1,234.56") == 1234.56
    assert normalize_amount_str("50.00") == 50.0
    assert normalize_amount_str("0.50") == 0.5


def test_normalize_amount_european():
    assert normalize_amount_str("1.234,56", decimal_sep=",", thousands_sep=".") == 1234.56
    assert normalize_amount_str("37,04 €", decimal_sep=",", thousands_sep=".") == 37.04
    assert normalize_amount_str("-890,43 €", decimal_sep=",", thousands_sep=".") == -890.43


def test_normalize_amount_french_canadian():
    assert normalize_amount_str("10 750,00 $", decimal_sep=",", thousands_sep=" ") == 10750.0
    assert normalize_amount_str("1 895,80 $", decimal_sep=",", thousands_sep=" ") == 1895.80


def test_normalize_amount_bank_muscat_omr_3_decimals():
    # Omani Rial has 3 decimal places
    assert normalize_amount_str("850.500") == 850.5
    assert normalize_amount_str("45.250 OMR") == 45.25
    assert normalize_amount_str("0.500") == 0.5


def test_normalize_amount_negative_conventions():
    assert normalize_amount_str("-13.84") == -13.84
    assert normalize_amount_str("13.84-") == -13.84
    assert normalize_amount_str("(13.84)") == -13.84


def test_parse_date_iso():
    assert parse_date_to_iso("2025-06-02") == "2025-06-02"
    assert parse_date_to_iso("2025/06/02") == "2025-06-02"


def test_parse_date_dmy():
    assert parse_date_to_iso("01/01/2025") == "2025-01-01"
    assert parse_date_to_iso("31/01/2025") == "2025-01-31"
    assert parse_date_to_iso("17-01-2025") == "2025-01-17"


def test_parse_date_partial_year_md():
    assert parse_date_to_iso("09/01", default_year=2025) == "2025-09-01"
    assert parse_date_to_iso("09/28", default_year=2025) == "2025-09-28"


def test_parse_date_text_month_en():
    assert parse_date_to_iso("27 Jun", default_year=2025) == "2025-06-27"
    assert parse_date_to_iso("1 Jul", default_year=2025) == "2025-07-01"


def test_parse_date_text_month_dutch():
    assert parse_date_to_iso("22 mei", default_year=2025) == "2025-05-22"
    assert parse_date_to_iso("24 mei", default_year=2025) == "2025-05-24"


def test_parse_date_text_month_french():
    assert parse_date_to_iso("21 janv. 25") == "2025-01-21"
    assert parse_date_to_iso("26 janv. 25") == "2025-01-26"


def test_parse_date_buddhist_era():
    # 2568 BE = 2025 CE
    assert parse_date_to_iso("15/01/2568") == "2025-01-15"


def test_extract_embedded_date_and_description():
    text = "21 janv. 25 UBER COURSE NYC"
    d, desc = extract_embedded_date_and_description(text)
    assert d == "2025-01-21"
    assert desc == "UBER COURSE NYC"
