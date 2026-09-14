"""
Unit Tests for Governed Data Transformation and Cleaning Functions
"""

import pytest
import pandas as pd
import numpy as np
from src.transformations import (
    normalize_user_id,
    normalize_merchant_id,
    normalize_txn_id,
    normalize_complaint_id,
    clean_amount_governed,
    parse_datetime_governed,
    validate_pan_governed,
    validate_aadhaar_governed,
    normalize_txn_status,
    normalize_kyc_status,
    normalize_merchant_status,
    normalize_severity_governed
)


def test_id_normalization():
    assert normalize_user_id("usr12345") == "USR12345"
    assert normalize_user_id("USR-12345") == "USR12345"
    assert normalize_user_id("USR 12345") == "USR12345"
    assert normalize_user_id("12345") == "USR12345"
    
    assert normalize_merchant_id("mch1234") == "MCH1234"
    assert normalize_merchant_id("MCH-1234") == "MCH1234"
    assert normalize_merchant_id("1234") == "MCH1234"

    assert normalize_txn_id("txn-00003119") == "TXN00003119"
    assert normalize_txn_id("TXN65742") == "TXN00065742"

    assert normalize_complaint_id("CBK0002082") == "CBK0002082"


def test_amount_cleaning_governed():
    # Regular positive amounts
    val1, is_neg1, is_inv1, status1 = clean_amount_governed("₹1,949.60")
    assert val1 == 1949.60 and not is_neg1 and status1 == "VALID_PARSED"

    val2, is_neg2, is_inv2, status2 = clean_amount_governed("Rs. 7,039")
    assert val2 == 7039.00 and not is_neg2 and status2 == "VALID_PARSED"

    # Negative amount preservation (DO NOT USE abs())
    val3, is_neg3, is_inv3, status3 = clean_amount_governed("-956.46")
    assert val3 == -956.46 and is_neg3 and status3 == "VALID_PARSED"

    # k-notation
    val4, is_neg4, is_inv4, status4 = clean_amount_governed("27.3k")
    assert val4 == 27300.00 and not is_neg4

    # Missing / empty string
    val5, is_neg5, is_inv5, status5 = clean_amount_governed("")
    assert val5 is None and status5 == "MISSING"


def test_datetime_parsing_governed():
    dt1, status1, amb1, inv1 = parse_datetime_governed("2026-01-15 00:11:30")
    assert dt1.year == 2026 and dt1.month == 1 and dt1.day == 15 and status1 == "VALID_DATETIME"

    dt2, status2, amb2, inv2 = parse_datetime_governed("1770063471")
    assert pd.notnull(dt2) and status2 == "VALID_EPOCH"

    dt3, status3, amb3, inv3 = parse_datetime_governed("25/02/2026 10:24 AM")
    assert dt3.year == 2026 and dt3.month == 2 and dt3.day == 25


def test_pan_and_aadhaar_validation():
    # Valid PAN
    raw1, norm1, stat1 = validate_pan_governed("SEJAA8194O")
    assert stat1 == "VALID_PAN" and norm1 == "SEJAA8194O"

    # Malformed PAN (without destructive char replacement)
    raw2, norm2, stat2 = validate_pan_governed("QT0ZZ5561X")
    assert stat2 == "MALFORMED_STRUCTURE_OCR_SUSPECT" and norm2 == "QT0ZZ5561X"

    # Valid Aadhaar
    raw3, norm3, stat3 = validate_aadhaar_governed("2781 6299 9816")
    assert stat3 == "VALID_AADHAAR" and norm3 == "278162999816"


def test_status_and_severity():
    assert normalize_txn_status("COMPLETED") == "SUCCESS"
    assert normalize_txn_status("TXN_FAILED") == "FAILED"
    assert normalize_txn_status("PROCESSING") == "PENDING"

    assert normalize_kyc_status("APPROVED") == "VERIFIED"
    assert normalize_kyc_status("Under Review") == "PENDING"
    assert normalize_kyc_status("Rejected") == "REJECTED"

    assert normalize_severity_governed("CRITICAL") == "CRITICAL"
    assert normalize_severity_governed("P1") == "CRITICAL"
    assert normalize_severity_governed("P2") == "HIGH"
    assert normalize_severity_governed("H") == "HIGH"
    assert normalize_severity_governed("P3") == "MEDIUM"
    assert normalize_severity_governed("P4") == "LOW"
