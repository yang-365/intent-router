"""Base skill abstraction for the banking assistant.

A Skill encapsulates:
1. Slot definitions (required parameters)
2. Parameter extraction logic
3. Business workflow execution via API tools
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class SlotStatus(StrEnum):
    MISSING = "missing"
    FILLED = "filled"
    CONFIRMED = "confirmed"


@dataclass(slots=True)
class SlotDefinition:
    name: str
    description: str
    required: bool = True
    slot_type: str = "string"
    examples: list[str] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)


@dataclass(slots=True)
class SlotValue:
    name: str
    value: Any = None
    status: SlotStatus = SlotStatus.MISSING

    @property
    def is_filled(self) -> bool:
        return self.status in (SlotStatus.FILLED, SlotStatus.CONFIRMED)


@dataclass(slots=True)
class SkillResult:
    success: bool
    message: str
    data: dict[str, Any] = field(default_factory=dict)
    slots: dict[str, Any] = field(default_factory=dict)
    needs_more_info: bool = False
    missing_slots: list[str] = field(default_factory=list)


class BaseSkill(ABC):
    """Abstract base class for all banking assistant skills."""

    @property
    @abstractmethod
    def skill_code(self) -> str:
        """Unique identifier for this skill."""

    @property
    @abstractmethod
    def skill_name(self) -> str:
        """Human-readable name."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what this skill does."""

    @property
    @abstractmethod
    def slot_definitions(self) -> list[SlotDefinition]:
        """Slot definitions for parameter extraction."""

    def extract_slots(
        self,
        user_input: str,
        current_slots: dict[str, Any],
    ) -> dict[str, SlotValue]:
        """Extract slot values from user input using rule-based logic.

        Subclasses override this for custom extraction patterns.
        """
        slots: dict[str, SlotValue] = {}
        for slot_def in self.slot_definitions:
            existing = current_slots.get(slot_def.name)
            if existing is not None and str(existing).strip():
                slots[slot_def.name] = SlotValue(
                    name=slot_def.name,
                    value=existing,
                    status=SlotStatus.FILLED,
                )
            else:
                slots[slot_def.name] = SlotValue(name=slot_def.name)
        return slots

    def missing_required_slots(self, slots: dict[str, SlotValue]) -> list[str]:
        """Return names of required slots that are still missing."""
        required_names = {s.name for s in self.slot_definitions if s.required}
        return sorted(
            name for name in required_names
            if name not in slots or not slots[name].is_filled
        )

    @abstractmethod
    async def execute(
        self,
        slots: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> SkillResult:
        """Execute the business workflow with the collected slots."""

    def build_ask_message(self, missing: list[str]) -> str:
        """Build a user-friendly message asking for missing information."""
        slot_map = {s.name: s for s in self.slot_definitions}
        descriptions = [slot_map[name].description for name in missing if name in slot_map]
        return "请提供以下信息：" + "、".join(descriptions)
