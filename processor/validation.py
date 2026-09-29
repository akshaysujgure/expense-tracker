from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

ALLOWED_SCOPES = {"PERSONAL", "FAMILY"}
ALLOWED_TYPES = {"expense"}
ALLOWED_STATUSES = {"ACTIVE", "REVERSED", "CORRECTED"}

def load_categories(path: str | Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def validate_date_string(value: str) -> bool:
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_iso_datetime(value: str) -> bool:
    try:
        datetime.fromisoformat(value)
        return True
    except ValueError:
        return False

def validate_transaction_structure(payload: Dict[str, Any], categories_data: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    required = [
        "transaction_id", "family_id", "telegram_user_id", "timestamp", "date",
        "amount", "type", "scope", "paid_by", "beneficiaries", "category",
        "subcategory", "payment_method", "merchant", "note", "status"
    ]

    for field in required:
        if field not in payload:
            errors.append(f"Missing required field: {field}")

    if errors:
        return errors

    if not str(payload["transaction_id"]).strip():
        errors.append("transaction_id cannot be blank")

    if not str(payload["family_id"]).strip():
        errors.append("family_id cannot be blank")

    if not str(payload["telegram_user_id"]).strip():
        errors.append("telegram_user_id cannot be blank")

    if not validate_iso_datetime(str(payload["timestamp"])):
        errors.append("timestamp must be ISO 8601")

    if not validate_date_string(str(payload["date"])):
        errors.append("date must be YYYY-MM-DD")

    try:
        amount = float(payload["amount"])
    except (TypeError, ValueError):
        errors.append("amount must be numeric")
    else:
        if amount <= 0:
            errors.append("amount must be greater than 0")
        if amount > 2000000:
            errors.append("amount exceeds maximum supported value")

    if payload["type"] not in ALLOWED_TYPES:
        errors.append(f"type must be one of {sorted(ALLOWED_TYPES)}")

    if payload["scope"] not in ALLOWED_SCOPES:
        errors.append(f"scope must be one of {sorted(ALLOWED_SCOPES)}")

    if payload["status"] not in ALLOWED_STATUSES:
        errors.append(f"status must be one of {sorted(ALLOWED_STATUSES)}")

    if payload["paid_by"] != payload["telegram_user_id"] and payload["scope"] == "PERSONAL":
        errors.append("personal expenses must be paid by the authenticated user")

    categories = categories_data.get("categories", [])
    category_names = {c["name"]: c for c in categories}
    if payload["category"] not in category_names:
        errors.append(f"category '{payload['category']}' is not configured")
    else:
        valid_subcats = category_names[payload["category"]].get("subcategories", [])
        if payload["subcategory"] not in valid_subcats:
            errors.append(f"subcategory '{payload['subcategory']}' is invalid for category '{payload['category']}'")

    payment_methods = set(categories_data.get("payment_methods", []))
    if payload["payment_method"] not in payment_methods:
        errors.append(f"payment_method '{payload['payment_method']}' is not allowed")

    if not isinstance(payload["beneficiaries"], list):
        errors.append("beneficiaries must be a list")

    return errors

def validate_raw_transaction_file(path: str | Path, categories_data: Dict[str, Any]) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    return validate_transaction_structure(payload, categories_data)