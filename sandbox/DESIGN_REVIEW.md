# Sandbox MVP Design Review

This document records the earlier mock TeamDynamix experiment. The team's agreed Hawk backend guide now defines a different first version: a grounded chatbot that prepares a copyable email when escalation is needed. See [`../HAWK_BACKEND_PLAN.md`](../HAWK_BACKEND_PLAN.md). The ticket API and the questions below are not prerequisites for that version.

## Implemented mechanics

- TDX-style ticket and feed objects
- JSON persistence with atomic file replacement
- Deterministic seed and reset behavior
- Ticket creation, retrieval, listing, and patching
- Student, pipeline, and human feed authors
- Minimal `TicketCreated` and `FeedEntryAdded` webhooks
- Webhook delivery log that does not block ticket persistence
- Health endpoint and generated OpenAPI documentation
- Automated tests using temporary data directories

## Sandbox-only additions

The following fields make ticket testing explicit but may need a different mapping if the team later integrates real TeamDynamix:

- `AuthorType`
- `ConfidenceTier`
- `ActionDecision`
- `DecisionReason`
- `AssignedTo`

## Decisions only for a future ticket integration

1. How should ticket status and type IDs map to real TeamDynamix configuration?
2. Where should confidence and action decisions be recorded in a real ticket?
3. What should a human handoff change in ticket assignment and status?
4. Should a pipeline-authored feed entry emit an event that the pipeline ignores?
5. What authentication, privacy, and operational controls would be needed before real data or deployment?

The current sandbox assumes one local server process. Multiple workers would need process-safe locking or a database. None of these decisions blocks the agreed Hawk chat and email-draft backend.
