"""Runtime declaration model."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Mapping


class PrimaryRuntime(str, Enum):
    PYTHON = "PYTHON"
    CODEX = "CODEX"
    CODEX_PYTHON_LOOP = "CODEX_PYTHON_LOOP"
    HUMAN_GATE = "HUMAN_GATE"


REQUIRED_RUNTIME_FIELDS = {
    "unit_id",
    "primary_runtime",
    "python_duties",
    "codex_duties",
    "validator",
    "human_gate",
    "authority_inputs",
    "write_scope",
    "forbidden_scope",
}

CODEX_FORBIDDEN_DUTY_TERMS = {
    "approve",
    "approval",
    "promote",
    "promotion",
    "lock",
    "canonical",
    "seal",
}


@dataclass(frozen=True)
class RuntimeDeclaration:
    unit_id: str
    primary_runtime: PrimaryRuntime
    python_duties: List[str]
    codex_duties: List[str]
    validator: str
    human_gate: str
    authority_inputs: List[str]
    write_scope: List[str]
    forbidden_scope: List[str]

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "RuntimeDeclaration":
        missing = sorted(REQUIRED_RUNTIME_FIELDS - set(data))
        if missing:
            raise ValueError(f"runtime declaration missing fields: {', '.join(missing)}")

        return cls(
            unit_id=_required_text(data, "unit_id"),
            primary_runtime=PrimaryRuntime(_required_text(data, "primary_runtime")),
            python_duties=_text_list(data, "python_duties"),
            codex_duties=_text_list(data, "codex_duties"),
            validator=_required_text(data, "validator"),
            human_gate=_required_text(data, "human_gate"),
            authority_inputs=_required_text_list(data, "authority_inputs"),
            write_scope=_required_text_list(data, "write_scope"),
            forbidden_scope=_required_text_list(data, "forbidden_scope"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "unit_id": self.unit_id,
            "primary_runtime": self.primary_runtime.value,
            "python_duties": list(self.python_duties),
            "codex_duties": list(self.codex_duties),
            "validator": self.validator,
            "human_gate": self.human_gate,
            "authority_inputs": list(self.authority_inputs),
            "write_scope": list(self.write_scope),
            "forbidden_scope": list(self.forbidden_scope),
        }

    def validate_responsibilities(self) -> None:
        codex_text = " ".join(self.codex_duties).lower()
        forbidden = sorted(term for term in CODEX_FORBIDDEN_DUTY_TERMS if term in codex_text)
        if forbidden:
            raise ValueError("codex duties include authority-changing terms: " + ", ".join(forbidden))

        if self.primary_runtime == PrimaryRuntime.PYTHON and self.codex_duties:
            raise ValueError("PYTHON runtime declarations must not assign Codex duties")


def _required_text(data: Mapping[str, Any], key: str) -> str:
    value = data[key]
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value


def _required_text_list(data: Mapping[str, Any], key: str) -> List[str]:
    value = data[key]
    if not isinstance(value, list) or not value:
        raise ValueError(f"{key} must be a non-empty list")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError(f"{key} must contain only non-empty strings")
    return list(value)


def _text_list(data: Mapping[str, Any], key: str) -> List[str]:
    value = data[key]
    if not isinstance(value, list):
        raise ValueError(f"{key} must be a list")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError(f"{key} must contain only non-empty strings")
    return list(value)
