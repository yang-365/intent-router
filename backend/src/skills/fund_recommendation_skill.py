"""Fund recommendation skill — recommends funds based on risk preference and amount."""

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

RISK_LEVEL_MAP: dict[str, str] = {
    "保守": "conservative",
    "稳健": "moderate",
    "平衡": "balanced",
    "积极": "aggressive",
    "激进": "aggressive",
    "低风险": "conservative",
    "中风险": "moderate",
    "中低风险": "moderate",
    "中高风险": "balanced",
    "高风险": "aggressive",
}

FUND_TYPE_MAP: dict[str, str] = {
    "货币基金": "money_market",
    "货币": "money_market",
    "余额宝": "money_market",
    "债券基金": "bond",
    "债券": "bond",
    "债基": "bond",
    "股票基金": "equity",
    "股票": "equity",
    "股基": "equity",
    "混合基金": "hybrid",
    "混合": "hybrid",
    "指数基金": "index",
    "指数": "index",
    "ETF": "etf",
    "etf": "etf",
}

AMOUNT_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(?:元|万|万元)")


class FundRecommendationSkill(BaseSkill):
    @property
    def skill_code(self) -> str:
        return "fund_recommendation"

    @property
    def skill_name(self) -> str:
        return "基金推荐"

    @property
    def description(self) -> str:
        return "根据用户风险偏好和投资金额推荐合适的基金产品。"

    @property
    def slot_definitions(self) -> list[SlotDefinition]:
        return [
            SlotDefinition(
                name="risk_level",
                description="风险偏好（保守/稳健/平衡/积极）",
                required=False,
                examples=["稳健", "保守"],
            ),
            SlotDefinition(
                name="fund_type",
                description="基金类型（货币/债券/股票/混合/指数）",
                required=False,
                examples=["货币基金", "债券基金"],
            ),
            SlotDefinition(
                name="investment_amount",
                description="投资金额",
                slot_type="number",
                required=False,
                examples=["10000", "5万"],
            ),
        ]

    def extract_slots(
        self,
        user_input: str,
        current_slots: dict[str, Any],
    ) -> dict[str, SlotValue]:
        slots = super().extract_slots(user_input, current_slots)

        if not slots["risk_level"].is_filled:
            for keyword, level in RISK_LEVEL_MAP.items():
                if keyword in user_input:
                    slots["risk_level"] = SlotValue(
                        name="risk_level",
                        value=level,
                        status=SlotStatus.FILLED,
                    )
                    break

        if not slots["fund_type"].is_filled:
            for keyword, ftype in FUND_TYPE_MAP.items():
                if keyword in user_input:
                    slots["fund_type"] = SlotValue(
                        name="fund_type",
                        value=ftype,
                        status=SlotStatus.FILLED,
                    )
                    break

        if not slots["investment_amount"].is_filled:
            match = AMOUNT_RE.search(user_input)
            if match:
                raw = match.group(1)
                suffix = match.group(0)
                value = float(raw) * 10000 if "万" in suffix else float(raw)
                slots["investment_amount"] = SlotValue(
                    name="investment_amount",
                    value=str(value),
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
        tool = registry.get("fund_query_api")
        if tool is None:
            return SkillResult(
                success=False,
                message="基金推荐服务暂不可用，请稍后再试。",
            )

        result = await tool.call({
            "risk_level": slots.get("risk_level", "moderate"),
            "fund_type": slots.get("fund_type"),
            "investment_amount": slots.get("investment_amount"),
            "cust_id": (context or {}).get("cust_id", ""),
        })

        return SkillResult(
            success=result.get("success", False),
            message=result.get("message", ""),
            data=result,
            slots=slots,
        )
