from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import uuid
from typing import Any, Dict, List

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def generate_uuid() -> str:
    return str(uuid.uuid4())

@dataclass
class Transaction:
    transaction_id: str
    family_id: str
    telegram_user_id: str
    timestamp: str
    date: str
    amount: float
    type: str
    scope: str
    paid_by: str
    beneficiaries: List[str]
    category: str
    subcategory: str
    payment_method: str
    merchant: str
    note: str
    status: str = "ACTIVE"

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "Transaction":
        return cls(
            transaction_id=payload["transaction_id"],
            family_id=str(payload["family_id"]),
            telegram_user_id=str(payload["telegram_user_id"]),
            timestamp=payload["timestamp"],
            date=payload["date"],
            amount=float(payload["amount"]),
            type=payload["type"],
            scope=payload["scope"],
            paid_by=str(payload["paid_by"]),
            beneficiaries=list(payload.get("beneficiaries", [])),
            category=payload["category"],
            subcategory=payload["subcategory"],
            payment_method=payload["payment_method"],
            merchant=payload.get("merchant", ""),
            note=payload.get("note", ""),
            status=payload.get("status", "ACTIVE"),
        )

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["amount"] = float(self.amount)
        return data