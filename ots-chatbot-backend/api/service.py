"""Swap DemoService for the real retrieval/LLM coordinator at create_app()."""
import re
from typing import Protocol

from api.schemas import ChatRequest, ChatResponse, Conversation, EscalationResponse
from escalation.email_builder import build_test_email
from escalation.topics import HUMAN_REQUEST, fixed_topic, topic_for


class ChatService(Protocol):
    def chat(self, request: ChatRequest) -> ChatResponse: ...
    def escalate(self, request: Conversation) -> EscalationResponse: ...


class DemoService:
    def chat(self, request: ChatRequest) -> ChatResponse:
        users = [message.text for message in request.messages if message.role == "user"]
        latest = users[-1]
        reason = None
        if re.search(HUMAN_REQUEST, latest, re.I):
            reason = "user_request"
        elif fixed_topic(latest, users):
            reason = "fixed_topic"
        if reason:
            return ChatResponse(reply="I can help prepare an email for OTS. You will review and send it yourself.", escalate=True, escalation_reason=reason)
        topic = topic_for(latest)
        if not topic and re.search(r"\b(that|it|still|same|phone|tried)\b", latest, re.I):
            topic = next((topic_for(text) for text in reversed(users[:-1]) if topic_for(text)), None)
        if not topic:
            return ChatResponse(reply="Test response: no matching demo topic. Let's prepare an email for OTS.", escalate=True, escalation_reason="low_confidence")
        return ChatResponse(reply=f"Test response: I am following your question about {topic}. Verified OTS guidance will appear here when retrieval and Ollama are connected. You can continue the conversation or choose Talk to a technician to draft an email.")

    def escalate(self, request: Conversation) -> EscalationResponse:
        return build_test_email(request)
