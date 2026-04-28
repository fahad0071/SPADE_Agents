"""Entry point for the Group 95 SPADE immigration assistant prototype."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

from agents.document_agent import DocumentAgent
from agents.eligibility_agent import EligibilityAgent
from agents.orchestrator_agent import OrchestratorAgent


DEFAULT_APPLICANT_PROFILE = {
    "applicant_name": "Fahad Zahid",
    "nationality": "Pakistan",
    "purpose": "study",
    "destination_country": "Finland",
    "university": "University of Jyvaskyla",
    "admission_letter": True,
}

ISSUE_SCENARIO_DOCUMENTS = {
    "passport": True,
    "admission_letter": True,
    "insurance": True,
    "bank_statement": True,
    "available_funds_eur": 5000,
}

SUCCESS_SCENARIO_DOCUMENTS = {
    "passport": True,
    "admission_letter": True,
    "insurance": True,
    "bank_statement": True,
    "available_funds_eur": 8000,
}


def load_env_file(env_path: Path) -> None:
    """Load simple KEY=VALUE pairs from a local .env file if present."""
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def build_document_payload() -> dict[str, object]:
    """Choose the demo scenario to run based on an environment variable."""
    demo_case = os.getenv("DEMO_CASE", "issue").strip().lower()
    if demo_case == "success":
        return SUCCESS_SCENARIO_DOCUMENTS.copy()
    return ISSUE_SCENARIO_DOCUMENTS.copy()


def env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


async def start_spade_gui(agent, label: str, host: str, port: int) -> None:
    await agent.web.start(hostname=host, port=port)
    print(f"[MAIN] {label} SPADE GUI: http://{host}:{port}/spade")


async def main() -> None:
    project_root = Path(__file__).resolve().parent
    load_env_file(project_root / ".env")

    orchestrator_jid = os.getenv("ORCHESTRATOR_JID", "orchestrator@localhost")
    orchestrator_password = os.getenv("ORCHESTRATOR_PASSWORD", "password")
    eligibility_jid = os.getenv("ELIGIBILITY_JID", "eligibility@localhost")
    eligibility_password = os.getenv("ELIGIBILITY_PASSWORD", "password")
    document_jid = os.getenv("DOCUMENT_JID", "document@localhost")
    document_password = os.getenv("DOCUMENT_PASSWORD", "password")
    spade_gui_enabled = env_flag("SPADE_GUI", default=False)
    spade_gui_host = os.getenv("SPADE_GUI_HOST", "127.0.0.1")
    post_run_hold_seconds = env_int("POST_RUN_HOLD_SECONDS", 8)
    spade_gui_hold_seconds = env_int("SPADE_GUI_HOLD_SECONDS", 120)

    applicant_profile = DEFAULT_APPLICANT_PROFILE.copy()
    document_payload = build_document_payload()

    print("[MAIN] Starting Group 95 SPADE immigration MAS prototype...")
    print(
        "[MAIN] Demo scenario selected: "
        f"{'success' if document_payload['available_funds_eur'] >= 6720 else 'issue'}"
    )

    eligibility_agent = EligibilityAgent(eligibility_jid, eligibility_password)
    document_agent = DocumentAgent(document_jid, document_password)
    orchestrator_agent = OrchestratorAgent(
        orchestrator_jid,
        orchestrator_password,
        eligibility_jid=eligibility_jid,
        document_jid=document_jid,
        applicant_profile=applicant_profile,
        document_payload=document_payload,
    )

    try:
        await eligibility_agent.start(auto_register=True)
        await document_agent.start(auto_register=True)

        if spade_gui_enabled:
            print("[MAIN] Starting SPADE web interfaces...")
            await start_spade_gui(
                eligibility_agent, "EligibilityAgent", spade_gui_host, 10001
            )
            await start_spade_gui(
                document_agent, "DocumentAgent", spade_gui_host, 10002
            )

        await orchestrator_agent.start(auto_register=True)

        if spade_gui_enabled:
            await start_spade_gui(
                orchestrator_agent, "OrchestratorAgent", spade_gui_host, 10000
            )

        await orchestrator_agent.workflow_complete.wait()
        if spade_gui_enabled:
            print(
                "[MAIN] Workflow complete. Keeping SPADE GUIs open for "
                f"{spade_gui_hold_seconds} seconds. Press Ctrl+C to stop earlier."
            )
            await asyncio.sleep(spade_gui_hold_seconds)
        else:
            print(
                "[MAIN] Workflow complete. Keeping agents alive for "
                f"{post_run_hold_seconds} seconds before shutdown."
            )
            await asyncio.sleep(post_run_hold_seconds)
    except KeyboardInterrupt:
        print("[MAIN] Shutdown requested by user.")
    finally:
        print("[MAIN] Stopping all agents...")
        await orchestrator_agent.stop()
        await eligibility_agent.stop()
        await document_agent.stop()
        print("[MAIN] Prototype execution finished.")


if __name__ == "__main__":
    asyncio.run(main())
