from pydantic import BaseModel, Field
from typing import List, Optional

class Evidence(BaseModel):
    source_text: Optional[str] = Field(default=None)
    page_number: Optional[int] = Field(default=None)

class ExtractedValue(BaseModel):
    value: Optional[str] = Field(default=None)
    confidence: Optional[float] = Field(default=None)
    page_number: Optional[int] = Field(default=None)
    evidence: Optional[Evidence] = Field(default=None)

class InvoiceLineItem(BaseModel):
    description: Optional[str] = Field(default=None)
    quantity: Optional[float] = Field(default=None)
    unit_price: Optional[float] = Field(default=None)
    amount: Optional[float] = Field(default=None)

class InvoiceExtraction(BaseModel):
    invoice_number: ExtractedValue = Field(default_factory=ExtractedValue)
    invoice_date: ExtractedValue = Field(default_factory=ExtractedValue)
    vendor_name: ExtractedValue = Field(default_factory=ExtractedValue)
    customer_name: ExtractedValue = Field(default_factory=ExtractedValue)
    currency: ExtractedValue = Field(default_factory=ExtractedValue)
    subtotal: ExtractedValue = Field(default_factory=ExtractedValue)
    tax_amount: ExtractedValue = Field(default_factory=ExtractedValue)
    discount: ExtractedValue = Field(default_factory=ExtractedValue)
    total_amount: ExtractedValue = Field(default_factory=ExtractedValue)
    line_items: List[InvoiceLineItem] = Field(default_factory=list)

class FinancialLineItem(BaseModel):
    description: Optional[str] = Field(default=None)
    value: Optional[float] = Field(default=None)

class BalanceSheetExtraction(BaseModel):
    total_assets: ExtractedValue = Field(default_factory=ExtractedValue)
    total_liabilities: ExtractedValue = Field(default_factory=ExtractedValue)
    total_equity: ExtractedValue = Field(default_factory=ExtractedValue)
    line_items: List[FinancialLineItem] = Field(default_factory=list)

class ProfitAndLossExtraction(BaseModel):
    revenue: ExtractedValue = Field(default_factory=ExtractedValue)
    cost_of_sales: ExtractedValue = Field(default_factory=ExtractedValue)
    gross_profit: ExtractedValue = Field(default_factory=ExtractedValue)
    operating_expenses: ExtractedValue = Field(default_factory=ExtractedValue)
    operating_profit: ExtractedValue = Field(default_factory=ExtractedValue)
    tax: ExtractedValue = Field(default_factory=ExtractedValue)
    net_profit: ExtractedValue = Field(default_factory=ExtractedValue)
    line_items: List[FinancialLineItem] = Field(default_factory=list)

class CashFlowExtraction(BaseModel):
    operating_cash_flow: ExtractedValue = Field(default_factory=ExtractedValue)
    investing_cash_flow: ExtractedValue = Field(default_factory=ExtractedValue)
    financing_cash_flow: ExtractedValue = Field(default_factory=ExtractedValue)
    opening_cash: ExtractedValue = Field(default_factory=ExtractedValue)
    net_change_in_cash: ExtractedValue = Field(default_factory=ExtractedValue)
    closing_cash: ExtractedValue = Field(default_factory=ExtractedValue)
    line_items: List[FinancialLineItem] = Field(default_factory=list)
