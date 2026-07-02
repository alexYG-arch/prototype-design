"""Codex runtime adapter for governed stage continuation."""

import os
import shlex
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Optional, Sequence


@dataclass(frozen=True)
class CodexRuntimeResult:
    status: str
    command: Sequence[str]
    exit_code: int
    stdout: str
    stderr: str
    unavailable_reason: str = ""

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "command": list(self.command),
            "exit_code": self.exit_code,
            "stdout": _truncate(self.stdout),
            "stderr": _truncate(self.stderr),
            "unavailable_reason": self.unavailable_reason,
        }


def run_codex_runtime(
    *,
    prompt_text: str,
    work_dir: Path,
    prompt_file: Path,
    output_dir: Path,
    stage_id: str,
    expected_outputs: Sequence[str],
    run_state_ref: Path,
    runtime_command: Optional[str] = None,
    codex_bin: Optional[str] = None,
    model: Optional[str] = None,
    timeout_seconds: int = 1800,
    output_last_message: Optional[Path] = None,
) -> CodexRuntimeResult:
    command, unavailable = _build_command(
        work_dir=work_dir,
        runtime_command=runtime_command,
        codex_bin=codex_bin,
        model=model,
        output_last_message=output_last_message,
    )
    if unavailable:
        return CodexRuntimeResult(
            status="CODEX_RUNTIME_UNAVAILABLE",
            command=command,
            exit_code=127,
            stdout="",
            stderr="",
            unavailable_reason=unavailable,
        )

    env = os.environ.copy()
    env.update(
        {
            "DRD_HARNESS_STAGE_ID": stage_id,
            "DRD_HARNESS_STAGE_OUTPUT_DIR": (output_dir / stage_id).as_posix(),
            "DRD_HARNESS_OUTPUT_DIR": output_dir.as_posix(),
            "DRD_HARNESS_PROMPT_FILE": prompt_file.as_posix(),
            "DRD_HARNESS_RUN_STATE_REF": run_state_ref.as_posix(),
            "DRD_HARNESS_EXPECTED_OUTPUTS": "\n".join(expected_outputs),
        }
    )

    try:
        completed = subprocess.run(
            list(command),
            cwd=work_dir,
            env=env,
            input=prompt_text,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return CodexRuntimeResult(
            status="CODEX_RUNTIME_FAILED",
            command=command,
            exit_code=124,
            stdout=exc.stdout or "",
            stderr=exc.stderr or "codex runtime timed out",
        )
    except OSError as exc:
        return CodexRuntimeResult(
            status="CODEX_RUNTIME_UNAVAILABLE",
            command=command,
            exit_code=127,
            stdout="",
            stderr="",
            unavailable_reason=str(exc),
        )

    return CodexRuntimeResult(
        status="CODEX_RUNTIME_COMPLETED" if completed.returncode == 0 else "CODEX_RUNTIME_FAILED",
        command=command,
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def _build_command(
    *,
    work_dir: Path,
    runtime_command: Optional[str],
    codex_bin: Optional[str],
    model: Optional[str],
    output_last_message: Optional[Path],
) -> tuple[Sequence[str], str]:
    if runtime_command:
        command = shlex.split(runtime_command)
        if not command:
            return [], "runtime command is empty"
        executable = command[0]
        if Path(executable).is_absolute():
            if not Path(executable).exists():
                return command, f"runtime command not found: {executable}"
        elif shutil.which(executable) is None:
            return command, f"runtime command not found on PATH: {executable}"
        return command, ""

    executable = codex_bin or shutil.which("codex")
    if not executable:
        return ["codex", "exec"], "codex executable not found on PATH"
    command = [
        executable,
        "exec",
        "-C",
        work_dir.as_posix(),
        "--sandbox",
        "workspace-write",
    ]
    if model:
        command.extend(["-m", model])
    if output_last_message:
        command.extend(["--output-last-message", output_last_message.as_posix()])
    command.append("-")
    return command, ""


def _truncate(value: str, limit: int = 12000) -> str:
    if len(value) <= limit:
        return value
    return value[:limit] + "\n[truncated]"
