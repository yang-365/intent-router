"""Consultation skill — answers common banking questions and FAQs."""

from __future__ import annotations

from typing import Any

from skills.base import (
    BaseSkill,
    SkillResult,
    SlotDefinition,
    SlotStatus,
    SlotValue,
)

FAQ_DATABASE: dict[str, dict[str, str]] = {
    "开户": {
        "answer": (
            "开户需要携带本人有效身份证件前往任意网点办理，"
            "也可通过掌银APP在线开立II类/III类账户。"
        ),
        "category": "account",
    },
    "挂失": {
        "answer": (
            "银行卡挂失可通过以下方式：\n"
            "1. 拨打客服热线进行口头挂失\n"
            "2. 通过掌银APP自助挂失\n"
            "3. 携带身份证前往网点办理书面挂失"
        ),
        "category": "card",
    },
    "修改密码": {
        "answer": "您可以通过掌银APP【设置】-【安全中心】-【修改密码】进行密码修改，也可前往网点柜台办理。",
        "category": "security",
    },
    "利率": {
        "answer": (
            "当前存款利率：\n"
            "- 活期：0.20%\n"
            "- 一年定期：1.45%\n"
            "- 三年定期：1.95%\n"
            "- 五年定期：2.00%\n"
            "具体利率以实际办理时为准。"
        ),
        "category": "rate",
    },
    "手续费": {
        "answer": (
            "转账手续费标准：\n"
            "- 掌银/网银转账：免费\n"
            "- 柜台同行转账：免费\n"
            "- 柜台跨行转账：按金额0.5%-1%收取，最低2元"
        ),
        "category": "fee",
    },
    "信用卡": {
        "answer": "信用卡相关业务可通过掌银APP【信用卡】专区办理，包括申请、还款、账单查询、额度调整等。",
        "category": "credit_card",
    },
    "贷款": {
        "answer": "我行提供多种贷款产品，包括个人消费贷、房贷、车贷等。您可以通过掌银APP【贷款】专区查看详情并在线申请。",
        "category": "loan",
    },
    "网点": {
        "answer": "您可以通过掌银APP【附近网点】功能查找最近的营业网点，查看营业时间和地址。",
        "category": "branch",
    },
}

KEYWORD_CATEGORY_MAP: dict[str, list[str]] = {
    "开户": ["开户", "开卡", "办卡", "新账户"],
    "挂失": ["挂失", "丢失", "丢了", "找不到卡"],
    "修改密码": ["密码", "改密码", "修改密码", "重置密码"],
    "利率": ["利率", "利息", "存款利率", "年利率"],
    "手续费": ["手续费", "收费", "费用"],
    "信用卡": ["信用卡", "信用", "额度"],
    "贷款": ["贷款", "借钱", "借款", "房贷", "车贷"],
    "网点": ["网点", "营业厅", "柜台", "银行地址"],
}


class ConsultationSkill(BaseSkill):
    @property
    def skill_code(self) -> str:
        return "consultation"

    @property
    def skill_name(self) -> str:
        return "业务咨询"

    @property
    def description(self) -> str:
        return "回答用户关于银行业务的常见问题，包括开户、挂失、利率、手续费等。"

    @property
    def slot_definitions(self) -> list[SlotDefinition]:
        return [
            SlotDefinition(
                name="question_topic",
                description="咨询主题",
                required=False,
                examples=["开户", "利率", "手续费"],
            ),
        ]

    def extract_slots(
        self,
        user_input: str,
        current_slots: dict[str, Any],
    ) -> dict[str, SlotValue]:
        slots = super().extract_slots(user_input, current_slots)

        for topic, keywords in KEYWORD_CATEGORY_MAP.items():
            for keyword in keywords:
                if keyword in user_input:
                    slots["question_topic"] = SlotValue(
                        name="question_topic",
                        value=topic,
                        status=SlotStatus.FILLED,
                    )
                    return slots

        return slots

    async def execute(
        self,
        slots: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> SkillResult:
        topic = slots.get("question_topic")

        if topic and topic in FAQ_DATABASE:
            faq = FAQ_DATABASE[topic]
            return SkillResult(
                success=True,
                message=faq["answer"],
                data={"topic": topic, "category": faq["category"]},
                slots=slots,
            )

        user_input = (context or {}).get("user_input", "")
        for faq_topic, keywords in KEYWORD_CATEGORY_MAP.items():
            for keyword in keywords:
                if keyword in user_input:
                    faq = FAQ_DATABASE[faq_topic]
                    return SkillResult(
                        success=True,
                        message=faq["answer"],
                        data={"topic": faq_topic, "category": faq["category"]},
                        slots=slots,
                    )

        return SkillResult(
            success=True,
            message=(
                "您好，我可以为您解答以下常见问题：\n"
                "• 开户/办卡\n"
                "• 银行卡挂失\n"
                "• 修改密码\n"
                "• 存款利率\n"
                "• 转账手续费\n"
                "• 信用卡业务\n"
                "• 贷款业务\n"
                "• 网点查询\n"
                "请告诉我您想咨询什么？"
            ),
            data={"topic": "general", "category": "faq_menu"},
            slots=slots,
        )
