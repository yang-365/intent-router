from __future__ import annotations

import os

from config.settings import _load_local_env_files
from router_core.domain import IntentDefinition


_load_local_env_files()


def _svc_base_url(service_name: str, *, local_port: int) -> str:
    namespace = os.getenv("INTENT_ROUTER_NAMESPACE", "intent")
    if os.getenv("KUBERNETES_SERVICE_HOST"):
        return f"http://{service_name}.{namespace}.svc.cluster.local:8000"
    return f"http://127.0.0.1:{local_port}"


def _agent_url(env_name: str, service_name: str, *, local_port: int) -> str:
    override = os.getenv(env_name)
    if override:
        return override
    return f"{_svc_base_url(service_name, local_port=local_port)}/api/agent/run"


DEMO_INTENTS: list[IntentDefinition] = [
    IntentDefinition(
        intent_code="query_account_balance",
        name="查询账户余额",
        description="查询用户账户余额。需要收集卡号和手机号后4位，信息齐全后返回余额结果。",
        examples=["帮我查一下账户余额", "查余额", "查询银行卡余额"],
        keywords=["余额", "账户", "银行卡", "查余额"],
        agent_url=_agent_url("QUERY_ACCOUNT_BALANCE_AGENT_URL", "intent-order-agent", local_port=8101),
        dispatch_priority=100,
        primary_threshold=0.68,
        candidate_threshold=0.45,
        request_schema={
            "type": "object",
            "required": ["sessionId", "taskId", "input", "conversation.recentMessages"],
        },
        field_mapping={
            "sessionId": "$session.id",
            "taskId": "$task.id",
            "input": "$message.current",
            "customer.custId": "$session.cust_id",
            "conversation.recentMessages": "$context.recent_messages",
            "conversation.longTermMemory": "$context.long_term_memory",
            "account.cardNumber": "$slot_memory.card_number",
            "account.phoneLast4": "$slot_memory.phone_last_four",
        },
    ),
    IntentDefinition(
        intent_code="transfer_money",
        name="转账",
        description="执行转账。需要收集收款人姓名、收款卡号、收款人手机号后4位和转账金额。",
        examples=["给张三转 200 元", "帮我给李四转账", "转账到对方银行卡"],
        keywords=["转账", "收款人", "卡号", "金额", "汇款"],
        agent_url=_agent_url("TRANSFER_MONEY_AGENT_URL", "intent-appointment-agent", local_port=8102),
        dispatch_priority=95,
        primary_threshold=0.72,
        candidate_threshold=0.5,
        request_schema={
            "type": "object",
            "required": ["sessionId", "taskId", "input", "conversation.recentMessages"],
        },
        field_mapping={
            "sessionId": "$session.id",
            "taskId": "$task.id",
            "input": "$message.current",
            "customer.custId": "$session.cust_id",
            "conversation.recentMessages": "$context.recent_messages",
            "conversation.longTermMemory": "$context.long_term_memory",
            "recipient.name": "$slot_memory.recipient_name",
            "recipient.cardNumber": "$slot_memory.recipient_card_number",
            "recipient.phoneLast4": "$slot_memory.recipient_phone_last_four",
            "transfer.amount": "$slot_memory.amount",
        },
    ),
    IntentDefinition(
        intent_code="update_shipping_address",
        name="修改收货地址",
        description="更新订单收货地址、配送地址。",
        examples=["帮我改一下收货地址", "更新配送地址"],
        keywords=["地址", "收货", "配送", "改成"],
        agent_url="mock://update_shipping_address",
        dispatch_priority=90,
        primary_threshold=0.65,
        candidate_threshold=0.45,
    ),
    IntentDefinition(
        intent_code="pay_bill",
        name="生活缴费",
        description="水电煤气、话费、宽带费、物业费等生活缴费。需要收集缴费类型和户号。",
        examples=["帮我缴电费", "交一下话费", "缴水费", "充话费", "交燃气费"],
        keywords=["缴费", "交费", "电费", "水费", "话费", "燃气费", "宽带费", "物业费", "充值"],
        agent_url=_agent_url("BILL_PAYMENT_AGENT_URL", "intent-bill-payment-agent", local_port=8103),
        dispatch_priority=85,
        primary_threshold=0.70,
        candidate_threshold=0.50,
        request_schema={
            "type": "object",
            "required": ["sessionId", "taskId", "input"],
        },
        field_mapping={
            "sessionId": "$session.id",
            "taskId": "$task.id",
            "input": "$message.current",
            "customer.custId": "$session.cust_id",
            "conversation.recentMessages": "$context.recent_messages",
            "conversation.longTermMemory": "$context.long_term_memory",
            "billType": "$slot_memory.bill_type",
            "accountNumber": "$slot_memory.account_number",
            "amount": "$slot_memory.amount",
        },
    ),
    IntentDefinition(
        intent_code="fund_recommendation",
        name="基金推荐",
        description="根据用户风险偏好和投资金额推荐合适的基金产品。",
        examples=["推荐一些基金", "有什么好的理财产品", "帮我选个基金", "稳健型基金有哪些"],
        keywords=["基金", "理财", "投资", "推荐", "收益", "风险"],
        agent_url=_agent_url("FUND_RECOMMENDATION_AGENT_URL", "intent-fund-agent", local_port=8104),
        dispatch_priority=80,
        primary_threshold=0.68,
        candidate_threshold=0.48,
        request_schema={
            "type": "object",
            "required": ["sessionId", "taskId", "input"],
        },
        field_mapping={
            "sessionId": "$session.id",
            "taskId": "$task.id",
            "input": "$message.current",
            "customer.custId": "$session.cust_id",
            "conversation.recentMessages": "$context.recent_messages",
            "conversation.longTermMemory": "$context.long_term_memory",
            "riskLevel": "$slot_memory.risk_level",
            "fundType": "$slot_memory.fund_type",
            "investmentAmount": "$slot_memory.investment_amount",
        },
    ),
    IntentDefinition(
        intent_code="consultation",
        name="业务咨询",
        description="回答用户关于银行业务的常见问题，包括开户、挂失、利率、手续费、信用卡、贷款等。",
        examples=["怎么开户", "利率是多少", "转账手续费多少", "怎么挂失银行卡", "信用卡怎么申请"],
        keywords=["咨询", "怎么", "如何", "什么是", "开户", "挂失", "利率", "手续费", "信用卡", "贷款"],
        agent_url=_agent_url("CONSULTATION_AGENT_URL", "intent-consultation-agent", local_port=8105),
        dispatch_priority=60,
        primary_threshold=0.60,
        candidate_threshold=0.40,
        request_schema={
            "type": "object",
            "required": ["sessionId", "taskId", "input"],
        },
        field_mapping={
            "sessionId": "$session.id",
            "taskId": "$task.id",
            "input": "$message.current",
            "customer.custId": "$session.cust_id",
            "conversation.recentMessages": "$context.recent_messages",
            "conversation.longTermMemory": "$context.long_term_memory",
        },
    ),
    IntentDefinition(
        intent_code="menu_navigation",
        name="菜单导航",
        description="识别用户想要访问的功能菜单，提供导航引导。帮助用户快速找到掌银功能入口。",
        examples=["功能菜单在哪", "帮我找转账功能", "怎么交电费", "理财产品在哪里"],
        keywords=["菜单", "功能", "在哪", "怎么找", "入口", "导航"],
        agent_url=_agent_url("MENU_RECOGNITION_AGENT_URL", "intent-menu-agent", local_port=8106),
        dispatch_priority=50,
        primary_threshold=0.55,
        candidate_threshold=0.35,
        request_schema={
            "type": "object",
            "required": ["sessionId", "taskId", "input"],
        },
        field_mapping={
            "sessionId": "$session.id",
            "taskId": "$task.id",
            "input": "$message.current",
            "customer.custId": "$session.cust_id",
            "conversation.recentMessages": "$context.recent_messages",
            "conversation.longTermMemory": "$context.long_term_memory",
        },
    ),
]
