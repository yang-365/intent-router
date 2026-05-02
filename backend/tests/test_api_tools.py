"""Tests for the API tools layer."""

from __future__ import annotations

import pytest

from api_tools.account_api import AccountQueryAPITool
from api_tools.base import BaseTool
from api_tools.bill_payment_api import BillPaymentAPITool
from api_tools.fund_api import FundQueryAPITool
from api_tools.registry import ToolRegistry, get_tool_registry
from api_tools.transfer_api import TransferAPITool


class TestToolRegistry:
    def test_register_and_get(self) -> None:
        registry = ToolRegistry()
        tool = TransferAPITool()
        registry.register(tool)
        assert registry.get("transfer_api") is tool

    def test_get_missing_returns_none(self) -> None:
        registry = ToolRegistry()
        assert registry.get("nonexistent") is None

    def test_list_tools(self) -> None:
        registry = ToolRegistry()
        registry.register(TransferAPITool())
        registry.register(BillPaymentAPITool())
        tools = registry.list_tools()
        assert len(tools) == 2
        codes = {t["tool_code"] for t in tools}
        assert codes == {"transfer_api", "bill_payment_api"}

    def test_global_registry_has_all_builtins(self) -> None:
        registry = get_tool_registry()
        expected = {"transfer_api", "bill_payment_api", "fund_query_api", "account_query_api"}
        assert expected.issubset(set(registry.tool_codes))


class TestTransferAPITool:
    @pytest.mark.asyncio
    async def test_successful_transfer(self) -> None:
        tool = TransferAPITool()
        result = await tool.call({
            "from_account": "cust_001",
            "to_name": "张三",
            "to_card_number": "6222020100049999999",
            "to_phone_last4": "1234",
            "amount": "5000",
        })
        assert result["success"]
        assert "转账成功" in result["message"]
        assert result["data"]["status"] == "completed"

    @pytest.mark.asyncio
    async def test_large_amount_needs_verification(self) -> None:
        tool = TransferAPITool()
        result = await tool.call({
            "from_account": "cust_001",
            "to_name": "张三",
            "to_card_number": "6222020100049999999",
            "to_phone_last4": "1234",
            "amount": "100000",
        })
        assert result["success"]
        assert "额外验证" in result["message"]
        assert result["data"]["status"] == "pending_verification"

    @pytest.mark.asyncio
    async def test_missing_params(self) -> None:
        tool = TransferAPITool()
        result = await tool.call({"from_account": "cust_001"})
        assert not result["success"]
        assert result["error_code"] == "MISSING_PARAMS"

    @pytest.mark.asyncio
    async def test_invalid_amount(self) -> None:
        tool = TransferAPITool()
        result = await tool.call({
            "from_account": "cust_001",
            "to_name": "张三",
            "to_card_number": "6222020100049999999",
            "to_phone_last4": "1234",
            "amount": "abc",
        })
        assert not result["success"]
        assert result["error_code"] == "INVALID_AMOUNT"

    @pytest.mark.asyncio
    async def test_negative_amount(self) -> None:
        tool = TransferAPITool()
        result = await tool.call({
            "from_account": "cust_001",
            "to_name": "张三",
            "to_card_number": "6222020100049999999",
            "to_phone_last4": "1234",
            "amount": "-100",
        })
        assert not result["success"]


class TestBillPaymentAPITool:
    @pytest.mark.asyncio
    async def test_successful_payment(self) -> None:
        tool = BillPaymentAPITool()
        result = await tool.call({
            "bill_type": "electricity",
            "account_number": "1001234567",
        })
        assert result["success"]
        assert "电费" in result["message"]

    @pytest.mark.asyncio
    async def test_custom_amount(self) -> None:
        tool = BillPaymentAPITool()
        result = await tool.call({
            "bill_type": "water",
            "account_number": "1001234567",
            "amount": "50",
        })
        assert result["success"]
        assert result["data"]["amount"] == 50.0

    @pytest.mark.asyncio
    async def test_missing_bill_type(self) -> None:
        tool = BillPaymentAPITool()
        result = await tool.call({"account_number": "123"})
        assert not result["success"]

    @pytest.mark.asyncio
    async def test_missing_account(self) -> None:
        tool = BillPaymentAPITool()
        result = await tool.call({"bill_type": "electricity"})
        assert not result["success"]


class TestFundQueryAPITool:
    @pytest.mark.asyncio
    async def test_default_recommendation(self) -> None:
        tool = FundQueryAPITool()
        result = await tool.call({})
        assert result["success"]
        assert "推荐" in result["message"]
        assert len(result["data"]["recommended_funds"]) > 0

    @pytest.mark.asyncio
    async def test_conservative_filter(self) -> None:
        tool = FundQueryAPITool()
        result = await tool.call({"risk_level": "conservative"})
        assert result["success"]
        for fund in result["data"]["recommended_funds"]:
            assert fund["risk_level"] == "conservative"

    @pytest.mark.asyncio
    async def test_fund_type_filter(self) -> None:
        tool = FundQueryAPITool()
        result = await tool.call({"fund_type": "bond"})
        assert result["success"]


class TestAccountQueryAPITool:
    @pytest.mark.asyncio
    async def test_successful_query(self) -> None:
        tool = AccountQueryAPITool()
        result = await tool.call({
            "card_number": "6222020100049999999",
            "phone_last4": "1234",
        })
        assert result["success"]
        assert "余额" in result["message"]
        assert result["data"]["balance"] > 0

    @pytest.mark.asyncio
    async def test_missing_card(self) -> None:
        tool = AccountQueryAPITool()
        result = await tool.call({"phone_last4": "1234"})
        assert not result["success"]

    @pytest.mark.asyncio
    async def test_missing_phone(self) -> None:
        tool = AccountQueryAPITool()
        result = await tool.call({"card_number": "6222020100049999999"})
        assert not result["success"]


class TestBaseTool:
    def test_to_schema(self) -> None:
        tool = TransferAPITool()
        schema = tool.to_schema()
        assert schema["tool_code"] == "transfer_api"
        assert len(schema["parameters"]) > 0

    def test_validate_params(self) -> None:
        tool = TransferAPITool()
        missing = tool.validate_params({"from_account": "x"})
        assert "to_name" in missing
        assert "amount" in missing
