"""Authority ordering primitives."""

from enum import IntEnum


class AuthorityLevel(IntEnum):
    """Ordered authority levels from highest to lowest."""

    SOURCE_PRD_AND_PLATFORM = 10
    HUMAN_DECISION = 20
    LOCKED_CONSTITUTION_AND_CONTRACT = 30
    APPROVED_STAGE_ARTIFACT = 40
    RULE_AND_PROJECTION = 50
    SKILL_AND_WORKPACK = 60
    CANDIDATE_OUTPUT = 70


def can_override(actor: AuthorityLevel, target: AuthorityLevel) -> bool:
    """Return whether an actor can override a target under the authority order."""

    return actor <= target


def require_no_silent_override(actor: AuthorityLevel, target: AuthorityLevel) -> None:
    if not can_override(actor, target):
        raise ValueError(f"{actor.name} cannot override {target.name}")
