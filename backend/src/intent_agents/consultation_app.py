"""Consultation agent FastAPI application."""

from __future__ import annotations

from fastapi import FastAPI

from intent_agents.common import (
    AgentCancelRequest,
    AgentCancelResponse,
    AgentExecutionResponse,
)
from intent_agents.consultation_service import (
    ConsultationAgentRequest,
    ConsultationAgentService,
)


def create_app() -> FastAPI:
    application = FastAPI(title="Consultation Agent", version="0.1.0")
    service = ConsultationAgentService()

    @application.get("/health")
    async def health() -> dict[str, object]:
        return {"status": "ok", "service": "consultation-agent"}

    @application.post("/api/agent/run", response_model=AgentExecutionResponse)
    async def run_agent(request: ConsultationAgentRequest) -> AgentExecutionResponse:
        return await service.handle(request)

    @application.post("/api/agent/cancel", response_model=AgentCancelResponse)
    async def cancel_agent(request: AgentCancelRequest) -> AgentCancelResponse:
        return AgentCancelResponse(status="cancelled")

    return application


app = create_app()
