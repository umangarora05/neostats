def is_present(val):
    if val is None:
        return False
    if isinstance(val, dict):
        return val.get("value") is not None
    return True

def safe_float(val):
    if not is_present(val):
        return 0.0
    if isinstance(val, dict):
        try:
            return float(str(val.get("value", 0.0)).replace(",", ""))
        except ValueError:
            return 0.0
    try:
        return float(str(val).replace(",", ""))
    except ValueError:
        return 0.0

def create_check(name, formula, operands, calculated, reported, is_applicable=True, tolerance=0.05):
    if not is_applicable:
        return {
            "name": name,
            "formula": formula,
            "operands": operands,
            "calculated_value": None,
            "reported_value": reported,
            "variance": None,
            "status": "NOT_APPLICABLE"
        }
    variance = abs(calculated - reported)
    return {
        "name": name,
        "formula": formula,
        "operands": operands,
        "calculated_value": calculated,
        "reported_value": reported,
        "variance": variance,
        "status": "PASS" if variance <= tolerance else "FAILED"
    }

def validate_invoice(data: dict) -> list:
    checks = []
    
    subtotal = safe_float(data.get("subtotal"))
    tax_amount = safe_float(data.get("tax_amount"))
    discount = safe_float(data.get("discount"))
    total_amount = safe_float(data.get("total_amount"))
    
    # 1. Subtotal + Tax - Discount ≈ Total
    is_applicable = is_present(data.get("subtotal")) and is_present(data.get("total_amount"))
    calculated = subtotal + tax_amount - discount
    checks.append(create_check(
        "invoice_total_check", 
        "subtotal + tax_amount - discount", 
        {"subtotal": subtotal, "tax_amount": tax_amount, "discount": discount}, 
        calculated, total_amount, is_applicable
    ))

    # 2. Line Items
    line_items = data.get("line_items", [])
    if line_items:
        sum_of_lines = 0.0
        for i, item in enumerate(line_items):
            qty = safe_float(item.get("quantity"))
            price = safe_float(item.get("unit_price"))
            amt = safe_float(item.get("amount"))
            
            # Qty * Price ≈ Line Total
            is_applicable_line = is_present(item.get("quantity")) and is_present(item.get("unit_price")) and is_present(item.get("amount"))
            calculated_line = qty * price
            checks.append(create_check(
                f"line_item_{i+1}_check",
                "quantity * unit_price",
                {"quantity": qty, "unit_price": price},
                calculated_line, amt, is_applicable_line
            ))
            sum_of_lines += amt
            
        # Sum of line totals ≈ subtotal
        checks.append(create_check(
            "sum_of_lines_check",
            "sum(line_item_amounts)",
            {"sum_of_lines": sum_of_lines},
            sum_of_lines, subtotal, is_present(data.get("subtotal"))
        ))

    # 3. Cash & Change (if present in additional_header_fields)
    add_fields = data.get("additional_header_fields", {})
    cash_paid = safe_float(add_fields.get("cash_paid"))
    change = safe_float(add_fields.get("change"))
    if is_present(add_fields.get("cash_paid")) and is_present(add_fields.get("change")):
        calculated_change = cash_paid - total_amount
        checks.append(create_check(
            "cash_change_check",
            "cash_paid - total_amount",
            {"cash_paid": cash_paid, "total_amount": total_amount},
            calculated_change, change, True
        ))

    return checks

def validate_balance_sheet(data: dict) -> list:
    checks = []
    total_assets = safe_float(data.get("total_assets"))
    total_liabilities = safe_float(data.get("total_liabilities"))
    total_equity = safe_float(data.get("total_equity"))
    
    # 1. Total Liabilities + Total Equity ≈ Total Assets
    is_applicable = is_present(data.get("total_assets")) and (is_present(data.get("total_liabilities")) or is_present(data.get("total_equity")))
    calculated = total_liabilities + total_equity
    checks.append(create_check(
        "balance_sheet_equation",
        "total_liabilities + total_equity",
        {"total_liabilities": total_liabilities, "total_equity": total_equity},
        calculated, total_assets, is_applicable
    ))

    # 2. Component Sums
    line_items = data.get("line_items", [])
    assets_sum = 0.0
    liabilities_equity_sum = 0.0
    has_assets = False
    has_liabilities = False
    
    for item in line_items:
        desc = str(item.get("description", "")).lower()
        val = safe_float(item.get("value"))
        if "asset" in desc and "total" not in desc:
            assets_sum += val
            has_assets = True
        elif ("liabilit" in desc or "equity" in desc or "capital" in desc) and "total" not in desc:
            liabilities_equity_sum += val
            has_liabilities = True

    if has_assets and is_present(data.get("total_assets")):
        checks.append(create_check(
            "assets_sum_check",
            "sum(asset_components)",
            {"assets_sum": assets_sum},
            assets_sum, total_assets, True
        ))
        
    if has_liabilities and (is_present(data.get("total_liabilities")) or is_present(data.get("total_equity"))):
        checks.append(create_check(
            "liabilities_equity_sum_check",
            "sum(liability_and_equity_components)",
            {"liabilities_equity_sum": liabilities_equity_sum},
            liabilities_equity_sum, calculated, True
        ))

    return checks

def validate_profit_and_loss(data: dict) -> list:
    checks = []
    
    revenue = safe_float(data.get("revenue"))
    cogs = safe_float(data.get("cost_of_sales"))
    opex = safe_float(data.get("operating_expenses"))
    tax = safe_float(data.get("tax"))
    net_profit = safe_float(data.get("net_profit"))
    
    # Revenue - COGS - Opex - Tax ≈ Net Profit (Simplified check if standard P&L)
    is_applicable = is_present(data.get("revenue")) and is_present(data.get("net_profit"))
    calculated_np = revenue - cogs - opex - tax
    checks.append(create_check(
        "net_profit_calculation",
        "revenue - cost_of_sales - operating_expenses - tax",
        {"revenue": revenue, "cost_of_sales": cogs, "operating_expenses": opex, "tax": tax},
        calculated_np, net_profit, is_applicable
    ))

    # Add Fields Checks (Interest Earned, etc)
    add_fields = data.get("additional_header_fields", {})
    interest_earned = safe_float(add_fields.get("interest_earned"))
    other_income = safe_float(add_fields.get("other_income"))
    total_income = safe_float(add_fields.get("total_income"))
    
    if is_present(add_fields.get("total_income")):
        calculated_income = interest_earned + other_income
        checks.append(create_check(
            "total_income_check",
            "interest_earned + other_income",
            {"interest_earned": interest_earned, "other_income": other_income},
            calculated_income, total_income, True
        ))

    interest_expended = safe_float(add_fields.get("interest_expended"))
    provisions = safe_float(add_fields.get("provisions_and_contingencies"))
    total_expenditure = safe_float(add_fields.get("total_expenditure"))
    
    if is_present(add_fields.get("total_expenditure")):
        calculated_exp = interest_expended + opex + provisions
        checks.append(create_check(
            "total_expenditure_check",
            "interest_expended + operating_expenses + provisions",
            {"interest_expended": interest_expended, "operating_expenses": opex, "provisions": provisions},
            calculated_exp, total_expenditure, True
        ))

    if is_present(add_fields.get("total_income")) and is_present(add_fields.get("total_expenditure")):
        net_profit_before_minority = safe_float(add_fields.get("net_profit_before_minority"))
        checks.append(create_check(
            "net_profit_before_minority_check",
            "total_income - total_expenditure",
            {"total_income": total_income, "total_expenditure": total_expenditure},
            total_income - total_expenditure, net_profit_before_minority, is_present(add_fields.get("net_profit_before_minority"))
        ))

    return checks

def validate_cash_flow_statement(data: dict) -> list:
    checks = []
    
    ocf = safe_float(data.get("operating_cash_flow"))
    icf = safe_float(data.get("investing_cash_flow"))
    fcf = safe_float(data.get("financing_cash_flow"))
    net_change = safe_float(data.get("net_change_in_cash"))
    
    add_fields = data.get("additional_header_fields", {})
    fx_adjustment = safe_float(add_fields.get("fx_translation_adjustment"))
    
    is_applicable_net = is_present(data.get("net_change_in_cash")) and (is_present(data.get("operating_cash_flow")) or is_present(data.get("investing_cash_flow")))
    calculated_net = ocf + icf + fcf + fx_adjustment
    checks.append(create_check(
        "net_change_calculation",
        "operating_cash_flow + investing_cash_flow + financing_cash_flow + fx_adjustment",
        {"operating_cash_flow": ocf, "investing_cash_flow": icf, "financing_cash_flow": fcf, "fx_adjustment": fx_adjustment},
        calculated_net, net_change, is_applicable_net
    ))
    
    opening_cash = safe_float(data.get("opening_cash"))
    closing_cash = safe_float(data.get("closing_cash"))
    adjustments = safe_float(add_fields.get("other_applicable_adjustments"))
    
    is_applicable_close = is_present(data.get("opening_cash")) and is_present(data.get("closing_cash"))
    calculated_close = opening_cash + net_change + adjustments
    checks.append(create_check(
        "closing_cash_calculation",
        "opening_cash + net_change + adjustments",
        {"opening_cash": opening_cash, "net_change": net_change, "adjustments": adjustments},
        calculated_close, closing_cash, is_applicable_close
    ))

    return checks

def validate_financials(document_type: str, extracted_data: dict) -> dict:
    checks = []
    overall_status = "PASS"
    issues = []
    
    if document_type == "invoice":
        checks = validate_invoice(extracted_data)
    elif document_type == "balance_sheet":
        checks = validate_balance_sheet(extracted_data)
    elif document_type == "profit_and_loss":
        checks = validate_profit_and_loss(extracted_data)
    elif document_type == "cash_flow_statement":
        checks = validate_cash_flow_statement(extracted_data)

    has_failed = False
    for check in checks:
        if check["status"] == "FAILED":
            has_failed = True
            issues.append(f"Validation failed for {check['name']}. Expected ~{check['calculated_value']}, got {check['reported_value']}. Variance: {check['variance']}")
            
    if has_failed:
        overall_status = "FAILED"
        
    return {
        "checks": checks,
        "overall_status": overall_status,
        "issues": issues
    }
