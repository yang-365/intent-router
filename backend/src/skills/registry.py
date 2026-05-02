"""Skill registry for discovering and managing available skills."""

from __future__ import annotations

from typing import Any

from skills.base import BaseSkill


class SkillRegistry:
    """Central registry that maps skill codes to skill instances."""

    def __init__(self) -> None:
        self._skills: dict[str, BaseSkill] = {}

    def register(self, skill: BaseSkill) -> None:
        self._skills[skill.skill_code] = skill

    def get(self, skill_code: str) -> BaseSkill | None:
        return self._skills.get(skill_code)

    def list_skills(self) -> list[dict[str, Any]]:
        return [
            {
                "skill_code": skill.skill_code,
                "skill_name": skill.skill_name,
                "description": skill.description,
                "slots": [
                    {
                        "name": slot.name,
                        "description": slot.description,
                        "required": slot.required,
                        "type": slot.slot_type,
                    }
                    for slot in skill.slot_definitions
                ],
            }
            for skill in self._skills.values()
        ]

    @property
    def skill_codes(self) -> list[str]:
        return list(self._skills.keys())


_global_registry: SkillRegistry | None = None


def get_skill_registry() -> SkillRegistry:
    """Return the global skill registry, creating and populating it on first call."""
    global _global_registry  # noqa: PLW0603
    if _global_registry is None:
        _global_registry = SkillRegistry()
        _register_builtin_skills(_global_registry)
    return _global_registry


def _register_builtin_skills(registry: SkillRegistry) -> None:
    from skills.bill_payment_skill import BillPaymentSkill
    from skills.consultation_skill import ConsultationSkill
    from skills.fund_recommendation_skill import FundRecommendationSkill
    from skills.menu_skill import MenuRecognitionSkill
    from skills.transfer_skill import TransferSkill

    registry.register(TransferSkill())
    registry.register(BillPaymentSkill())
    registry.register(FundRecommendationSkill())
    registry.register(ConsultationSkill())
    registry.register(MenuRecognitionSkill())
