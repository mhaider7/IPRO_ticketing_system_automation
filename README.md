# IPRO Ticketing System Automation

This IPRO project is building Hawk, a student-facing OTS support chatbot. Under the team's agreed backend guide, Hawk will answer from retrieved OTS information and use recent conversation context for follow-up questions. For topics that require a person, low-confidence answers, or an explicit request for help, it will prepare an email draft that the student can copy and send to OTS.

## Repository contents

- [`IIT_Chatbot_UI_Design/`](IIT_Chatbot_UI_Design/) contains the connected Hawk browser interface and the original design reference.
- [`ots-chatbot-backend/`](ots-chatbot-backend/README.md) contains the working API skeleton and deterministic test service. Follow its README to run the complete chat-to-email-draft demo locally.
- [`HAWK_BACKEND_PLAN.md`](HAWK_BACKEND_PLAN.md) summarizes the agreed chatbot backend scope, API contract, and next integration milestone.
- [`sandbox/`](sandbox/) contains an earlier mock TeamDynamix service and its design notes. It is separate exploratory work and is not required for the agreed chatbot version.

The agreed version does not authenticate students, collect personal student identifiers, create tickets, or send email on a student's behalf. The connected demo now supports conversation history, escalation, an editable email draft, and copying. Replies are test placeholders; real retrieval and Ollama integration remain the next backend work.
