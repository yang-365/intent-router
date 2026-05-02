"""Tests for the skills framework."""

from __future__ import annotations

import pytest

from skills.base import BaseSkill, SkillResult, SlotDefinition, SlotStatus, SlotValue
from skills.bill_payment_skill import BillPaymentSkill
from skills.consultation_skill import ConsultationSkill
from skills.fund_recommendation_skill import FundRecommendationSkill
from skills.menu_skill import MenuRecognitionSkill
from skills.registry import SkillRegistry, get_skill_registry
from skills.transfer_skill import TransferSkill


class TestSkillRegistry:
    def test_register_and_get(self) -> None:
        registry = SkillRegistry()
        skill = TransferSkill()
        registry.register(skill)
        assert registry.get("transfer_money") is skill

    def test_get_missing_returns_none(self) -> None:
        registry = SkillRegistry()
        assert registry.get("nonexistent") is None

    def test_list_skills(self) -> None:
        registry = SkillRegistry()
        registry.register(TransferSkill())
        registry.register(BillPaymentSkill())
        skills = registry.list_skills()
        assert len(skills) == 2
        codes = {s["skill_code"] for s in skills}
        assert codes == {"transfer_money", "bill_payment"}

    def test_global_registry_has_all_builtins(self) -> None:
        registry = get_skill_registry()
        expected = {"transfer_money", "bill_payment", "fund_recommendation", "consultation", "menu_recognition"}
        assert expected.issubset(set(registry.skill_codes))


class TestTransferSkill:
    def test_slot_definitions(self) -> None:
        skill = TransferSkill()
        names = {s.name for s in skill.slot_definitions}
        assert names == {"recipient_name", "recipient_card_number", "recipient_phone_last4", "amount"}

    def test_extract_name(self) -> None:
        skill = TransferSkill()
        slots = skill.extract_slots("给张三转200元", {})
        assert slots["recipient_name"].value == "张三"
        assert slots["recipient_name"].is_filled

    def test_extract_amount(self) -> None:
        skill = TransferSkill()
        slots = skill.extract_slots("转5000元", {})
        assert slots["amount"].value == "5000"

    def test_extract_card_number(self) -> None:
        skill = TransferSkill()
        slots = skill.extract_slots("收款卡号 6222020100049999999", {})
        assert slots["recipient_card_number"].value == "6222020100049999999"

    def test_extract_phone_last4(self) -> None:
        skill = TransferSkill()
        slots = skill.extract_slots("手机号后4位1234", {})
        assert slots["recipient_phone_last4"].value == "1234"

    def test_preserve_existing_slots(self) -> None:
        skill = TransferSkill()
        slots = skill.extract_slots("转5000元", {"recipient_name": "张三"})
        assert slots["recipient_name"].value == "张三"
        assert slots["amount"].value == "5000"

    def test_missing_required_slots(self) -> None:
        skill = TransferSkill()
        slots = skill.extract_slots("给张三转账", {})
        missing = skill.missing_required_slots(slots)
        assert "recipient_card_number" in missing
        assert "recipient_phone_last4" in missing
        assert "amount" in missing

    @pytest.mark.asyncio
    async def test_execute_success(self) -> None:
        skill = TransferSkill()
        result = await skill.execute(
            {
                "recipient_name": "张三",
                "recipient_card_number": "6222020100049999999",
                "recipient_phone_last4": "1234",
                "amount": "5000",
            },
            context={"cust_id": "cust_001"},
        )
        assert result.success
        assert "转账成功" in result.message


class TestBillPaymentSkill:
    def test_extract_bill_type(self) -> None:
        skill = BillPaymentSkill()
        slots = skill.extract_slots("帮我缴电费", {})
        assert slots["bill_type"].value == "electricity"

    def test_extract_account_number(self) -> None:
        skill = BillPaymentSkill()
        slots = skill.extract_slots("户号1001234567", {})
        assert slots["account_number"].value == "1001234567"

    def test_missing_slots(self) -> None:
        skill = BillPaymentSkill()
        slots = skill.extract_slots("帮我缴电费", {})
        missing = skill.missing_required_slots(slots)
        assert "account_number" in missing

    @pytest.mark.asyncio
    async def test_execute_success(self) -> None:
        skill = BillPaymentSkill()
        result = await skill.execute(
            {"bill_type": "electricity", "account_number": "1001234567"},
            context={"cust_id": "cust_001"},
        )
        assert result.success
        assert "电费" in result.message


class TestFundRecommendationSkill:
    def test_extract_risk_level(self) -> None:
        skill = FundRecommendationSkill()
        slots = skill.extract_slots("推荐一些稳健型基金", {})
        assert slots["risk_level"].value == "moderate"

    def test_extract_fund_type(self) -> None:
        skill = FundRecommendationSkill()
        slots = skill.extract_slots("推荐债券基金", {})
        assert slots["fund_type"].value == "bond"

    def test_extract_amount(self) -> None:
        skill = FundRecommendationSkill()
        slots = skill.extract_slots("我想投5万元", {})
        assert slots["investment_amount"].value == "50000.0"

    def test_no_required_slots(self) -> None:
        skill = FundRecommendationSkill()
        slots = skill.extract_slots("推荐基金", {})
        missing = skill.missing_required_slots(slots)
        assert len(missing) == 0

    @pytest.mark.asyncio
    async def test_execute_success(self) -> None:
        skill = FundRecommendationSkill()
        result = await skill.execute(
            {"risk_level": "moderate"},
            context={"cust_id": "cust_001"},
        )
        assert result.success
        assert "推荐" in result.message


class TestConsultationSkill:
    def test_extract_topic(self) -> None:
        skill = ConsultationSkill()
        slots = skill.extract_slots("怎么开户", {})
        assert slots["question_topic"].value == "开户"

    def test_extract_rate_topic(self) -> None:
        skill = ConsultationSkill()
        slots = skill.extract_slots("利率是多少", {})
        assert slots["question_topic"].value == "利率"

    @pytest.mark.asyncio
    async def test_execute_with_known_topic(self) -> None:
        skill = ConsultationSkill()
        result = await skill.execute(
            {"question_topic": "开户"},
            context={"user_input": "怎么开户"},
        )
        assert result.success
        assert "身份证" in result.message

    @pytest.mark.asyncio
    async def test_execute_unknown_topic(self) -> None:
        skill = ConsultationSkill()
        result = await skill.execute({}, context={"user_input": "随便问一下"})
        assert result.success
        assert "常见问题" in result.message


class TestMenuRecognitionSkill:
    def test_extract_transfer_menu(self) -> None:
        skill = MenuRecognitionSkill()
        slots = skill.extract_slots("我要转账", {})
        assert slots["menu_target"].value == "transfer"

    def test_extract_payment_menu(self) -> None:
        skill = MenuRecognitionSkill()
        slots = skill.extract_slots("我想缴费", {})
        assert slots["menu_target"].value == "payment"

    def test_extract_finance_menu(self) -> None:
        skill = MenuRecognitionSkill()
        slots = skill.extract_slots("看看理财产品", {})
        assert slots["menu_target"].value == "finance"

    @pytest.mark.asyncio
    async def test_execute_with_target(self) -> None:
        skill = MenuRecognitionSkill()
        result = await skill.execute({"menu_target": "transfer"})
        assert result.success
        assert "转账汇款" in result.message
        assert result.data["action"] == "navigate"

    @pytest.mark.asyncio
    async def test_execute_show_main_menu(self) -> None:
        skill = MenuRecognitionSkill()
        result = await skill.execute({})
        assert result.success
        assert "主要功能菜单" in result.message
        assert result.data["action"] == "show_main_menu"


class TestSlotValue:
    def test_missing_slot(self) -> None:
        sv = SlotValue(name="test")
        assert not sv.is_filled
        assert sv.status == SlotStatus.MISSING

    def test_filled_slot(self) -> None:
        sv = SlotValue(name="test", value="hello", status=SlotStatus.FILLED)
        assert sv.is_filled
