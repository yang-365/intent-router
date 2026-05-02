"""Menu recognition skill — identifies menu items and navigates the user."""

from __future__ import annotations

from typing import Any

from skills.base import (
    BaseSkill,
    SkillResult,
    SlotDefinition,
    SlotStatus,
    SlotValue,
)

MENU_ITEMS: dict[str, dict[str, Any]] = {
    "transfer": {
        "name": "转账汇款",
        "path": "/transfer",
        "keywords": ["转账", "汇款", "转钱"],
        "description": "向他人转账汇款",
        "children": [
            {"name": "银行卡转账", "path": "/transfer/card"},
            {"name": "手机号转账", "path": "/transfer/phone"},
            {"name": "跨行转账", "path": "/transfer/cross-bank"},
        ],
    },
    "payment": {
        "name": "生活缴费",
        "path": "/payment",
        "keywords": ["缴费", "交费", "电费", "水费", "话费", "燃气"],
        "description": "水电煤气话费等缴费",
        "children": [
            {"name": "电费", "path": "/payment/electricity"},
            {"name": "水费", "path": "/payment/water"},
            {"name": "燃气费", "path": "/payment/gas"},
            {"name": "话费充值", "path": "/payment/phone"},
        ],
    },
    "finance": {
        "name": "投资理财",
        "path": "/finance",
        "keywords": ["理财", "基金", "投资", "存款", "定期"],
        "description": "基金、理财产品、定期存款",
        "children": [
            {"name": "基金超市", "path": "/finance/fund"},
            {"name": "理财产品", "path": "/finance/wealth"},
            {"name": "定期存款", "path": "/finance/deposit"},
        ],
    },
    "account": {
        "name": "我的账户",
        "path": "/account",
        "keywords": ["账户", "余额", "明细", "流水", "账单"],
        "description": "账户余额、交易明细查询",
        "children": [
            {"name": "余额查询", "path": "/account/balance"},
            {"name": "交易明细", "path": "/account/transactions"},
            {"name": "电子回单", "path": "/account/receipt"},
        ],
    },
    "credit_card": {
        "name": "信用卡",
        "path": "/credit-card",
        "keywords": ["信用卡", "还款", "账单", "额度", "分期"],
        "description": "信用卡管理、还款、分期",
        "children": [
            {"name": "信用卡还款", "path": "/credit-card/repay"},
            {"name": "账单查询", "path": "/credit-card/bill"},
            {"name": "额度管理", "path": "/credit-card/limit"},
            {"name": "分期付款", "path": "/credit-card/installment"},
        ],
    },
    "loan": {
        "name": "贷款服务",
        "path": "/loan",
        "keywords": ["贷款", "借款", "借钱", "房贷", "车贷"],
        "description": "贷款申请与管理",
        "children": [
            {"name": "贷款申请", "path": "/loan/apply"},
            {"name": "贷款查询", "path": "/loan/query"},
            {"name": "还款管理", "path": "/loan/repay"},
        ],
    },
    "settings": {
        "name": "安全设置",
        "path": "/settings",
        "keywords": ["设置", "密码", "安全", "修改", "手机号"],
        "description": "账户安全与个人设置",
        "children": [
            {"name": "修改密码", "path": "/settings/password"},
            {"name": "手机号管理", "path": "/settings/phone"},
            {"name": "安全中心", "path": "/settings/security"},
        ],
    },
}


class MenuRecognitionSkill(BaseSkill):
    @property
    def skill_code(self) -> str:
        return "menu_recognition"

    @property
    def skill_name(self) -> str:
        return "菜单导航"

    @property
    def description(self) -> str:
        return "识别用户想要访问的功能菜单，提供导航引导。"

    @property
    def slot_definitions(self) -> list[SlotDefinition]:
        return [
            SlotDefinition(
                name="menu_target",
                description="目标菜单",
                required=False,
                examples=["转账", "缴费", "理财"],
            ),
        ]

    def extract_slots(
        self,
        user_input: str,
        current_slots: dict[str, Any],
    ) -> dict[str, SlotValue]:
        slots = super().extract_slots(user_input, current_slots)

        for menu_code, menu_info in MENU_ITEMS.items():
            for keyword in menu_info["keywords"]:
                if keyword in user_input:
                    slots["menu_target"] = SlotValue(
                        name="menu_target",
                        value=menu_code,
                        status=SlotStatus.FILLED,
                    )
                    return slots

        return slots

    async def execute(
        self,
        slots: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> SkillResult:
        target = slots.get("menu_target")

        if target and target in MENU_ITEMS:
            menu = MENU_ITEMS[target]
            children_text = "\n".join(
                f"  • {child['name']}" for child in menu["children"]
            )
            message = (
                f"已为您找到【{menu['name']}】功能：\n"
                f"{children_text}\n"
                f"请问您需要办理哪项业务？"
            )
            return SkillResult(
                success=True,
                message=message,
                data={
                    "menu_code": target,
                    "menu_name": menu["name"],
                    "path": menu["path"],
                    "children": menu["children"],
                    "action": "navigate",
                },
                slots=slots,
            )

        all_menus = "\n".join(
            f"  • {info['name']}（{info['description']}）"
            for info in MENU_ITEMS.values()
        )
        return SkillResult(
            success=True,
            message=f"掌银主要功能菜单：\n{all_menus}\n\n请问您需要使用哪个功能？",
            data={
                "action": "show_main_menu",
                "menus": [
                    {"code": code, "name": info["name"], "path": info["path"]}
                    for code, info in MENU_ITEMS.items()
                ],
            },
            slots=slots,
        )
