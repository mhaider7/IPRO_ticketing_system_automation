# Hawk backend plan

This is a repository summary of the team's agreed `OTS_Chatbot_Backend_Guide.pdf`. The PDF is the source for the full six-part assignment and detailed acceptance criteria. This file makes the current repository scope clear; it is not an implementation status report.

## Student flow for this version

1. A student asks Hawk a question. The frontend sends the conversation so far to `POST /api/chat`.
2. The backend checks topics that always need a person before searching for an answer.
3. For other questions, it retrieves relevant, source-labeled OTS material from a local ChromaDB index and asks a local Ollama model to answer using that material and recent conversation context.
4. If the topic requires a person, the available evidence is inadequate, confidence is low, or the student requests help, Hawk switches to escalation. It may ask one or two clarifying questions.
5. Hawk returns a formatted support email draft in the chat. The student reviews, copies, and sends it themselves.

The guide excludes student login, automatic email delivery, and collection or storage of personal student identifiers for this version. It does not require creating or updating a TeamDynamix ticket.

## Frontend API contract

| Route | Request | Response |
| --- | --- | --- |
| `POST /api/chat` | Full conversation as `messages` with `role` and `text` | `reply`, `sources`, `escalate`, `escalation_reason` |
| `POST /api/escalate` | Full conversation as `messages` | An `email` object (`to`, `subject`, `body`) or a `clarifying_question` |
| `GET /api/health` | No body | `{ "status": "ok" }` |

The guide defines escalation reasons as `fixed_topic`, `low_confidence`, and `user_request`. Keep the frontend and backend contract in sync if the team changes it.

## Planned backend pieces

- Clean and de-identify source material, split it into chunks, label sources, and build a local ChromaDB index.
- Implement fixed-topic checks, retrieval, and a confidence decision. A missing or poor evidence match should not produce a confident answer.
- Integrate a local Ollama model for grounded answers and short conversation context.
- Implement the three FastAPI routes above, with browser access for local frontend testing.
- Generate a copyable support email draft, asking at most one or two clarifying questions when essential details are missing.
- Connect the existing Hawk widget to the API and test ordinary answers, follow-ups, and all escalation triggers end to end.

## Current repository state

The Hawk widget is a demonstration interface with hard-coded answer text and placeholder escalation behavior. The repository does not yet contain the backend described above. The existing `sandbox/` service implements a different ticket API (`/tickets` and feed routes); it does not implement `/api/chat`, `/api/escalate`, retrieval, Ollama integration, or email drafting. Do not wire it into Hawk as a substitute for the agreed backend contract.

The next useful implementation milestone is a small backend skeleton with the three agreed routes and deterministic test responses, followed by replacing the widget's hard-coded lookup and handoff functions with those calls. Retrieval, model generation, and source review can then be connected behind the same contract.
