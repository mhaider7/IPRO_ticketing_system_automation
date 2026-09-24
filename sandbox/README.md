# TDX Mock Sandbox

This service is an earlier mock TeamDynamix (TDX) ticketing experiment. It is intentionally local, uses fictional test data, and does not require access to the university's live ticketing system. The team's agreed Hawk backend version uses a chat and copyable email-draft flow; it does not depend on this ticket API. See [`../HAWK_BACKEND_PLAN.md`](../HAWK_BACKEND_PLAN.md) for the current plan.

## Current capabilities

- Create, retrieve, list, and update tickets.
- Append student, pipeline, or human feed entries.
- Persist tickets to a JSON file using atomic replacement writes.
- Reset the store to a deterministic seed file.
- Emit `TicketCreated` and `FeedEntryAdded` webhook events.
- Record successful, failed, and unconfigured webhook deliveries.
- Expose interactive OpenAPI documentation through FastAPI.

The service does not include authentication or communicate with any real Illinois Tech system. All included identities use the reserved `.test` domain.

The connected Hawk demo now uses the separate [`../ots-chatbot-backend/`](../ots-chatbot-backend/README.md) API. It uses labeled test responses and is not connected to this ticket service. The original `.dc.html` widget remains a design reference.

## Setup

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".\sandbox[test]"
Copy-Item ".\sandbox\.env.example" ".\.env"
```

Set `PIPELINE_WEBHOOK_URL` only when a receiver is running. An unset webhook URL is safe: ticket operations still succeed and the undelivered event is recorded in `sandbox/data/events.json`.

Start the server:

```powershell
python -m uvicorn sandbox.app.main:app --reload --port 8000 --env-file .env
```

Open the API documentation at <http://127.0.0.1:8000/docs>.

If you do not create `.env`, the service uses `sandbox/data` and records webhook events as undelivered until a pipeline URL is configured.

Run tests:

```powershell
python -m pytest sandbox/tests
```

## Ticket lifecycle

1. A client creates a ticket through `POST /tickets`.
2. The sandbox saves the ticket, then emits `TicketCreated`.
3. The pipeline receives the event and fetches `GET /tickets/{id}`.
4. The pipeline records confidence and its action through `PATCH /tickets/{id}`.
5. An approved response is added through `POST /tickets/{id}/feed`.
6. The sandbox emits `FeedEntryAdded`, including the entry's author type.
7. The pipeline ignores events whose author is `pipeline`, preventing self-reply loops.

## Relationship to Hawk

These routes remain available for sandbox experimentation and tests. They are not the Hawk backend routes specified in the team's guide. This service neither generates grounded chat answers nor drafts support emails. The current Hawk milestone is described in [`../HAWK_BACKEND_PLAN.md`](../HAWK_BACKEND_PLAN.md).

## API summary

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Confirm that the sandbox is running |
| `GET` | `/tickets` | List all tickets |
| `POST` | `/tickets` | Create a new ticket |
| `GET` | `/tickets/{id}` | Retrieve a complete ticket and feed |
| `PATCH` | `/tickets/{id}` | Update status, confidence, action, or assignment |
| `POST` | `/tickets/{id}/feed` | Append a feed entry |
| `POST` | `/reset` | Restore the seed state and clear the event log |

## Example request

```powershell
$ticket = @{
  Title = "Cannot connect to eduroam"
  Description = "My laptop keeps asking for my password."
  TypeID = 10
  TypeName = "Network"
  RequestorEmail = "student@example.test"
  RequestorUid = "student-001"
  ContactFullName = "Test Student"
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/tickets" `
  -ContentType "application/json" `
  -Body $ticket
```

## Sandbox-only fields

The sandbox adds `AuthorType`, `ConfidenceTier`, `ActionDecision`, `DecisionReason`, and `AssignedTo` to support deterministic testing. A future TDX adapter may map these values to real TDX identities, custom attributes, private notes, or workflow state.

## Safety boundaries

- Never add real student records to the seed files.
- Do not store passwords, MFA codes, recovery contacts, or real A-numbers.
- Treat the sandbox as development infrastructure, not as a production service.
- Do not expose it publicly without authentication, authorization, and a security review.
