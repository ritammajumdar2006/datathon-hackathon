"""
FRAUDNET AI - Data Transformation and Normalization Module
Governed & Audited Implementation
"""

import re
import pandas as pd
import numpy as np
import dateutil.parser


def normalize_user_id(val):
    if pd.isna(val) or str(val).strip() == '':
        return None
    s = str(val).strip().upper()
    nums = re.findall(r'\d+', s)
    if nums:
        return f"USR{int(nums[0]):05d}"
    return None


def normalize_merchant_id(val):
    if pd.isna(val) or str(val).strip() == '':
        return None
    s = str(val).strip().upper()
    nums = re.findall(r'\d+', s)
    if nums:
        return f"MCH{int(nums[0]):04d}"
    return None


def normalize_txn_id(val):
    if pd.isna(val) or str(val).strip() == '':
        return None
    s = str(val).strip().upper()
    nums = re.findall(r'\d+', s)
    if nums:
        return f"TXN{int(nums[0]):08d}"
    return None


def normalize_complaint_id(val):
    if pd.isna(val) or str(val).strip() == '':
        return None
    s = str(val).strip().upper()
    nums = re.findall(r'\d+', s)
    if nums:
        return f"CBK{int(nums[0]):07d}"
    return None


def clean_amount_governed(val):
    """
    Parses amount string preserving signedness (DO NOT USE abs()).
    Returns (amount_clean, negative_amount_flag, invalid_amount_flag, amount_parse_status)
    """
    if pd.isna(val) or str(val).strip() == '':
        return None, False, True, "MISSING"
    
    s = str(val).strip()
    is_negative = s.startswith('-') or ('-' in s and not any(c.isdigit() for c in s[:s.find('-')]))
    is_k = 'k' in s.lower()

    # Strip currency keywords and symbols but PRESERVE negative sign
    s_clean = re.sub(r'(?i)(?:rs|inr|usd|eur|rupees)\.?\s*', '', s)
    s_clean = re.sub(r'[₹â‚¹$€£kK\s]', '', s_clean)
    s_clean = s_clean.replace(',', '')

    try:
        val_f = float(s_clean)
        if is_k:
            val_f *= 1000.0
        
        # Round to 2 decimal places
        val_clean = round(val_f, 2)
        neg_flag = val_clean < 0
        return val_clean, neg_flag, False, "VALID_PARSED"
    except (ValueError, TypeError):
        return None, False, True, "INVALID_FORMAT"


def parse_datetime_governed(val):
    """
    Parses datetime with explicit status tracking and ambiguity flags.
    Returns (parsed_dt, timestamp_parse_status, timestamp_ambiguous_flag, timestamp_invalid_flag)
    """
    if pd.isna(val) or str(val).strip() == '':
        return pd.NaT, "MISSING", False, True
    
    s = str(val).strip()

    # 1. Unix Timestamp handling
    if s.isdigit():
        num = int(s)
        if 1000000000 <= num <= 2500000000:
            dt = pd.to_datetime(num, unit='s')
            return dt, "VALID_EPOCH", False, False
        elif 1000000000000 <= num <= 2500000000000:
            dt = pd.to_datetime(num, unit='ms')
            return dt, "VALID_EPOCH_MS", False, False
        else:
            return pd.NaT, "INVALID_EPOCH_OUT_OF_BOUNDS", False, True

    # 2. Check ambiguous date formats (e.g. 02/01/2026 vs 01/02/2026 where both day and month <= 12)
    ambiguous_flag = False
    m_slash = re.match(r'^(\d{1,2})[/-](\d{1,2})[/-](\d{4})', s)
    if m_slash:
        d1, d2 = int(m_slash.group(1)), int(m_slash.group(2))
        if 1 <= d1 <= 12 and 1 <= d2 <= 12 and d1 != d2:
            ambiguous_flag = True

    try:
        dt = dateutil.parser.parse(s, dayfirst=True)
        # Check impossible future dates (e.g. beyond 2030)
        if dt.year < 2020 or dt.year > 2030:
            return pd.NaT, "INVALID_YEAR_OUT_OF_RANGE", ambiguous_flag, True
        return dt, "VALID_DATETIME", ambiguous_flag, False
    except Exception:
        return pd.NaT, "INVALID_FORMAT", False, True


def validate_pan_governed(val):
    """
    Validates PAN format (5 letters, 4 digits, 1 letter) WITHOUT destructive character replacement.
    Returns (pan_raw, pan_normalized, pan_validity_status)
    """
    if pd.isna(val) or str(val).strip() == '':
        return None, None, "MISSING"
    
    raw = str(val).strip()
    clean = re.sub(r'[^A-Za-z0-9]', '', raw).upper()
    
    if len(clean) == 10 and re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', clean):
        return raw, clean, "VALID_PAN"
    elif len(clean) == 10:
        return raw, clean, "MALFORMED_STRUCTURE_OCR_SUSPECT"
    else:
        return raw, clean, f"INVALID_LENGTH_{len(clean)}"


def mask_pan(pan):
    if not pan or len(str(pan)) < 5:
        return 'XXXXX0000X'
    p = str(pan)
    return f"{p[:2]}XXXXXX{p[-2:]}"


def validate_aadhaar_governed(val):
    """
    Validates Aadhaar format (12 numeric digits) WITHOUT destructive replacement.
    Returns (aadhaar_raw, aadhaar_normalized, aadhaar_validity_status)
    """
    if pd.isna(val) or str(val).strip() == '':
        return None, None, "MISSING"
    
    raw = str(val).strip()
    clean = re.sub(r'[^0-9]', '', raw)
    
    if len(clean) == 12:
        return raw, clean, "VALID_AADHAAR"
    elif len(clean) == 13 and clean.startswith('0'):
        return raw, clean[1:], "VALID_AADHAAR_LEADING_ZERO_TRIMMED"
    else:
        return raw, clean, f"INVALID_LENGTH_{len(clean)}"


def mask_aadhaar(aadhaar):
    if not aadhaar or len(str(aadhaar)) < 4:
        return 'XXXXXXXX0000'
    a = str(aadhaar)
    return f"XXXXXXXX{a[-4:]}"


def normalize_txn_status(val):
    if pd.isna(val) or str(val).strip() == '':
        return 'UNKNOWN'
    s = str(val).strip().upper()
    if s in ['SUCCESS', 'S', 'TXN_SUCCESS', 'COMPLETED']:
        return 'SUCCESS'
    elif s in ['FAILED', 'F', 'FAIL', 'TXN_FAILED', 'DECLINED']:
        return 'FAILED'
    elif s in ['PENDING', 'P', 'PROCESSING', 'IN_PROGRESS', 'WIP']:
        return 'PENDING'
    return s


def normalize_kyc_status(val):
    if pd.isna(val) or str(val).strip() == '':
        return 'UNKNOWN'
    s = str(val).strip().upper()
    if s in ['VERIFIED', 'APPROVED', 'DONE', 'KYC_DONE', 'V']:
        return 'VERIFIED'
    elif s in ['PENDING', 'P', 'IN_PROGRESS', 'UNDER REVIEW', 'WIP']:
        return 'PENDING'
    elif s in ['REJECTED', 'R', 'REJECT', 'FAILED']:
        return 'REJECTED'
    return s


def normalize_risk_segment(val):
    if pd.isna(val) or str(val).strip() == '':
        return 'UNKNOWN'
    s = str(val).strip().upper()
    if s in ['LOW', 'MEDIUM', 'HIGH', 'UNKNOWN']:
        return s
    return 'UNKNOWN'


def normalize_merchant_status(val):
    if pd.isna(val) or str(val).strip() == '':
        return 'UNKNOWN'
    s = str(val).strip().upper()
    if s in ['ACTIVE', 'ENABLED', 'LIVE', 'A']:
        return 'ACTIVE'
    elif s in ['INACTIVE', 'DISABLED', 'CLOSED', 'I']:
        return 'INACTIVE'
    elif s in ['SUSPENDED', 'HOLD', 'S', 'BLOCKED']:
        return 'SUSPENDED'
    return s


def normalize_severity_governed(val):
    """
    Evidence-based severity mapping:
    - Text codes: CRITICAL/CRIT -> CRITICAL; HIGH/H -> HIGH; MEDIUM/M -> MEDIUM; LOW/L -> LOW
    - Priority codes: P1, P2, P3, P4 are mapped to standard tiers with explicit traceability in docs/methodology.md
    """
    if pd.isna(val) or str(val).strip() == '':
        return 'UNMAPPED'
    s = str(val).strip().upper()
    if s in ['CRITICAL', 'CRIT', 'P1']:
        return 'CRITICAL'
    elif s in ['HIGH', 'H', 'P2']:
        return 'HIGH'
    elif s in ['MEDIUM', 'M', 'P3']:
        return 'MEDIUM'
    elif s in ['LOW', 'L', 'P4']:
        return 'LOW'
    return 'UNMAPPED'


def normalize_resolution_status(val):
    if pd.isna(val) or str(val).strip() == '':
        return 'OPEN'
    s = str(val).strip().upper()
    if s in ['RESOLVED', 'CLOSED']:
        return 'RESOLVED'
    elif s in ['OPEN', 'IN_PROGRESS', 'WIP']:
        return 'IN_PROGRESS'
    elif s in ['REJECTED']:
        return 'REJECTED'
    elif s in ['PENDING_BANK', 'PENDING BANK']:
        return 'PENDING_BANK'
    return s


def normalize_business_type(val):
    if pd.isna(val) or str(val).strip() == '':
        return 'UNKNOWN'
    s = str(val).strip().upper().replace('-', '_').replace(' ', '_')
    if 'SOLE' in s or 'PROPRIETOR' in s:
        return 'SOLE_PROPRIETOR'
    elif 'PARTNER' in s:
        return 'PARTNERSHIP'
    elif 'PRIVATE' in s or 'PVT' in s or 'LIMITED' in s:
        return 'PRIVATE_LIMITED'
    elif 'INDIVIDUAL' in s:
        return 'INDIVIDUAL'
    return s


def normalize_channel(val):
    if pd.isna(val) or str(val).strip() == '':
        return 'OTHER'
    s = str(val).strip().upper()
    if 'CHAT' in s:
        return 'Chatbot'
    elif 'IVR' in s:
        return 'IVR'
    elif 'CALL' in s:
        return 'Call Center'
    elif 'BRANCH' in s:
        return 'Branch'
    elif 'EMAIL' in s:
        return 'Email'
    elif 'APP' in s:
        return 'App'
    return str(val).strip().title()
