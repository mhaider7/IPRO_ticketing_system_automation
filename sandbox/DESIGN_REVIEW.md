# Sandbox MVP Design Review

This file separates implemented mechanics, the proposed Hawk-first work sequence, and product-policy decisions that still need team approval.

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

The following fields make testing explicit but may need a different mapping in real TeamDynamix:

- `AuthorType`
- `ConfidenceTier`
- `ActionDecision`
- `DecisionReason`
- `AssignedTo`

## Current working direction

The team appears to be prioritizing Hawk as the student-facing product. This sandbox MVP does not modify or connect the widget yet; it provides a ticket and feed API that Hawk can use. Confirm the priority and user flow with the full team before treating them as final product decisions.

The proposed integration keeps one ticket ID per Hawk conversation, appends later student messages to that ticket's feed, displays pipeline or technician replies from the feed, and provides a technician-handoff action without deleting the ticket history.

## Proposed next milestone: one Hawk conversation

1. Connect Hawk's first message to `POST /tickets` and retain the returned ID.
2. Append subsequent student messages through `POST /tickets/{id}/feed`.
3. Read the feed through `GET /tickets/{id}` and show a clearly labeled test reply from the pipeline or a technician.
4. Demonstrate a technician handoff on the same ticket after the team chooses the exact status, assignment, and action behavior.
5. Check that closing or restarting the widget does not erase the ticket or create duplicate tickets.

This is the next integration target, not a claim that Hawk and the sandbox are already connected. The widget currently uses hard-coded demonstration answers; they should not become production guidance without source and policy review.

## Decisions requested from the team

1. Should medium confidence create a draft for human approval, or post automatically?
2. Should any student reply after an AI response require human review?
3. Should confidence remain a ticket field, become a private feed note, or map to a TDX custom attribute?
4. Should escalation use `PATCH /tickets/{id}` or a dedicated `/escalate` action?
5. Which status and type IDs should the mock use when real TDX configuration becomes available?
6. Should the mock emit events for pipeline-authored feed entries and let the pipeline ignore them, as it does now?

## Intentionally deferred

- Authentication and authorization
- Real student or OTS data
- RAG, embedding, vector database, and LLM code
- Automatic response policy
- Additional channels such as email ingestion
- Webhook retries and simulated outages
- Multi-process file locking
- Deployment or public hosting

The current implementation is intended for one local server process. If the team later runs multiple workers, replace the JSON store or add process-safe locking.
