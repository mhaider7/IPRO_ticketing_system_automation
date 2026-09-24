# Hawk backend plan

This is a repository summary of the team's agreed `OTS_Chatbot_Backend_Guide.pdf`. The PDF is the source for the full six-part assignment and detailed acceptance criteria. The final section records which integration milestone is currently implemented.

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

The first connected demo is implemented in [`ots-chatbot-backend/`](ots-chatbot-backend/README.md) and `IIT_Chatbot_UI_Design/index.html`. It provides all three agreed routes, browser conversation history, test escalation routing, one optional clarification, and an editable/copyable email draft. The browser calls the API for replies and drafts; it does not contain a knowledge base. The original `.dc.html` design reference is preserved separately.

The service uses explicitly labeled deterministic replies and a test email template. Verified source ingestion, ChromaDB retrieval, Ollama generation, real confidence checks, and model-generated email summaries are not implemented yet. These are the next backend integration steps behind the existing contract.

The existing `sandbox/` service remains a separate ticket experiment. It is not part of the running Hawk demo.
