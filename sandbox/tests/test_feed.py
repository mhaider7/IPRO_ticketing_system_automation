from __future__ import annotations


def feed_request(author: str = "student") -> dict:
    return {
        "Body": "I am still unable to connect.",
        "CreatedUid": f"{author}-001",
        "CreatedFullName": f"Test {author.title()}",
        "AuthorType": author,
    }


def test_feed_entry_is_persisted_and_emits_author(app_context):
    client, sender, _ = app_context
    response = client.post("/tickets/1000/feed", json=feed_request())
    assert response.status_code == 201
    entry = response.json()
    assert entry["ID"] == 500
    assert entry["AuthorType"] == "student"

    ticket = client.get("/tickets/1000").json()
    assert ticket["StatusName"] == "In Process"
    assert [item["Body"] for item in ticket["Feed"]] == [
        "I am still unable to connect."
    ]
    assert sender.events[-1].author == "student"
    assert sender.events[-1].eventType == "FeedEntryAdded"


def test_pipeline_entry_remains_identifiable(app_context):
    client, sender, _ = app_context
    response = client.post("/tickets/1000/feed", json=feed_request("pipeline"))
    assert response.status_code == 201
    assert response.json()["AuthorType"] == "pipeline"
    assert sender.events[-1].author == "pipeline"


def test_feed_entries_are_ordered_and_ids_are_unique(app_context):
    client, _, _ = app_context
    first = client.post("/tickets/1000/feed", json=feed_request()).json()
    second_payload = feed_request("human")
    second_payload["Body"] = "A technician has taken ownership."
    second = client.post("/tickets/1000/feed", json=second_payload).json()
    ticket = client.get("/tickets/1000").json()
    assert [item["ID"] for item in ticket["Feed"]] == [first["ID"], second["ID"]]
    assert first["ID"] != second["ID"]


def test_feed_for_unknown_ticket_returns_404(app_context):
    client, _, _ = app_context
    response = client.post("/tickets/999999/feed", json=feed_request())
    assert response.status_code == 404
