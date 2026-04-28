# Group 95 Second Project: SPADE Multi-Agent Visa and Immigration Assistant

This repository contains a beginner-friendly SPADE prototype for the Agent Technologies course. It implements a focused version of the earlier GAIA design for a visa and immigration application assistant, using the student residence permit scenario for Finland.

## Project scope

The prototype demonstrates:

- Three SPADE agents communicating with JSON messages over XMPP.
- Domain-specific decision making for visa eligibility and document verification.
- Autonomous orchestration of the workflow from profile submission to final guidance.

This is intentionally a small prototype, not the full seven-agent production design from the earlier course phase.

## Agents implemented

- `OrchestratorAgent`: starts the workflow, coordinates message exchange, and prints the final decision.
- `EligibilityAgent`: checks whether the applicant qualifies for the Student Residence Permit.
- `DocumentAgent`: verifies mandatory documents and checks the minimum funds rule.

## Communication flow

1. `OrchestratorAgent` sends the applicant profile to `EligibilityAgent`.
2. `EligibilityAgent` returns an eligibility result.
3. `OrchestratorAgent` decides whether to continue.
4. `OrchestratorAgent` sends document data to `DocumentAgent`.
5. `DocumentAgent` returns a document verification result.
6. `OrchestratorAgent` prints the final application guidance.

## Installation

Create and activate a local virtual environment, then install the dependency:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## XMPP configuration

SPADE agents require XMPP accounts. Configure the JIDs and passwords either through environment variables or a local `.env` file in the project root.

Example `.env`:

```text
ORCHESTRATOR_JID=orchestrator@localhost
ORCHESTRATOR_PASSWORD=password
ELIGIBILITY_JID=eligibility@localhost
ELIGIBILITY_PASSWORD=password
DOCUMENT_JID=document@localhost
DOCUMENT_PASSWORD=password
DEMO_CASE=issue
```

## Local Prosody option

This project also includes a lightweight local Prosody setup under [`xmpp/`](./xmpp). It is useful for demos and screenshots on a single machine.

Start the local XMPP server with:

```bash
./start_local_prosody.sh
```

Then run the SPADE agents in a second terminal:

```bash
./run_issue_demo.sh
```

## How to run

From this folder:

```bash
./run_issue_demo.sh
```

successful scenario:

```bash
./run_success_demo.sh
```

SPADE GUI issue scenario:

```bash
./run_issue_demo_gui.sh
```

SPADE GUI success scenario:

```bash
./run_success_demo_gui.sh
```


## SPADE web GUI

The GUI mode starts SPADE's built-in web interface for each agent:

- OrchestratorAgent: `http://127.0.0.1:10000/spade`
- EligibilityAgent: `http://127.0.0.1:10001/spade`
- DocumentAgent: `http://127.0.0.1:10002/spade`


## Expected output

For the recommended issue scenario, the console should show:

- The three agents starting.
- The orchestrator sending the applicant profile to the eligibility agent.
- A Student Residence Permit recommendation.
- A document verification result showing insufficient funds.
- A final decision that the application is not ready for submission.


## Suggested screenshot flow

1. In Terminal 1, run `./start_local_prosody.sh`.
2. In Terminal 2, run `./run_issue_demo_gui.sh` and capture:
   - agent startup
   - eligibility exchange
   - document issue result
   - final orchestrator decision
3. Open `http://127.0.0.1:10000/spade` for the OrchestratorAgent GUI.
4. Run `./run_success_demo_gui.sh` if you also want a success-case screenshot.

## Connection to the previous GAIA design

This prototype is derived from the earlier Group 95 GAIA artifacts:

- The project domain remains visa and immigration application support.
- The orchestrator keeps the central coordination role from the GAIA role model.
- The eligibility and document verification logic reflects Scenario 1 from the preliminary interaction model.
- The service model for the Eligibility Agent is simplified into a deterministic rule-based recommendation.
