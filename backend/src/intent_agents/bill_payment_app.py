"""Bill payment agent FastAPI application."""

from __future__ import annotations

from fastapi import FastAPI

from intent_agents.common import (
    AgentCancelRequest,
    AgentCancelResponse,
    AgentExecutionResponse,
)
from intent_agents.bill_payment_service import (
    BillPaymentAgentRequest,
    BillPaymentAgentService,
)


def create_app() -> FastAPI:
    application = FastAPI(title="Bill Payment Agent", version="0.1.0")
    service = BillPaymentAgentService()

    @application.get("/health")
    async def health() -> dict[str, object]:
        return {"status": "ok", "service": "bill-payment-agent"}

    @application.post("/api/agent/run", response_model=AgentExecutionResponse)
    async def run_agent(request: BillPaymentAgentRequest) -> AgentExecutionResponse:
        return await service.handle(request)

    @application.post("/api/agent/cancel", response_model=AgentCancelResponse)
    async def cancel_agent(request: AgentCancelRequest) -> AgentCancelResponse:
        return AgentCancelResponse(status="cancelled")

    return application


app = create_app()
