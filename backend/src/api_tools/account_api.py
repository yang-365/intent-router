"""Account API tool — simulates account query operations."""

from __future__ import annotations

from typing import Any

from api_tools.base import BaseTool, ToolParameter

MOCK_ACCOUNTS: dict[str, dict[str, Any]] = {
    "default": {
        "card_number": "6222020100049999999",
        "balance": 85000.50,
        "available_balance": 83000.50,
        "account_type": "储蓄卡",
        "currency": "CNY",
    },
}


class AccountQueryAPITool(BaseTool):
    @property
    def tool_code(self) -> str:
        return "account_query_api"

    @property
    def tool_name(self) -> str:
        return "账户查询接口"

    @property
    def description(self) -> str:
        return "查询账户余额和基本信息"

    @property
    def parameters(self) -> list[ToolParameter]:
        return [
            ToolParameter(name="card_number", description="银行卡号"),
            ToolParameter(name="phone_last4", description="手机号后4位"),
            ToolParameter(name="cust_id", description="客户ID", required=False),
        ]

    async def call(self, params: dict[str, Any]) -> dict[str, Any]:
        card_number = params.get("card_number", "")
        phone_last4 = params.get("phone_last4", "")

        if not card_number:
            return {
                "success": False,
                "error_code": "MISSING_CARD",
                "message": "请提供银行卡号",
            }

        if not phone_last4:
            return {
                "success": False,
                "error_code": "MISSING_PHONE",
                "message": "请提供手机号后4位进行验证",
            }

        account = MOCK_ACCOUNTS.get("default", {})
        card_last4 = str(card_number)[-4:]

        return {
            "success": True,
            "message": (
                f"卡号尾号{card_last4}的账户余额为 "
                f"{account['balance']:,.2f} 元，"
                f"可用余额 {account['available_balance']:,.2f} 元。"
            ),
            "data": {
                "card_last4": card_last4,
                "balance": account["balance"],
                "available_balance": account["available_balance"],
                "account_type": account["account_type"],
                "currency": account["currency"],
            },
        }
