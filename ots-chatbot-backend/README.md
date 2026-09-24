# Hawk API and connected demo

This is the first integration milestone from the agreed backend guide: the three API routes and a working browser conversation through an email draft. All chat replies are explicitly labeled test responses. The email builder is a deterministic test template. ChromaDB, verified OTS source material, model confidence grading, and Ollama are not connected yet.

## Run locally

From the repository root with Python 3.11 or newer:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r ots-chatbot-backend/requirements.txt
.\.venv\Scripts\python.exe -m uvicorn api.main:app --app-dir ots-chatbot-backend --host 127.0.0.1 --port 8000
```

On macOS/Linux use `.venv/bin/python` in place of `.\.venv\Scripts\python.exe`.

Open <http://127.0.0.1:8000/> for the connected Hawk demo and <http://127.0.0.1:8000/docs> for the API. The app serves its own frontend, so no frontend build or separate web server is required. Stop any other service using port 8000 first, or select another port.

The runnable frontend is `IIT_Chatbot_UI_Design/index.html`, `hawk.css`, and `hawk.js`. It adapts the existing OTS/Hawk design into ordinary browser code. The `.dc.html` file and its `support.js` runtime are preserved as the original design reference; open the server URL above to use the connected version.

## Try the complete flow

1. Click **Ask Hawk** and send **My Wi-Fi will not connect**. The backend returns a test response with no fabricated sources.
2. Send **It still does that on my phone**. Hawk uses the conversation history to retain the topic.
3. Click **Talk to a technician**. Review the editable email body and click **Copy email**. Paste it into a text editor to inspect it; no email is sent by this demo.
4. Start a new chat and ask **What is my ticket status?** (fixed-topic fixture) or **Can you predict the weather?** (no matching demo topic). Both enter email drafting automatically.
5. Request a technician before typing an issue. Hawk asks what the problem is, then drafts the email after the answer. The test builder asks at most one clarifying question, including when the answer is **skip**.

The no-match fixture uses the contract's `low_confidence` reason to exercise that UI path; it is not a real model confidence assessment. Topic checks are example rules rather than a complete production classifier.

## API contract

Both POST routes accept `{ "messages": [{ "role": "user", "text": "My Wi-Fi fails" }] }`. Roles are `user` and `bot`; the frontend sends the full conversation. Chat requests must end with a user message. Escalation requests can be empty or end with a bot message, supporting explicit requests and automatic transitions. The frontend stays on `/api/escalate` while collecting clarification.

| Route | Response |
| --- | --- |
| `GET /api/health` | `{ "status": "ok" }` |
| `POST /api/chat` | `{ "reply": "...", "sources": [], "escalate": false, "escalation_reason": null }` |
| `POST /api/escalate` | `{ "email": { "to": "...", "subject": "...", "body": "..." }, "clarifying_question": null }` or `{ "email": null, "clarifying_question": "..." }` |

An escalating chat response uses `fixed_topic`, `low_confidence`, or `user_request` as its reason. Invalid requests return HTTP 422; unavailable dependencies return HTTP 503 with a short `detail` message. Inputs are limited to 60 messages, 4,000 characters per message, and 24,000 total characters. Error replies do not echo request content.

The default UI calls the API on its own origin. For a separate local frontend, set `HAWK_ALLOWED_ORIGINS` to comma-separated exact origins before starting the server; localhost and 127.0.0.1 on port 8000 are allowed by default. CORS is not authentication.

## Team integration points

- **Part 4:** `api/main.py` owns routes and frontend serving; `api/schemas.py` owns request/response validation.
- **Parts 2 and 3:** Replace `DemoService.chat()` via the `ChatService` interface in `api/service.py` with retrieval, grounded generation, and confidence decisions. `create_app(service=...)` accepts the replacement for integration and testing. Put real retrieval and LLM code in the guide's `retrieval/` and `llm/` directories when those parts are ready.
- **Part 5:** Replace `escalation/email_builder.py` through `ChatService.escalate()`. Preserve the exclusive email-or-question response shape. `escalation/topics.py` is the shared location for the current test rules.
- **Part 6:** `tests/test_api.py` checks contracts, routing fixtures, stateless conversations, validation, and dependency failure. `tests/browser.cjs` exercises the actual frontend and API together.

Map frontend role `bot`/field `text` to Ollama role `assistant`/field `content` inside the future model adapter. Keep the public API stable. A real model adapter must enforce its own request timeout; the browser already aborts after 15 seconds and provides retry. Real generation may require an agreed longer timeout or a streaming contract later.

## Data handling

Use fictional issues for this local demo. It has no login, personal-information fields, ticket creation, email delivery, server-side conversation storage, or browser storage. Messages are transmitted to the local backend for each call, held in memory during processing, and never logged by application code. Closing the widget retains the current page session; **New chat** or reload clears it. Draft text is copied only when the student clicks **Copy email**.

The template masks common email addresses, A-number student IDs, and explicitly labeled password/code fields if accidentally typed. This is a limited safeguard, not comprehensive personal-data detection. Use de-identified test conversations; real data and public deployment need further review.

## Verification

```powershell
.\.venv\Scripts\python.exe -m pytest ots-chatbot-backend/tests sandbox/tests -q
```

For browser checks, install Playwright in a local development environment, start the server, and run:

```powershell
npm install --no-save --package-lock=false playwright
npx playwright install chromium
node ots-chatbot-backend/tests/browser.cjs
```

If Microsoft Edge is already installed, set `$env:HAWK_BROWSER_CHANNEL='msedge'` to use it instead of downloading Chromium. `HAWK_BASE_URL` overrides the default server URL. Screenshots go into ignored `ots-chatbot-backend/.browser-output/`, or the directory set in `HAWK_SCREENSHOT_DIR`.

The browser check covers follow-up context, all three escalation triggers, clarification, copy and clipboard fallback, network/draft-service failure and retry, reset during an outstanding request, mobile widths, and clearing history on reload.
