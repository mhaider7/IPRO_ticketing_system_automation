from __future__ import annotations

from typing import Protocol

import httpx

from .models import EventDelivery, WebhookEvent, utc_now
from .store import JsonStore


class WebhookSender(Protocol):
    def send(self, event: WebhookEvent) -> EventDelivery: ...


class WebhookClient:
    def __init__(self, store: JsonStore, destination: str | None, timeout: float):
        self.store = store
        self.destination = destination
        self.timeout = timeout

    def send(self, event: WebhookEvent) -> EventDelivery:
        sequence = self.store.next_event_sequence()
        if not self.destination:
            delivery = EventDelivery(
                sequence=sequence,
                event=event,
                attemptedAt=utc_now(),
                destination=None,
                delivered=False,
                error="PIPELINE_WEBHOOK_URL is not configured",
            )
            self.store.record_event(delivery)
            return delivery

        try:
            response = httpx.post(
                self.destination,
                json=event.model_dump(mode="json"),
                timeout=self.timeout,
            )
            delivery = EventDelivery(
                sequence=sequence,
                event=event,
                attemptedAt=utc_now(),
                destination=self.destination,
                delivered=response.is_success,
                statusCode=response.status_code,
                error=None if response.is_success else response.text[:500],
            )
        except httpx.HTTPError as exc:
            delivery = EventDelivery(
                sequence=sequence,
                event=event,
                attemptedAt=utc_now(),
                destination=self.destination,
                delivered=False,
                error=str(exc)[:500],
            )
        self.store.record_event(delivery)
        return delivery
