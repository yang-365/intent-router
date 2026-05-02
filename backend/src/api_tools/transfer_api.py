"""Transfer API tool — simulates bank transfer operations."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from api_tools.base import BaseTool, ToolParameter


class TransferAPITool(BaseTool):
    @property
    def tool_code(self) -> str:
        return "transfer_api"

    @property
    def tool_name(self) -> str:
        return "转账接口"

    @property
    def description(self) -> str:
        return "调用核心银行系统执行转账操作"

    @property
    def parameters(self) -> list[ToolParameter]:
        return [
            ToolParameter(name="from_account", description="付款账户"),
            ToolParameter(name="to_name", description="收款人姓名"),
            ToolParameter(name="to_card_number", description="收款卡号"),
            ToolParameter(name="to_phone_last4", description="收款人手机号后4位"),
            ToolParameter(name="amount", description="转账金额"),
        ]

    async def call(self, params: dict[str, Any]) -> dict[str, Any]:
        missing = self.validate_params(params)
        if missing:
            return {
                "success": False,
                "error_code": "MISSING_PARAMS",
                "message": f"缺少必要参数：{', '.join(missing)}",
            }

        try:
            amount = Decimal(str(params["amount"]))
        except (InvalidOperation, ValueError):
            return {
                "success": False,
                "error_code": "INVALID_AMOUNT",
                "message": "转账金额格式不正确",
            }

        if amount <= 0:
            return {
                "success": False,
                "error_code": "INVALID_AMOUNT",
                "message": "转账金额必须大于0",
            }

        if amount > 50000:
            return {
                "success": True,
                "message": (
                    f"转账申请已提交：向 {params['to_name']}（卡号尾号"
                    f"{str(params['to_card_number'])[-4:]}）转账 {amount} 元。"
                    f"由于金额超过5万元，需要额外验证，请注意短信通知。"
                ),
                "data": {
                    "transaction_id": "TXN20250502001",
                    "status": "pending_verification",
                    "amount": str(amount),
                    "to_name": params["to_name"],
                    "to_card_last4": str(params["to_card_number"])[-4:],
                },
            }

        return {
            "success": True,
            "message": (
                f"转账成功！已向 {params['to_name']}（卡号尾号"
                f"{str(params['to_card_number'])[-4:]}）转账 {amount} 元。"
            ),
            "data": {
                "transaction_id": "TXN20250502001",
                "status": "completed",
                "amount": str(amount),
                "to_name": params["to_name"],
                "to_card_last4": str(params["to_card_number"])[-4:],
            },
        }
