"""Deterministic routing fixtures, not a complete production topic classifier."""
import re

FIXED_TOPICS = (
    r"\bticket\s+(?:status|update)\b|\bstatus\s+of\s+(?:my\s+)?ticket\b",
    r"\b(?:billing|charge|fee)\s+(?:dispute|on my account)\b",
    r"\b(?:dispute|appeal)\b.*\b(?:hold|suspension|violation|charge|fee)\b",
    r"\b(?:my|individual)\s+(?:loan history|license assignment)\b",
)
HUMAN_REQUEST = r"\b(?:talk|speak|connect)\b.*\b(?:technician|human|person)\b"


def fixed_topic(latest: str, user_history: list[str]) -> bool:
    if any(re.search(pattern, latest, re.I) for pattern in FIXED_TOPICS):
        return True
    context = " ".join(user_history[-4:]).lower()
    if "duo" in context and re.search(r"(?:lost|no access|no longer|can't access).*?(?:phone|device)|(?:phone|device).*?(?:lost|broken|no longer)", latest, re.I):
        return True
    return "password" in context and "reset" in context and bool(
        re.search(r"still|didn't work|did not work|not working|won't let", latest, re.I)
    )


def topic_for(text: str) -> str | None:
    for topic, words in (
        ("Wi-Fi", ("wifi", "wi-fi", "eduroam", "wireless")),
        ("password reset", ("password", "myiit", "log in", "login")),
        ("printing", ("print", "printer", "papercut")),
        ("Duo", ("duo", "two-factor", "mfa")),
        ("VPN", ("vpn",)),
        ("software", ("software", "license", "matlab")),
        ("equipment", ("laptop", "equipment", "borrow")),
    ):
        if any(word in text.lower() for word in words):
            return topic
    return None
