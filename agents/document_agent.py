"""Document verification agent for the student residence permit scenario."""

from __future__ import annotations

import json

from spade.behaviour import CyclicBehaviour

from agents.base_agent import LocalAgent


MANDATORY_DOCUMENTS = [
    "passport",
    "admission_letter",
    "insurance",
    "bank_statement",
]
MINIMUM_REQUIRED_FUNDS_EUR = 6720


class DocumentAgent(LocalAgent):
    """Checks whether the submitted application documents are sufficient."""

    class DocumentVerificationBehaviour(CyclicBehaviour):
        async def run(self) -> None:
            msg = await self.receive(timeout=10)
            if msg is None:
                return

            print("[DocumentAgent] Received document verification request.")

            documents = json.loads(msg.body)
            missing_documents = [
                name for name in MANDATORY_DOCUMENTS if not documents.get(name, False)
            ]
            available_funds = documents.get("available_funds_eur", 0)

            if missing_documents:
                result = {
                    "status": "DOCUMENT_ISSUE",
                    "missing_documents": missing_documents,
                    "issue": "Missing mandatory documents",
                    "required_funds_eur": MINIMUM_REQUIRED_FUNDS_EUR,
                    "available_funds_eur": available_funds,
                }
                print(
                    "[DocumentAgent] Decision: missing documents detected -> "
                    f"{', '.join(missing_documents)}."
                )
            elif available_funds < MINIMUM_REQUIRED_FUNDS_EUR:
                result = {
                    "status": "DOCUMENT_ISSUE",
                    "missing_documents": [],
                    "issue": "Insufficient funds",
                    "required_funds_eur": MINIMUM_REQUIRED_FUNDS_EUR,
                    "available_funds_eur": available_funds,
                }
                print("[DocumentAgent] Decision: insufficient funds detected.")
            else:
                result = {
                    "status": "DOCUMENTS_ACCEPTED",
                    "missing_documents": [],
                    "issue": None,
                    "required_funds_eur": MINIMUM_REQUIRED_FUNDS_EUR,
                    "available_funds_eur": available_funds,
                }
                print("[DocumentAgent] Decision: documents accepted.")

            response = msg.make_reply()
            response.body = json.dumps(result)
            response.set_metadata("performative", "inform")
            response.set_metadata("ontology", "document-verification-result")

            await self.send(response)
            print("[DocumentAgent] Sent document verification result to OrchestratorAgent.")

    async def setup(self) -> None:
        print("[DocumentAgent] Started and waiting for document verification requests.")
        self.add_behaviour(self.DocumentVerificationBehaviour())
