"""Fund recommendation agent service — recommends funds based on user preferences."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from intent_agents.common import (
    AgentConversationContext,
    AgentCustomer,
    AgentExecutionResponse,
    AgentIntentContext,
)
from skills.fund_recommendation_skill import FundRecommendationSkill


class FundRecommendationAgentRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    session_id: str = Field(alias="sessionId")
    task_id: str = Field(alias="taskId")
    input: str
    customer: AgentCustomer = Field(default_factory=AgentCustomer)
    conversation: AgentConversationContext = Field(default_factory=AgentConversationContext)
    intent: AgentIntentContext = Field(default_factory=AgentIntentContext)
    risk_level: str | None = Field(default=None, alias="riskLevel")
    fund_type: str | None = Field(default=None, alias="fundType")
    investment_amount: str | None = Field(default=None, alias="investmentAmount")


class FundRecommendationAgentService:
    def __init__(self) -> None:
        self.skill = FundRecommendationSkill()

    async def handle(self, request: FundRecommendationAgentRequest) -> AgentExecutionResponse:
        current_slots: dict[str, Any] = {}
        if request.risk_level:
            current_slots["risk_level"] = request.risk_level
        if request.fund_type:
            current_slots["fund_type"] = request.fund_type
        if request.investment_amount:
            current_slots["investment_amount"] = request.investment_amount

        extracted = self.skill.extract_slots(request.input, current_slots)

        slot_memory: dict[str, Any] = {
            name: sv.value for name, sv in extracted.items() if sv.is_filled
        }

        result = await self.skill.execute(
            slot_memory,
            context={"cust_id": request.customer.cust_id or ""},
        )

        if result.success:
            return AgentExecutionResponse.completed(
                result.message,
                slot_memory=slot_memory,
                payload={
                    "agent": "fund_recommendation",
                    "business_status": "completed",
                    **result.data,
                },
            )

        return AgentExecutionResponse.failed(
            result.message,
            payload={"agent": "fund_recommendation", **result.data},
        )
