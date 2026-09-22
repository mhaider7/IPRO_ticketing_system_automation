# IPRO Ticketing System Automation

This IPRO project is currently prioritizing Hawk, a student-facing OTS support chatbot. The intended experience lets a student describe an issue, continue a conversation, receive guidance when the team-approved response policy permits it, and reach a human technician when needed. Ticket handling and evidence-grounded automation support that experience.

## Repository contents

- [`IIT_Chatbot_UI_Design/`](IIT_Chatbot_UI_Design/) contains an early Hawk support-widget prototype. Its current answers are hard-coded demonstration content, not a connected or approved support knowledge base.
- [`sandbox/`](sandbox/) contains a mock TeamDynamix service, design review, and architecture document for testing Hawk's ticket and conversation flow.

The next integration milestone is a local Hawk conversation that creates one ticket, appends follow-up messages to that ticket, displays a test pipeline or technician reply, and requests a technician handoff. The mock sandbox makes that flow testable without live student information or real TeamDynamix access. The widget is not connected to the sandbox yet. See [`sandbox/README.md`](sandbox/README.md) for setup and [`sandbox/DESIGN_REVIEW.md`](sandbox/DESIGN_REVIEW.md) for the proposed sequence and open decisions.
