from __future__ import annotations
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List
RAW_DATA_ROOT = Path("data/raw")
OUTPUT_ROOT = Path("data/processed")
def load_transactions(raw_root: str | Path = RAW_DATA_ROOT) -> List[Dict[str, Any]]:
   rows: List[Dict[str, Any]] = []
   base = Path(raw_root)
   for file_path in sorted(base.rglob("*.json")):
       try:
           with open(file_path, "r", encoding="utf-8") as handle:
               payload = json.load(handle)
           if isinstance(payload, dict):
               rows.append(payload)
       except Exception:
           continue
   return rows
def monthly_summary(transactions: Iterable[Dict[str, Any]]) -> Dict[str, float]:
   result: Dict[str, float] = defaultdict(float)
   for tx in transactions:
       month = str(tx.get("date", "")).split("T")[0][:7]
       if month:
           result[month] += float(tx.get("amount", 0))
   return dict(sorted(result.items()))
def category_summary(transactions: Iterable[Dict[str, Any]]) -> Dict[str, float]:
   result: Dict[str, float] = defaultdict(float)
   for tx in transactions:
       result[str(tx.get("category", "Other"))] += float(tx.get("amount", 0))
   return dict(sorted(result.items()))
def subcategory_summary(transactions: Iterable[Dict[str, Any]]) -> Dict[str, float]:
   result: Dict[str, float] = defaultdict(float)
   for tx in transactions:
       key = f"{tx.get('category', 'Other')}::{tx.get('subcategory', 'Other')}"
       result[key] += float(tx.get("amount", 0))
   return dict(sorted(result.items()))
def personal_vs_family(transactions: Iterable[Dict[str, Any]]) -> Dict[str, float]:
   total = {"personal": 0.0, "family": 0.0}
   for tx in transactions:
       amount = float(tx.get("amount", 0))
       scope = str(tx.get("scope", "")).upper()
       if scope == "PERSONAL":
           total["personal"] += amount
       elif scope == "FAMILY":
           total["family"] += amount
   return total
def user_family_spending(transactions: Iterable[Dict[str, Any]]) -> Dict[str, float]:
   result: Dict[str, float] = defaultdict(float)
   for tx in transactions:
       if str(tx.get("scope", "")).upper() == "FAMILY":
           user = str(tx.get("paid_by", "unknown"))
           result[user] += float(tx.get("amount", 0))
   return dict(sorted(result.items()))
def daily_summary(transactions: Iterable[Dict[str, Any]]) -> Dict[str, float]:
   result: Dict[str, float] = defaultdict(float)
   for tx in transactions:
       date = str(tx.get("date", ""))
       result[date] += float(tx.get("amount", 0))
   return dict(sorted(result.items()))
def month_over_month(transactions: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
   monthly = monthly_summary(transactions)
   months = sorted(monthly)
   if len(months) < 2:
       return {"current_month": monthly.get(months[-1], 0.0) if months else 0.0, "previous_month": 0.0, "difference": 0.0}
   current = monthly[months[-1]]
   previous = monthly[months[-2]]
   return {"current_month": current, "previous_month": previous, "difference": current - previous}
def spending_trend(transactions: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
   values: Dict[str, float] = defaultdict(float)
   for tx in transactions:
       month = str(tx.get("date", "")).split("T")[0][:7]
       if month:
           values[month] += float(tx.get("amount", 0))
   return [{"month": month, "total": values[month]} for month in sorted(values)]
def generate_processed_data(raw_root: str | Path = RAW_DATA_ROOT, output_root: str | Path = OUTPUT_ROOT) -> Dict[str, Any]:
   txs = load_transactions(raw_root)
   output_root = Path(output_root)
   output_root.mkdir(parents=True, exist_ok=True)
   report = {
       "daily": daily_summary(txs),
       "monthly": monthly_summary(txs),
       "category_totals": category_summary(txs),
       "subcategory_totals": subcategory_summary(txs),
       "scope_totals": personal_vs_family(txs),
       "user_family_spending": user_family_spending(txs),
       "transaction_count": len(txs),
       "month_over_month": month_over_month(txs),
       "spending_trend": spending_trend(txs),
   }
   (output_root / "summary.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
   (output_root / "daily.json").write_text(json.dumps(report["daily"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
   (output_root / "monthly.json").write_text(json.dumps(report["monthly"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
   (output_root / "categories.json").write_text(json.dumps(report["category_totals"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
   (output_root / "subcategories.json").write_text(json.dumps(report["subcategory_totals"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
   (output_root / "users.json").write_text(json.dumps(report["user_family_spending"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
   (output_root / "trends.json").write_text(json.dumps({"month_over_month": report["month_over_month"], "spending_trend": report["spending_trend"]}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
   return report
