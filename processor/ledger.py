from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

def transaction_file_path(raw_root: str | Path, transaction: Dict[str, Any]) -> Path:
    timestamp = datetime.fromisoformat(transaction["timestamp"])
    year = timestamp.strftime("%Y")
    month = timestamp.strftime("%m")
    day = timestamp.strftime("%d")
    return Path(raw_root) / year / month / day / f"{transaction['transaction_id']}.json"

def write_transaction(raw_root: str | Path, payload: Dict[str, Any]) -> Path:
    file_path = transaction_file_path(raw_root, payload)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return file_path