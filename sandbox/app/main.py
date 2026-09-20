from __future__ import annotations

from fastapi import FastAPI, HTTPException, status

from .models import (
    AuthorKind,
    FeedEntry,
    FeedEntryCreate,
    HealthResult,
    ResetResult,
    Ticket,
    TicketCreate,
    TicketUpdate,
    WebhookEvent,
)
from .settings import Settings
from .store import JsonStore, TicketNotFoundError
from .webhooks import WebhookClient, WebhookSender


def create_app(
    settings: Settings | None = None,
    webhook_sender: WebhookSender | None = None,
) -> FastAPI:
    settings = settings or Settings.from_env()
    store = JsonStore(settings.data_dir, settings.seed_file)
    webhook_sender = webhook_sender or WebhookClient(
        store,
        settings.webhook_url,
        settings.webhook_timeout_seconds,
    )

    app = FastAPI(
        title="TDX Mock Sandbox",
        version="0.1.0",
        description="A minimal TeamDynamix-compatible ticket lifecycle for local development.",
    )
    app.state.store = store
    app.state.webhook_sender = webhook_sender

    def not_found(ticket_id: int) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket {ticket_id} was not found",
        )

    @app.get("/health", response_model=HealthResult)
    def health() -> HealthResult:
        return HealthResult()

    @app.get("/tickets", response_model=list[Ticket])
    def list_tickets() -> list[Ticket]:
        return store.list_tickets()

    @app.get("/tickets/{ticket_id}", response_model=Ticket)
    def get_ticket(ticket_id: int) -> Ticket:
        try:
            return store.get_ticket(ticket_id)
        except TicketNotFoundError:
            raise not_found(ticket_id) from None

    @app.post("/tickets", response_model=Ticket, status_code=status.HTTP_201_CREATED)
    def create_ticket(request: TicketCreate) -> Ticket:
        ticket = store.create_ticket(request)
        webhook_sender.send(
            WebhookEvent(
                eventType="TicketCreated",
                ticketId=ticket.ID,
                author=AuthorKind.student,
            )
        )
        return ticket

    @app.patch("/tickets/{ticket_id}", response_model=Ticket)
    def update_ticket(ticket_id: int, request: TicketUpdate) -> Ticket:
        try:
            return store.update_ticket(ticket_id, request)
        except TicketNotFoundError:
            raise not_found(ticket_id) from None

    @app.post(
        "/tickets/{ticket_id}/feed",
        response_model=FeedEntry,
        status_code=status.HTTP_201_CREATED,
    )
    def add_feed_entry(ticket_id: int, request: FeedEntryCreate) -> FeedEntry:
        try:
            _, entry = store.add_feed_entry(ticket_id, request)
        except TicketNotFoundError:
            raise not_found(ticket_id) from None
        webhook_sender.send(
            WebhookEvent(
                eventType="FeedEntryAdded",
                ticketId=ticket_id,
                author=request.AuthorType,
            )
        )
        return entry

    @app.post("/reset", response_model=ResetResult)
    def reset() -> ResetResult:
        return ResetResult(ticketsLoaded=store.reset())

    return app


app = create_app()
