from processor.analytics import category_summary, monthly_summary, personal_vs_family
transactions = [
   {"date": "2026-09-01", "amount": 500, "scope": "PERSONAL", "category": "Food", "subcategory": "Groceries"},
   {"date": "2026-09-02", "amount": 3200, "scope": "FAMILY", "category": "Bills", "subcategory": "Electricity"},
   {"date": "2026-10-01", "amount": 700, "scope": "PERSONAL", "category": "Transport", "subcategory": "Fuel"},
   {"date": "2026-10-02", "amount": 2500, "scope": "FAMILY", "category": "Food", "subcategory": "Restaurants"},
]
def test_personal_family_split():
   totals = personal_vs_family(transactions)
   assert totals["personal"] == 1200
   assert totals["family"] == 5700
def test_category_aggregation():
   totals = category_summary(transactions)
   assert totals["Food"] == 3000
   assert totals["Bills"] == 3200
def test_monthly_aggregation():
   totals = monthly_summary(transactions)
   assert totals["2026-09"] == 3700
   assert totals["2026-10"] == 3200
