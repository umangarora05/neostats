import pytest
from app.services.financial_validation_service import validate_invoice, validate_balance_sheet, validate_profit_and_loss, validate_cash_flow_statement

def test_validate_invoice_success():
    data = {
        "subtotal": 100.0,
        "tax_amount": 10.0,
        "discount": 0.0,
        "total_amount": 110.0,
        "line_items": [
            {"quantity": 2, "unit_price": 50.0, "amount": 100.0}
        ]
    }
    result = validate_invoice(data)
    assert len(result) >= 3  # invoice total, line item 1, sum of lines
    assert all(r["status"] == "PASS" for r in result)

def test_validate_invoice_failure():
    data = {
        "subtotal": 100.0,
        "tax_amount": 10.0,
        "discount": 0.0,
        "total_amount": 120.0, # Incorrect total
    }
    result = validate_invoice(data)
    total_check = next(r for r in result if r["name"] == "invoice_total_check")
    assert total_check["status"] == "FAILED"

def test_validate_balance_sheet():
    data = {
        "total_assets": 50000.0,
        "total_liabilities": 30000.0,
        "total_equity": 20000.0,
        "line_items": [
            {"description": "Cash (Asset)", "value": 50000.0},
            {"description": "Loans (Liability)", "value": 30000.0},
            {"description": "Owner Equity", "value": 20000.0}
        ]
    }
    result = validate_balance_sheet(data)
    assert all(r["status"] == "PASS" for r in result)
    
def test_validate_profit_and_loss():
    data = {
        "revenue": 100000.0,
        "cost_of_sales": 40000.0,
        "operating_expenses": 20000.0,
        "tax": 10000.0,
        "net_profit": 30000.0
    }
    result = validate_profit_and_loss(data)
    np_check = next(r for r in result if r["name"] == "net_profit_calculation")
    assert np_check["status"] == "PASS"

def test_validate_cash_flow():
    data = {
        "operating_cash_flow": 10000.0,
        "investing_cash_flow": -5000.0,
        "financing_cash_flow": -2000.0,
        "net_change_in_cash": 3000.0,
        "opening_cash": 5000.0,
        "closing_cash": 8000.0
    }
    result = validate_cash_flow_statement(data)
    assert all(r["status"] == "PASS" for r in result)
