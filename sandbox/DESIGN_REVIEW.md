# Sandbox MVP Design Review

This file separates implemented mechanics from product-policy decisions that still need team approval.

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

## Confirmed product direction

Hawk remains the required student-facing interface in the final product. This sandbox MVP does not modify or connect the widget yet; it provides the ticket and feed API that Hawk will use.

The planned integration keeps one ticket ID per Hawk conversation, appends later student messages to that ticket's feed, displays pipeline or technician replies from the feed, and provides a technician-handoff action without deleting the ticket history.

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
- Hawk chatbot integration code (planned next phase; Hawk remains in the final product)
- Webhook retries and simulated outages
- Multi-process file locking
- Deployment or public hosting

The current implementation is intended for one local server process. If the team later runs multiple workers, replace the JSON store or add process-safe locking.
