"""Bill payment API tool — simulates utility bill payment operations."""

from __future__ import annotations

from typing import Any

from api_tools.base import BaseTool, ToolParameter

BILL_TYPE_NAMES: dict[str, str] = {
    "electricity": "电费",
    "water": "水费",
    "gas": "燃气费",
    "phone": "话费",
    "broadband": "宽带费",
    "property": "物业费",
}

MOCK_BILLS: dict[str, dict[str, Any]] = {
    "electricity": {"pending_amount": 156.80, "last_payment": "2025-04-01"},
    "water": {"pending_amount": 45.60, "last_payment": "2025-03-15"},
    "gas": {"pending_amount": 89.20, "last_payment": "2025-03-20"},
    "phone": {"pending_amount": 128.00, "last_payment": "2025-04-05"},
    "broadband": {"pending_amount": 99.00, "last_payment": "2025-04-01"},
    "property": {"pending_amount": 2400.00, "last_payment": "2025-03-01"},
}


class BillPaymentAPITool(BaseTool):
    @property
    def tool_code(self) -> str:
        return "bill_payment_api"

    @property
    def tool_name(self) -> str:
        return "缴费接口"

    @property
    def description(self) -> str:
        return "调用缴费系统完成水电煤气话费等缴费"

    @property
    def parameters(self) -> list[ToolParameter]:
        return [
            ToolParameter(name="bill_type", description="缴费类型"),
            ToolParameter(name="account_number", description="缴费户号"),
            ToolParameter(name="amount", description="缴费金额", required=False),
            ToolParameter(name="cust_id", description="客户ID", required=False),
        ]

    async def call(self, params: dict[str, Any]) -> dict[str, Any]:
        bill_type = params.get("bill_type", "")
        account_number = params.get("account_number", "")

        if not bill_type:
            return {
                "success": False,
                "error_code": "MISSING_BILL_TYPE",
                "message": "请指定缴费类型",
            }

        if not account_number:
            return {
                "success": False,
                "error_code": "MISSING_ACCOUNT",
                "message": "请提供缴费户号",
            }

        type_name = BILL_TYPE_NAMES.get(bill_type, bill_type)
        mock_bill = MOCK_BILLS.get(bill_type, {"pending_amount": 100.00})
        amount = params.get("amount")
        pay_amount = float(amount) if amount else mock_bill["pending_amount"]

        return {
            "success": True,
            "message": (
                f"{type_name}缴费成功！户号 {account_number}，"
                f"缴费金额 {pay_amount} 元。"
            ),
            "data": {
                "payment_id": "PAY20250502001",
                "bill_type": bill_type,
                "type_name": type_name,
                "account_number": account_number,
                "amount": pay_amount,
                "status": "completed",
            },
        }
