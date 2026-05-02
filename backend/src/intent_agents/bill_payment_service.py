"""Bill payment agent service — handles utility bill payment flows."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from intent_agents.common import (
    AgentConversationContext,
    AgentCustomer,
    AgentExecutionResponse,
    AgentIntentContext,
)
from skills.bill_payment_skill import BillPaymentSkill


class BillPaymentAgentRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    session_id: str = Field(alias="sessionId")
    task_id: str = Field(alias="taskId")
    input: str
    customer: AgentCustomer = Field(default_factory=AgentCustomer)
    conversation: AgentConversationContext = Field(default_factory=AgentConversationContext)
    intent: AgentIntentContext = Field(default_factory=AgentIntentContext)
    bill_type: str | None = Field(default=None, alias="billType")
    account_number: str | None = Field(default=None, alias="accountNumber")
    amount: str | None = None


class BillPaymentAgentService:
    def __init__(self) -> None:
        self.skill = BillPaymentSkill()

    async def handle(self, request: BillPaymentAgentRequest) -> AgentExecutionResponse:
        current_slots: dict[str, Any] = {}
        if request.bill_type:
            current_slots["bill_type"] = request.bill_type
        if request.account_number:
            current_slots["account_number"] = request.account_number
        if request.amount:
            current_slots["amount"] = request.amount

        extracted = self.skill.extract_slots(request.input, current_slots)
        missing = self.skill.missing_required_slots(extracted)

        slot_memory: dict[str, Any] = {
            name: sv.value for name, sv in extracted.items() if sv.is_filled
        }

        if missing:
            ask = self.skill.build_ask_message(missing)
            return AgentExecutionResponse.waiting(
                ask,
                slot_memory=slot_memory,
                payload={
                    "agent": "bill_payment",
                    "missing_fields": missing,
                },
            )

        result = await self.skill.execute(
            slot_memory,
            context={"cust_id": request.customer.cust_id or ""},
        )

        if result.success:
            return AgentExecutionResponse.completed(
                result.message,
                slot_memory=slot_memory,
                payload={
                    "agent": "bill_payment",
                    "business_status": "completed",
                    **result.data,
                },
            )

        return AgentExecutionResponse.failed(
            result.message,
            payload={"agent": "bill_payment", **result.data},
        )
