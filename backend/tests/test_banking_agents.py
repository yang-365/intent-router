"""Tests for the new banking intent agent services."""

from __future__ import annotations

import pytest

from intent_agents.bill_payment_service import (
    BillPaymentAgentRequest,
    BillPaymentAgentService,
)
from intent_agents.consultation_service import (
    ConsultationAgentRequest,
    ConsultationAgentService,
)
from intent_agents.fund_recommendation_service import (
    FundRecommendationAgentRequest,
    FundRecommendationAgentService,
)
from intent_agents.menu_recognition_service import (
    MenuRecognitionAgentRequest,
    MenuRecognitionAgentService,
)


class TestBillPaymentAgent:
    @pytest.mark.asyncio
    async def test_missing_info_asks_for_account(self) -> None:
        service = BillPaymentAgentService()
        request = BillPaymentAgentRequest(
            sessionId="s1",
            taskId="t1",
            input="帮我缴电费",
        )
        response = await service.handle(request)
        assert response.status == "waiting_user_input"
        assert "account_number" in response.payload.get("missing_fields", [])

    @pytest.mark.asyncio
    async def test_complete_payment(self) -> None:
        service = BillPaymentAgentService()
        request = BillPaymentAgentRequest(
            sessionId="s1",
            taskId="t1",
            input="帮我缴电费，户号1001234567",
        )
        response = await service.handle(request)
        assert response.status == "completed"
        assert "电费" in response.content

    @pytest.mark.asyncio
    async def test_with_preset_slots(self) -> None:
        service = BillPaymentAgentService()
        request = BillPaymentAgentRequest(
            sessionId="s1",
            taskId="t1",
            input="帮我缴费",
            billType="electricity",
            accountNumber="1001234567",
        )
        response = await service.handle(request)
        assert response.status == "completed"


class TestFundRecommendationAgent:
    @pytest.mark.asyncio
    async def test_basic_recommendation(self) -> None:
        service = FundRecommendationAgentService()
        request = FundRecommendationAgentRequest(
            sessionId="s1",
            taskId="t1",
            input="推荐一些稳健型基金",
        )
        response = await service.handle(request)
        assert response.status == "completed"
        assert "推荐" in response.content

    @pytest.mark.asyncio
    async def test_with_fund_type(self) -> None:
        service = FundRecommendationAgentService()
        request = FundRecommendationAgentRequest(
            sessionId="s1",
            taskId="t1",
            input="推荐债券基金",
        )
        response = await service.handle(request)
        assert response.status == "completed"


class TestConsultationAgent:
    @pytest.mark.asyncio
    async def test_known_topic(self) -> None:
        service = ConsultationAgentService()
        request = ConsultationAgentRequest(
            sessionId="s1",
            taskId="t1",
            input="怎么开户",
        )
        response = await service.handle(request)
        assert response.status == "completed"
        assert "身份证" in response.content

    @pytest.mark.asyncio
    async def test_general_inquiry(self) -> None:
        service = ConsultationAgentService()
        request = ConsultationAgentRequest(
            sessionId="s1",
            taskId="t1",
            input="你好",
        )
        response = await service.handle(request)
        assert response.status == "completed"


class TestMenuRecognitionAgent:
    @pytest.mark.asyncio
    async def test_recognize_transfer_menu(self) -> None:
        service = MenuRecognitionAgentService()
        request = MenuRecognitionAgentRequest(
            sessionId="s1",
            taskId="t1",
            input="我要转账",
        )
        response = await service.handle(request)
        assert response.status == "completed"
        assert "转账汇款" in response.content

    @pytest.mark.asyncio
    async def test_show_main_menu(self) -> None:
        service = MenuRecognitionAgentService()
        request = MenuRecognitionAgentRequest(
            sessionId="s1",
            taskId="t1",
            input="功能菜单",
        )
        response = await service.handle(request)
        assert response.status == "completed"
        assert response.payload.get("action") == "show_main_menu"
