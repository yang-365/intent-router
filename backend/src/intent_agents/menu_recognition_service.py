"""Menu recognition agent service — navigates users to the right menu/feature."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from intent_agents.common import (
    AgentConversationContext,
    AgentCustomer,
    AgentExecutionResponse,
    AgentIntentContext,
)
from skills.menu_skill import MenuRecognitionSkill


class MenuRecognitionAgentRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    session_id: str = Field(alias="sessionId")
    task_id: str = Field(alias="taskId")
    input: str
    customer: AgentCustomer = Field(default_factory=AgentCustomer)
    conversation: AgentConversationContext = Field(default_factory=AgentConversationContext)
    intent: AgentIntentContext = Field(default_factory=AgentIntentContext)


class MenuRecognitionAgentService:
    def __init__(self) -> None:
        self.skill = MenuRecognitionSkill()

    async def handle(self, request: MenuRecognitionAgentRequest) -> AgentExecutionResponse:
        extracted = self.skill.extract_slots(request.input, {})

        slot_memory: dict[str, Any] = {
            name: sv.value for name, sv in extracted.items() if sv.is_filled
        }

        result = await self.skill.execute(slot_memory, context={})

        return AgentExecutionResponse.completed(
            result.message,
            slot_memory=slot_memory,
            payload={
                "agent": "menu_recognition",
                "business_status": "completed",
                **result.data,
            },
        )
