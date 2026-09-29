from processor.validation import validate_transaction_structure
CATEGORIES = {
   "categories": [
       {"name": "Food", "subcategories": ["Groceries", "Restaurants", "Other"]},
       {"name": "Bills", "subcategories": ["Electricity", "Internet", "Other"]},
       {"name": "Utilities", "subcategories": ["Electricity", "Water", "Other"]}
   ],
   "payment_methods": ["UPI", "Cash", "Credit Card"]
}
valid_tx = {
   "transaction_id": "11111111-1111-4111-8111-111111111111",
   "family_id": "-100123456789",
   "telegram_user_id": "12345",
   "timestamp": "2026-09-29T18:30:00+05:30",
   "date": "2026-09-29",
   "amount": 500,
   "type": "expense",
   "scope": "PERSONAL",
   "paid_by": "12345",
   "beneficiaries": ["12345"],
   "category": "Food",
   "subcategory": "Groceries",
   "payment_method": "UPI",
   "merchant": "Market",
   "note": "Weekly purchase",
   "status": "ACTIVE"
}
def test_valid_transaction_passes():
   errors = validate_transaction_structure(valid_tx, CATEGORIES)
   assert errors == []
def test_invalid_amount_rejected():
   tx = dict(valid_tx)
   tx["amount"] = 0
   errors = validate_transaction_structure(tx, CATEGORIES)
   assert any("amount must be greater than 0" in e for e in errors)
def test_invalid_category_rejected():
   tx = dict(valid_tx)
   tx["category"] = "UnknownCategory"
   errors = validate_transaction_structure(tx, CATEGORIES)
   assert any("not configured" in e for e in errors)
def test_invalid_subcategory_rejected():
   tx = dict(valid_tx)
   tx["subcategory"] = "Taxi"
   errors = validate_transaction_structure(tx, CATEGORIES)
   assert any("subcategory" in e for e in errors)
def test_invalid_scope_rejected():
   tx = dict(valid_tx)
   tx["scope"] = "INVALID"
   errors = validate_transaction_structure(tx, CATEGORIES)
   assert any("scope must be one of" in e for e in errors)
