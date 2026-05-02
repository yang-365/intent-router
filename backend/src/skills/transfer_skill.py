"""Transfer money skill — collects recipient info and amount, then executes transfer."""

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

CARD_NUMBER_RE = re.compile(r"\b(\d{12,19})\b")
PHONE_LAST4_RE = re.compile(r"(?:后[4四]位|尾号)\D*(\d{4})")
AMOUNT_RE = re.compile(r"(\d+(?:\.\d+)?)\s*元")
AMOUNT_PLAIN_RE = re.compile(r"(?:转|转账|金额)\D*(\d+(?:\.\d+)?)")
NAME_CUE_RE = re.compile(
    r"(?:给|向|转给|转账给)"
    r"([\u4e00-\u9fffA-Za-z]{2,16}?)"
    r"(?:转账|转|汇款|打款|\d|$)"
)


class TransferSkill(BaseSkill):
    @property
    def skill_code(self) -> str:
        return "transfer_money"

    @property
    def skill_name(self) -> str:
        return "转账"

    @property
    def description(self) -> str:
        return "向指定收款人转账，需要收款人姓名、卡号、手机号后4位和金额。"

    @property
    def slot_definitions(self) -> list[SlotDefinition]:
        return [
            SlotDefinition(
                name="recipient_name",
                description="收款人姓名",
                examples=["张三", "李四"],
            ),
            SlotDefinition(
                name="recipient_card_number",
                description="收款卡号",
                slot_type="card_number",
                examples=["6222020100049999999"],
            ),
            SlotDefinition(
                name="recipient_phone_last4",
                description="收款人手机号后4位",
                slot_type="phone_last4",
                examples=["1234"],
            ),
            SlotDefinition(
                name="amount",
                description="转账金额",
                slot_type="number",
                examples=["5000", "200.50"],
            ),
        ]

    def extract_slots(
        self,
        user_input: str,
        current_slots: dict[str, Any],
    ) -> dict[str, SlotValue]:
        slots = super().extract_slots(user_input, current_slots)

        if not slots["recipient_name"].is_filled:
            match = NAME_CUE_RE.search(user_input)
            if match:
                slots["recipient_name"] = SlotValue(
                    name="recipient_name",
                    value=match.group(1),
                    status=SlotStatus.FILLED,
                )

        if not slots["recipient_card_number"].is_filled:
            match = CARD_NUMBER_RE.search(user_input)
            if match:
                slots["recipient_card_number"] = SlotValue(
                    name="recipient_card_number",
                    value=match.group(1),
                    status=SlotStatus.FILLED,
                )

        if not slots["recipient_phone_last4"].is_filled:
            match = PHONE_LAST4_RE.search(user_input)
            if match:
                slots["recipient_phone_last4"] = SlotValue(
                    name="recipient_phone_last4",
                    value=match.group(1),
                    status=SlotStatus.FILLED,
                )

        if not slots["amount"].is_filled:
            match = AMOUNT_RE.search(user_input) or AMOUNT_PLAIN_RE.search(user_input)
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
        tool = registry.get("transfer_api")
        if tool is None:
            return SkillResult(
                success=False,
                message="转账服务暂不可用，请稍后再试。",
            )

        result = await tool.call({
            "from_account": (context or {}).get("cust_id", ""),
            "to_name": slots.get("recipient_name", ""),
            "to_card_number": slots.get("recipient_card_number", ""),
            "to_phone_last4": slots.get("recipient_phone_last4", ""),
            "amount": slots.get("amount", ""),
        })

        return SkillResult(
            success=result.get("success", False),
            message=result.get("message", "转账处理完成"),
            data=result,
            slots=slots,
        )
