"""Eligibility agent for the student residence permit scenario."""

from __future__ import annotations

import json

from spade.behaviour import CyclicBehaviour

from agents.base_agent import LocalAgent


class EligibilityAgent(LocalAgent):
    """Determines the visa or residence permit recommendation."""

    class EligibilityBehaviour(CyclicBehaviour):
        async def run(self) -> None:
            msg = await self.receive(timeout=10)
            if msg is None:
                return

            print(
                f"[EligibilityAgent] Received eligibility request from {msg.sender}"
            )

            profile = json.loads(msg.body)
            eligible = (
                profile.get("purpose") == "study"
                and profile.get("destination_country") == "Finland"
                and profile.get("admission_letter") is True
            )

            if eligible:
                result = {
                    "eligible": True,
                    "visa_type": "Student Residence Permit",
                    "reason": (
                        "Applicant is studying in Finland and has a valid admission "
                        "letter."
                    ),
                }
                print(
                    "[EligibilityAgent] Decision: eligible for Student Residence Permit."
                )
            else:
                result = {
                    "eligible": False,
                    "visa_type": "Manual Review Required",
                    "reason": (
                        "The applicant profile does not satisfy the automatic study "
                        "permit rule."
                    ),
                }
                print("[EligibilityAgent] Decision: manual review required.")

            response = msg.make_reply()
            response.body = json.dumps(result)
            response.set_metadata("performative", "inform")
            response.set_metadata("ontology", "immigration-eligibility-result")

            await self.send(response)
            print("[EligibilityAgent] Sent eligibility result to OrchestratorAgent.")

    async def setup(self) -> None:
        print("[EligibilityAgent] Started and waiting for eligibility requests.")
        self.add_behaviour(self.EligibilityBehaviour())
