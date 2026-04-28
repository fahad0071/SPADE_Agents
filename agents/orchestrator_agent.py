"""Orchestrator agent for the student residence permit workflow."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from spade.behaviour import CyclicBehaviour
from spade.message import Message

from agents.base_agent import LocalAgent


class OrchestratorAgent(LocalAgent):
    """Coordinates the eligibility and document verification workflow."""

    def __init__(
        self,
        jid: str,
        password: str,
        eligibility_jid: str,
        document_jid: str,
        applicant_profile: dict[str, Any],
        document_payload: dict[str, Any],
        **kwargs: Any,
    ) -> None:
        super().__init__(jid, password, **kwargs)
        self.eligibility_jid = eligibility_jid
        self.document_jid = document_jid
        self.applicant_profile = applicant_profile
        self.document_payload = document_payload
        self.workflow_complete = asyncio.Event()

    class WorkflowBehaviour(CyclicBehaviour):
        async def on_start(self) -> None:
            self.state = "START"
            self.final_summary = None
            print("[OrchestratorAgent] Started application workflow.")

        async def run(self) -> None:
            if self.state == "START":
                await self.send_eligibility_request()
                self.state = "WAITING_FOR_ELIGIBILITY"
                return

            msg = await self.receive(timeout=15)
            if msg is None:
                if self.state != "COMPLETED":
                    print(
                        "[OrchestratorAgent] Waiting for the next agent response..."
                    )
                return

            ontology = msg.get_metadata("ontology")

            if self.state == "WAITING_FOR_ELIGIBILITY":
                await self.handle_eligibility_result(msg, ontology)
                return

            if self.state == "WAITING_FOR_DOCUMENTS":
                await self.handle_document_result(msg, ontology)
                return

        async def send_eligibility_request(self) -> None:
            print(
                "[OrchestratorAgent] Sending applicant profile to EligibilityAgent..."
            )
            print(
                "[OrchestratorAgent] Applicant profile payload: "
                f"{json.dumps(self.agent.applicant_profile)}"
            )

            msg = Message(to=self.agent.eligibility_jid)
            msg.body = json.dumps(self.agent.applicant_profile)
            msg.set_metadata("performative", "request")
            msg.set_metadata("ontology", "immigration-eligibility")
            await self.send(msg)

        async def handle_eligibility_result(self, msg: Message, ontology: str | None) -> None:
            if ontology != "immigration-eligibility-result":
                print(
                    "[OrchestratorAgent] Ignored unexpected message while waiting for "
                    "eligibility result."
                )
                return

            result = json.loads(msg.body)
            print(
                "[OrchestratorAgent] Received eligibility result: "
                f"{result['visa_type']}."
            )
            print(
                "[OrchestratorAgent] Eligibility reason: "
                f"{result['reason']}"
            )

            if result.get("eligible") is True:
                print(
                    "[OrchestratorAgent] Eligibility accepted. Sending documents to "
                    "DocumentAgent..."
                )
                await self.send_document_request()
                self.state = "WAITING_FOR_DOCUMENTS"
                return

            print(
                "[OrchestratorAgent] Final decision: Manual review required before "
                "document verification."
            )
            self.final_summary = "Application requires manual review."
            self.state = "COMPLETED"
            self.agent.workflow_complete.set()
            self.kill()

        async def send_document_request(self) -> None:
            print(
                "[OrchestratorAgent] Uploaded documents payload: "
                f"{json.dumps(self.agent.document_payload)}"
            )

            msg = Message(to=self.agent.document_jid)
            msg.body = json.dumps(self.agent.document_payload)
            msg.set_metadata("performative", "request")
            msg.set_metadata("ontology", "document-verification")
            await self.send(msg)

        async def handle_document_result(self, msg: Message, ontology: str | None) -> None:
            if ontology != "document-verification-result":
                print(
                    "[OrchestratorAgent] Ignored unexpected message while waiting for "
                    "document verification result."
                )
                return

            result = json.loads(msg.body)
            print("[OrchestratorAgent] Received document verification result.")

            if result["status"] == "DOCUMENTS_ACCEPTED":
                print("[OrchestratorAgent] Final decision: Application ready for submission.")
                print(
                    "[OrchestratorAgent] Action: Student Residence Permit recommended "
                    "and documents accepted."
                )
                self.final_summary = "Application ready for submission."
            else:
                missing_documents = result.get("missing_documents", [])
                issue = result.get("issue")

                if missing_documents:
                    print(
                        "[OrchestratorAgent] Warning: Missing documents -> "
                        f"{', '.join(missing_documents)}."
                    )

                if issue == "Insufficient funds":
                    print(
                        "[OrchestratorAgent] Action required: Increase financial proof "
                        f"to at least {result['required_funds_eur']} EUR. "
                        f"Available: {result['available_funds_eur']} EUR."
                    )
                else:
                    print(
                        "[OrchestratorAgent] Action required: Resolve document issues "
                        "before submission."
                    )

                print(
                    "[OrchestratorAgent] Final decision: Application not ready for "
                    "submission."
                )
                self.final_summary = "Application not ready for submission."

            self.state = "COMPLETED"
            self.agent.workflow_complete.set()
            self.kill()

    async def setup(self) -> None:
        self.add_behaviour(self.WorkflowBehaviour())
