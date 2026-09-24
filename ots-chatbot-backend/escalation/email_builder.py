"""A test template that preserves the student's words without inventing facts."""
import re

from api.schemas import Conversation, EmailDraft, EscalationResponse
from escalation.topics import topic_for

CLARIFY_ISSUE = "What problem would you like OTS to help with? Use fictional details for this demo; do not include personal identifiers or passwords."
CLARIFY_DETAIL = "What device or error message is involved? You can say 'skip' if you do not know. Please leave out personal identifiers and passwords."
QUESTIONS = {CLARIFY_ISSUE, CLARIFY_DETAIL}


def redact_identifiers(text: str) -> str:
    # Defense in depth for common accidental identifiers; not a general PII detector.
    text = re.sub(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", "[email omitted]", text)
    text = re.sub(r"\b[Aa]\d{8}\b", "[student ID omitted]", text)
    text = re.sub(r"(?i)\b(student\s*id|password|verification code|mfa code)\s*(?:is|:|=)\s*\S+", r"\1 [omitted]", text)
    return text


def build_test_email(conversation: Conversation) -> EscalationResponse:
    users = [message.text for message in conversation.messages if message.role == "user"]
    asked = any(message.role == "bot" and message.text in QUESTIONS for message in conversation.messages)
    if not asked and not users:
        return EscalationResponse(clarifying_question=CLARIFY_ISSUE)
    if not asked and len(users) == 1 and len(users[0].split()) < 8:
        return EscalationResponse(clarifying_question=CLARIFY_DETAIL)
    details = [redact_identifiers(text) for text in users if text.lower().strip() != "skip"]
    topic = next((topic_for(text) for text in reversed(users) if topic_for(text)), "IT assistance")
    summary = "\n".join(f"- {text}" for text in details) or "[Describe the issue before sending.]"
    return EscalationResponse(email=EmailDraft(
        to="supportdesk@illinoistech.edu",
        subject=f"OTS Support Request: {topic}",
        body=("Hello OTS Support Desk,\n\nI would appreciate help with the following issue. "
              "These are the details I shared:\n\n" + summary +
              "\n\nCould you advise me on the next steps?\n\nThank you."),
    ))
