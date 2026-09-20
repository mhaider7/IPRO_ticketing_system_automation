from __future__ import annotations

from fastapi.testclient import TestClient

from sandbox.app.main import create_app
from sandbox.app.store import JsonStore


def test_ticket_survives_new_app_instance(app_context, ticket_request):
    client, sender, settings = app_context
    created = client.post("/tickets", json=ticket_request).json()

    second_app = create_app(settings=settings, webhook_sender=sender)
    with TestClient(second_app) as second_client:
        restored = second_client.get(f"/tickets/{created['ID']}")
        assert restored.status_code == 200
        assert restored.json()["Description"] == ticket_request["Description"]


def test_reset_restores_seed_and_clears_added_tickets(app_context, ticket_request):
    client, _, _ = app_context
    client.post("/tickets", json=ticket_request)
    response = client.post("/reset")
    assert response.json() == {"ticketsLoaded": 1}
    tickets = client.get("/tickets").json()
    assert [ticket["ID"] for ticket in tickets] == [1000]


def test_atomic_store_file_is_valid_json(app_context, ticket_request):
    client, _, settings = app_context
    for index in range(5):
        payload = dict(ticket_request)
        payload["Title"] = f"Ticket {index}"
        assert client.post("/tickets", json=payload).status_code == 201
    store = JsonStore(settings.data_dir, settings.seed_file)
    assert len(store.list_tickets()) == 6
