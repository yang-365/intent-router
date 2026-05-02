"""Bill payment skill — handles utility bill payments (electricity, water, gas, phone)."""

from __future__ import annotations

import re
from typing import Any

from skills.base import (
    BaseSkill,
    SkillResult,
    SlotDefinition,
    SlotStatus,
    SlotValue,
)

BILL_TYPE_MAP: dict[str, str] = {
    "电费": "electricity",
    "电": "electricity",
    "水费": "water",
    "水": "water",
    "燃气费": "gas",
    "燃气": "gas",
    "煤气费": "gas",
    "煤气": "gas",
    "话费": "phone",
    "手机费": "phone",
    "宽带费": "broadband",
    "宽带": "broadband",
    "物业费": "property",
    "物业": "property",
}

ACCOUNT_NO_RE = re.compile(r"(?:户号|账号|编号)\D*(\d{6,20})")
AMOUNT_RE = re.compile(r"(\d+(?:\.\d+)?)\s*元")


class BillPaymentSkill(BaseSkill):
    @property
    def skill_code(self) -> str:
        return "bill_payment"

    @property
    def skill_name(self) -> str:
        return "生活缴费"

    @property
    def description(self) -> str:
        return "水电煤气、话费等生活缴费，需要缴费类型、户号和金额。"

    @property
    def slot_definitions(self) -> list[SlotDefinition]:
        return [
            SlotDefinition(
                name="bill_type",
                description="缴费类型（电费/水费/燃气费/话费等）",
                examples=["电费", "水费", "话费"],
            ),
            SlotDefinition(
                name="account_number",
                description="缴费户号",
                examples=["1001234567"],
            ),
            SlotDefinition(
                name="amount",
                description="缴费金额",
                slot_type="number",
                required=False,
            ),
        ]

    def extract_slots(
        self,
        user_input: str,
        current_slots: dict[str, Any],
    ) -> dict[str, SlotValue]:
        slots = super().extract_slots(user_input, current_slots)

        if not slots["bill_type"].is_filled:
            for keyword, code in BILL_TYPE_MAP.items():
                if keyword in user_input:
                    slots["bill_type"] = SlotValue(
                        name="bill_type",
                        value=code,
                        status=SlotStatus.FILLED,
                    )
                    break

        if not slots["account_number"].is_filled:
            match = ACCOUNT_NO_RE.search(user_input)
            if match:
                slots["account_number"] = SlotValue(
                    name="account_number",
                    value=match.group(1),
                    status=SlotStatus.FILLED,
                )

        if not slots["amount"].is_filled:
            match = AMOUNT_RE.search(user_input)
            if match:
                slots["amount"] = SlotValue(
                    name="amount",
                    value=match.group(1),
                    status=SlotStatus.FILLED,
                )

        return slots

    async def execute(
        self,
        slots: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> SkillResult:
        from api_tools.registry import get_tool_registry

        registry = get_tool_registry()
        tool = registry.get("bill_payment_api")
        if tool is None:
            return SkillResult(
                success=False,
                message="缴费服务暂不可用，请稍后再试。",
            )

        result = await tool.call({
            "bill_type": slots.get("bill_type", ""),
            "account_number": slots.get("account_number", ""),
            "amount": slots.get("amount"),
            "cust_id": (context or {}).get("cust_id", ""),
        })

        return SkillResult(
            success=result.get("success", False),
            message=result.get("message", "缴费处理完成"),
            data=result,
            slots=slots,
        )
