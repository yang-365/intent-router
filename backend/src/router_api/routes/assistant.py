"""Banking assistant API routes — skill listing, tool listing, and direct skill execution."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from api_tools.registry import get_tool_registry
from skills.registry import get_skill_registry

router = APIRouter(prefix="/api/router/assistant", tags=["assistant"])


class SkillExecuteRequest(BaseModel):
    skill_code: str
    user_input: str = ""
    current_slots: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] = Field(default_factory=dict)


class ToolCallRequest(BaseModel):
    tool_code: str
    params: dict[str, Any] = Field(default_factory=dict)


@router.get("/skills")
async def list_skills() -> dict[str, Any]:
    registry = get_skill_registry()
    return {"skills": registry.list_skills()}


@router.get("/tools")
async def list_tools() -> dict[str, Any]:
    registry = get_tool_registry()
    return {"tools": registry.list_tools()}


@router.post("/skills/{skill_code}/extract")
async def extract_slots(skill_code: str, request: SkillExecuteRequest) -> dict[str, Any]:
    registry = get_skill_registry()
    skill = registry.get(skill_code)
    if skill is None:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_code}' not found")

    extracted = skill.extract_slots(request.user_input, request.current_slots)
    missing = skill.missing_required_slots(extracted)

    return {
        "skill_code": skill_code,
        "slots": {
            name: {"value": sv.value, "status": sv.status.value}
            for name, sv in extracted.items()
        },
        "missing_slots": missing,
        "all_filled": len(missing) == 0,
        "ask_message": skill.build_ask_message(missing) if missing else None,
    }


@router.post("/skills/{skill_code}/execute")
async def execute_skill(skill_code: str, request: SkillExecuteRequest) -> dict[str, Any]:
    registry = get_skill_registry()
    skill = registry.get(skill_code)
    if skill is None:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_code}' not found")

    extracted = skill.extract_slots(request.user_input, request.current_slots)
    missing = skill.missing_required_slots(extracted)

    if missing:
        return {
            "success": False,
            "needs_more_info": True,
            "missing_slots": missing,
            "ask_message": skill.build_ask_message(missing),
            "current_slots": {
                name: sv.value for name, sv in extracted.items() if sv.is_filled
            },
        }

    filled_slots = {name: sv.value for name, sv in extracted.items() if sv.is_filled}
    result = await skill.execute(filled_slots, context=request.context)

    return {
        "success": result.success,
        "message": result.message,
        "data": result.data,
        "slots": result.slots,
    }


@router.post("/tools/{tool_code}/call")
async def call_tool(tool_code: str, request: ToolCallRequest) -> dict[str, Any]:
    registry = get_tool_registry()
    tool = registry.get(tool_code)
    if tool is None:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_code}' not found")

    result = await tool.call(request.params)
    return result
