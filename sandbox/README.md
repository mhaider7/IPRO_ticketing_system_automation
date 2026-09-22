# TDX Mock Sandbox

This service reproduces the small part of TeamDynamix (TDX) needed to develop Hawk's conversation and technician-handoff flow. It is intentionally local, uses fictional test data, and does not require access to the university's live ticketing system. Hawk is the current product priority; this API supports it and is not a standalone student experience.

## Current capabilities

- Create, retrieve, list, and update tickets.
- Append student, pipeline, or human feed entries.
- Persist tickets to a JSON file using atomic replacement writes.
- Reset the store to a deterministic seed file.
- Emit `TicketCreated` and `FeedEntryAdded` webhook events.
- Record successful, failed, and unconfigured webhook deliveries.
- Expose interactive OpenAPI documentation through FastAPI.

The service does not include authentication or communicate with any real Illinois Tech system. All included identities use the reserved `.test` domain.

The existing Hawk widget is a visual prototype with hard-coded sample answers. It is not connected to this service. Do not treat its answers or cited URLs as verified support guidance.

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

## Hawk-first integration milestone

The next demo should use fictional student details and the local sandbox:

1. Hawk sends the first student issue to `POST /tickets` and keeps the returned ticket ID for that conversation.
2. Hawk sends later student messages to `POST /tickets/{id}/feed` using the same ID.
3. Hawk reads `GET /tickets/{id}` to display a test pipeline or technician reply from the feed. The display must distinguish student, pipeline, and human authors.
4. A technician-handoff action updates the ticket's assignment, status, and action decision. The exact handoff behavior still needs team approval.
5. Closing or restarting the widget changes only its visible session; it does not delete the saved ticket.

Use a clearly labeled test reply for this milestone. Connecting an evidence source or allowing automatic answers requires a team-approved response policy and verified support content.

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
