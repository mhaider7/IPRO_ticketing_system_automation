from __future__ import annotations

import json

from fastapi.testclient import TestClient

from sandbox.app.main import create_app
from sandbox.app.settings import Settings


def test_unconfigured_webhook_is_recorded_without_failing_ticket(
    tmp_path, seed_ticket, ticket_request
):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    seed_file = data_dir / "seed_tickets.json"
    seed_file.write_text(json.dumps([seed_ticket]), encoding="utf-8")
    settings = Settings(data_dir=data_dir, seed_file=seed_file, webhook_url=None)
    app = create_app(settings=settings)

    with TestClient(app) as client:
        response = client.post("/tickets", json=ticket_request)
        assert response.status_code == 201

    events = json.loads((data_dir / "events.json").read_text(encoding="utf-8"))
    assert len(events) == 1
    assert events[0]["delivered"] is False
    assert events[0]["event"]["eventType"] == "TicketCreated"
    assert "not configured" in events[0]["error"]
