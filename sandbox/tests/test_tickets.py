from __future__ import annotations


def test_health_and_seed_are_available(app_context):
    client, _, _ = app_context
    assert client.get("/health").json() == {"status": "ok"}
    tickets = client.get("/tickets").json()
    assert [ticket["ID"] for ticket in tickets] == [1000]


def test_create_ticket_assigns_id_and_emits_event(app_context, ticket_request):
    client, sender, _ = app_context
    response = client.post("/tickets", json=ticket_request)
    assert response.status_code == 201
    ticket = response.json()
    assert ticket["ID"] == 1001
    assert ticket["StatusName"] == "New"
    assert ticket["Feed"] == []
    assert sender.events[0].model_dump(mode="json") == {
        "eventType": "TicketCreated",
        "ticketId": 1001,
        "author": "student",
    }


def test_create_rejects_blank_required_text(app_context, ticket_request):
    client, _, _ = app_context
    ticket_request["Title"] = "   "
    response = client.post("/tickets", json=ticket_request)
    assert response.status_code == 422


def test_get_unknown_ticket_returns_404(app_context):
    client, _, _ = app_context
    response = client.get("/tickets/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket 999999 was not found"


def test_patch_updates_status_and_decision_fields(app_context):
    client, _, _ = app_context
    response = client.patch(
        "/tickets/1000",
        json={
            "StatusName": "In Process",
            "ConfidenceTier": "medium",
            "ActionDecision": "draft_for_review",
            "DecisionReason": "A technician must verify the draft.",
            "AssignedTo": "OTS review queue",
        },
    )
    assert response.status_code == 200
    ticket = response.json()
    assert ticket["StatusID"] == 2
    assert ticket["ConfidenceTier"] == "medium"
    assert ticket["ActionDecision"] == "draft_for_review"
    assert ticket["AssignedTo"] == "OTS review queue"
