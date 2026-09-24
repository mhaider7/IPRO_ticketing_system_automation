# IPRO Ticketing System Automation

This IPRO project is building Hawk, a student-facing OTS support chatbot. Under the team's agreed backend guide, Hawk will answer from retrieved OTS information and use recent conversation context for follow-up questions. For topics that require a person, low-confidence answers, or an explicit request for help, it will prepare an email draft that the student can copy and send to OTS.

## Repository contents

- [`IIT_Chatbot_UI_Design/`](IIT_Chatbot_UI_Design/) contains an early Hawk support-widget prototype. Its current answers are hard-coded demonstration content, not a connected or approved support knowledge base.
- [`HAWK_BACKEND_PLAN.md`](HAWK_BACKEND_PLAN.md) summarizes the agreed chatbot backend scope, API contract, and next integration milestone.
- [`sandbox/`](sandbox/) contains an earlier mock TeamDynamix service and its design notes. It is separate exploratory work and is not required for the agreed chatbot version.

The agreed version does not authenticate students, collect personal student identifiers, create tickets, or send email on a student's behalf. The current widget is not connected to a chatbot backend yet.
