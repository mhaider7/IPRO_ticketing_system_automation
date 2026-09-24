from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from sandbox.app.main import create_app
from sandbox.app.models import EventDelivery, WebhookEvent, utc_now
from sandbox.app.settings import Settings


class RecordingWebhookSender:
    def __init__(self) -> None:
        self.events: list[WebhookEvent] = []

    def send(self, event: WebhookEvent) -> EventDelivery:
        self.events.append(event)
        return EventDelivery(
            sequence=len(self.events),
            event=event,
            attemptedAt=utc_now(),
            destination="memory://test",
            delivered=True,
            statusCode=200,
        )


@pytest.fixture
def seed_ticket() -> dict:
    return {
        "ID": 1000,
        "Title": "Seed ticket",
        "Description": "Known starting state",
        "StatusID": 1,
        "StatusName": "New",
        "TypeID": 1,
        "TypeName": "General",
        "RequestorEmail": "seed@example.test",
        "RequestorUid": "seed-001",
        "ContactFullName": "Seed Student",
        "CreatedDate": "2026-09-19T14:30:00Z",
        "ModifiedDate": "2026-09-19T14:30:00Z",
        "ConfidenceTier": None,
        "ActionDecision": None,
        "DecisionReason": None,
        "AssignedTo": None,
        "Feed": [],
    }


@pytest.fixture
def app_context(tmp_path: Path, seed_ticket: dict):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    seed_file = data_dir / "seed_tickets.json"
    seed_file.write_text(json.dumps([seed_ticket]), encoding="utf-8")
    sender = RecordingWebhookSender()
    settings = Settings(data_dir=data_dir, seed_file=seed_file)
    app = create_app(settings=settings, webhook_sender=sender)
    with TestClient(app) as client:
        yield client, sender, settings


@pytest.fixture
def ticket_request() -> dict:
    return {
        "Title": "Cannot access myIIT",
        "Description": "My account says it is locked.",
        "TypeID": 20,
        "TypeName": "Account",
        "RequestorEmail": "new-student@example.test",
        "RequestorUid": "student-002",
        "ContactFullName": "New Student",
    }
