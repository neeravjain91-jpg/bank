"""
Integration tests for the complete extraction pipeline across benchmark statements and Bank Muscat.
"""

import os
import pytest
from app.services.extractor import StatementExtractorService


@pytest.fixture(scope="module")
def extractor():
    return StatementExtractorService()


def test_extract_bsb001_straits_capital(extractor):
    pdf = "data/bankstatemently_benchmark/datasets/basic/bsb-001/bsb-001-statement.pdf"
    if not os.path.exists(pdf):
        pytest.skip("Benchmark statement not available")
    res = extractor.extract_from_path(pdf, profile_id="auto")
    assert res.metadata.transaction_count == 12
    assert res.metadata.profile_used == "straits_capital"
    assert res.validation.reconciled is True
    assert res.validation.total_debits == 2181.67
    assert res.validation.total_credits == 2002.15


def test_extract_bsb002_liberty_national(extractor):
    pdf = "data/bankstatemently_benchmark/datasets/basic/bsb-002/bsb-002-statement.pdf"
    if not os.path.exists(pdf):
        pytest.skip("Benchmark statement not available")
    res = extractor.extract_from_path(pdf, profile_id="auto")
    assert res.metadata.transaction_count == 15
    assert res.metadata.profile_used == "liberty_national"
    assert res.validation.reconciled is True


def test_extract_bsb003_continental_trust(extractor):
    pdf = "data/bankstatemently_benchmark/datasets/basic/bsb-003/bsb-003-statement.pdf"
    if not os.path.exists(pdf):
        pytest.skip("Benchmark statement not available")
    res = extractor.extract_from_path(pdf, profile_id="auto")
    assert res.metadata.transaction_count == 22
    assert res.metadata.profile_used == "continental_trust"
    assert res.validation.reconciled is True


def test_extract_bsb004_silk_road(extractor):
    pdf = "data/bankstatemently_benchmark/datasets/basic/bsb-004/bsb-004-statement.pdf"
    if not os.path.exists(pdf):
        pytest.skip("Benchmark statement not available")
    res = extractor.extract_from_path(pdf, profile_id="auto")
    assert res.metadata.transaction_count == 25
    assert res.metadata.profile_used == "silk_road"
    assert res.validation.reconciled is True


def test_extract_bsb005_harbour_bank(extractor):
    pdf = "data/bankstatemently_benchmark/datasets/basic/bsb-005/bsb-005-statement.pdf"
    if not os.path.exists(pdf):
        pytest.skip("Benchmark statement not available")
    res = extractor.extract_from_path(pdf, profile_id="auto")
    assert res.metadata.transaction_count == 25
    assert res.metadata.profile_used == "harbour_bank"
    assert res.validation.reconciled is True


def test_extract_bank_muscat_sample(extractor):
    pdf = "data/raw/bank_muscat_sample.pdf"
    if not os.path.exists(pdf):
        from scripts.generate_bank_muscat_sample import generate_bank_muscat_pdf
        generate_bank_muscat_pdf(pdf)
    
    res = extractor.extract_from_path(pdf, profile_id="auto")
    assert res.metadata.bank == "Bank Muscat"
    assert res.metadata.profile_used == "bank_muscat"
    assert res.metadata.currency == "OMR"
    assert res.metadata.transaction_count == 7
    assert res.validation.reconciled is True
    assert res.validation.total_debits == 221.500
    assert res.validation.total_credits == 921.000


def test_csv_serialization(extractor):
    pdf = "data/bankstatemently_benchmark/datasets/basic/bsb-001/bsb-001-statement.pdf"
    if not os.path.exists(pdf):
        pytest.skip("Benchmark statement not available")
    res = extractor.extract_from_path(pdf)
    csv_str = StatementExtractorService.to_csv(res)
    assert "date,value_date,description,amount,direction" in csv_str
    assert "2025-01-01" in csv_str
    assert "1902.690" in csv_str
