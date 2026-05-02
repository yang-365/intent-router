"""Fund query API tool — simulates fund recommendation and query operations."""

from __future__ import annotations

from typing import Any

from api_tools.base import BaseTool, ToolParameter

MOCK_FUNDS: list[dict[str, Any]] = [
    {
        "fund_code": "000001",
        "fund_name": "华夏成长混合",
        "fund_type": "hybrid",
        "risk_level": "moderate",
        "nav": 1.2350,
        "return_1y": "12.5%",
        "return_3y": "35.2%",
        "min_purchase": 100,
    },
    {
        "fund_code": "110011",
        "fund_name": "易方达中小盘混合",
        "fund_type": "hybrid",
        "risk_level": "aggressive",
        "nav": 3.8920,
        "return_1y": "18.3%",
        "return_3y": "52.1%",
        "min_purchase": 100,
    },
    {
        "fund_code": "003003",
        "fund_name": "华夏现金增利A",
        "fund_type": "money_market",
        "risk_level": "conservative",
        "nav": 1.0000,
        "return_1y": "2.1%",
        "return_3y": "6.8%",
        "min_purchase": 1,
    },
    {
        "fund_code": "110025",
        "fund_name": "易方达稳健收益债券A",
        "fund_type": "bond",
        "risk_level": "moderate",
        "nav": 1.5230,
        "return_1y": "5.8%",
        "return_3y": "18.2%",
        "min_purchase": 100,
    },
    {
        "fund_code": "510300",
        "fund_name": "华泰柏瑞沪深300ETF",
        "fund_type": "etf",
        "risk_level": "balanced",
        "nav": 4.1250,
        "return_1y": "8.6%",
        "return_3y": "22.4%",
        "min_purchase": 1000,
    },
    {
        "fund_code": "161725",
        "fund_name": "招商中证白酒指数",
        "fund_type": "index",
        "risk_level": "aggressive",
        "nav": 1.0890,
        "return_1y": "15.2%",
        "return_3y": "45.6%",
        "min_purchase": 100,
    },
    {
        "fund_code": "005827",
        "fund_name": "易方达蓝筹精选混合",
        "fund_type": "equity",
        "risk_level": "aggressive",
        "nav": 2.1560,
        "return_1y": "20.1%",
        "return_3y": "58.3%",
        "min_purchase": 100,
    },
]

RISK_LEVEL_NAMES: dict[str, str] = {
    "conservative": "保守型",
    "moderate": "稳健型",
    "balanced": "平衡型",
    "aggressive": "积极型",
}

RISK_COMPATIBILITY: dict[str, list[str]] = {
    "conservative": ["conservative"],
    "moderate": ["conservative", "moderate"],
    "balanced": ["conservative", "moderate", "balanced"],
    "aggressive": ["conservative", "moderate", "balanced", "aggressive"],
}


class FundQueryAPITool(BaseTool):
    @property
    def tool_code(self) -> str:
        return "fund_query_api"

    @property
    def tool_name(self) -> str:
        return "基金查询接口"

    @property
    def description(self) -> str:
        return "查询和推荐基金产品"

    @property
    def parameters(self) -> list[ToolParameter]:
        return [
            ToolParameter(
                name="risk_level",
                description="风险偏好",
                required=False,
            ),
            ToolParameter(
                name="fund_type",
                description="基金类型",
                required=False,
            ),
            ToolParameter(
                name="investment_amount",
                description="投资金额",
                required=False,
            ),
            ToolParameter(
                name="cust_id",
                description="客户ID",
                required=False,
            ),
        ]

    async def call(self, params: dict[str, Any]) -> dict[str, Any]:
        risk_level = params.get("risk_level", "moderate")
        fund_type = params.get("fund_type")
        investment_amount = params.get("investment_amount")

        compatible_risks = RISK_COMPATIBILITY.get(risk_level, ["conservative", "moderate"])
        candidates = [
            f for f in MOCK_FUNDS
            if f["risk_level"] in compatible_risks
        ]

        if fund_type:
            typed = [f for f in candidates if f["fund_type"] == fund_type]
            if typed:
                candidates = typed

        if investment_amount:
            try:
                amount_val = float(investment_amount)
                candidates = [f for f in candidates if f["min_purchase"] <= amount_val]
            except (ValueError, TypeError):
                pass

        recommended = candidates[:3] if candidates else MOCK_FUNDS[:3]

        risk_name = RISK_LEVEL_NAMES.get(risk_level, risk_level)
        fund_lines = []
        for fund in recommended:
            fund_lines.append(
                f"  • {fund['fund_name']}（{fund['fund_code']}）"
                f"- 近一年收益 {fund['return_1y']}，"
                f"净值 {fund['nav']}"
            )

        message = f"根据您的{risk_name}风险偏好，为您推荐以下基金：\n" + "\n".join(fund_lines)

        return {
            "success": True,
            "message": message,
            "data": {
                "risk_level": risk_level,
                "recommended_funds": recommended,
                "total_candidates": len(candidates),
            },
        }
