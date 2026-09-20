from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from threading import RLock

from .models import (
    EventDelivery,
    FeedEntry,
    FeedEntryCreate,
    STATUS_IDS,
    Ticket,
    TicketCreate,
    TicketStatus,
    TicketUpdate,
    utc_now,
)


class TicketNotFoundError(KeyError):
    pass


class JsonStore:
    """Thread-safe JSON persistence with atomic replacement writes."""

    def __init__(self, data_dir: Path, seed_file: Path):
        self.data_dir = data_dir
        self.seed_file = seed_file
        self.tickets_file = data_dir / "tickets.json"
        self.events_file = data_dir / "events.json"
        self._lock = RLock()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if not self.tickets_file.exists():
            self.reset()
        if not self.events_file.exists():
            self._write_json(self.events_file, [])

    def _read_json(self, path: Path, default: object) -> object:
        if not path.exists():
            return default
        with path.open("r", encoding="utf-8") as stream:
            return json.load(stream)

    def _write_json(self, path: Path, value: object) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        handle, temp_name = tempfile.mkstemp(
            prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
        )
        try:
            with os.fdopen(handle, "w", encoding="utf-8") as stream:
                json.dump(value, stream, indent=2, ensure_ascii=False)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_name, path)
        except Exception:
            try:
                os.unlink(temp_name)
            except FileNotFoundError:
                pass
            raise

    def _load_tickets(self) -> list[Ticket]:
        raw = self._read_json(self.tickets_file, [])
        return [Ticket.model_validate(item) for item in raw]

    def _save_tickets(self, tickets: list[Ticket]) -> None:
        self._write_json(
            self.tickets_file,
            [ticket.model_dump(mode="json") for ticket in tickets],
        )

    def list_tickets(self) -> list[Ticket]:
        with self._lock:
            return self._load_tickets()

    def get_ticket(self, ticket_id: int) -> Ticket:
        with self._lock:
            for ticket in self._load_tickets():
                if ticket.ID == ticket_id:
                    return ticket
        raise TicketNotFoundError(ticket_id)

    def create_ticket(self, request: TicketCreate) -> Ticket:
        with self._lock:
            tickets = self._load_tickets()
            ticket_id = max((ticket.ID for ticket in tickets), default=999) + 1
            now = utc_now()
            ticket = Ticket(
                ID=ticket_id,
                Title=request.Title.strip(),
                Description=request.Description.strip(),
                StatusID=STATUS_IDS[TicketStatus.new],
                StatusName=TicketStatus.new,
                TypeID=request.TypeID,
                TypeName=request.TypeName.strip(),
                RequestorEmail=request.RequestorEmail.strip(),
                RequestorUid=request.RequestorUid.strip(),
                ContactFullName=request.ContactFullName.strip(),
                CreatedDate=now,
                ModifiedDate=now,
            )
            tickets.append(ticket)
            self._save_tickets(tickets)
            return ticket

    def update_ticket(self, ticket_id: int, request: TicketUpdate) -> Ticket:
        with self._lock:
            tickets = self._load_tickets()
            for index, ticket in enumerate(tickets):
                if ticket.ID != ticket_id:
                    continue
                changes = request.model_dump(exclude_unset=True)
                if "StatusName" in changes:
                    changes["StatusID"] = STATUS_IDS[changes["StatusName"]]
                changes["ModifiedDate"] = utc_now()
                updated = ticket.model_copy(update=changes)
                tickets[index] = updated
                self._save_tickets(tickets)
                return updated
        raise TicketNotFoundError(ticket_id)

    def add_feed_entry(self, ticket_id: int, request: FeedEntryCreate) -> tuple[Ticket, FeedEntry]:
        with self._lock:
            tickets = self._load_tickets()
            next_feed_id = max(
                (entry.ID for ticket in tickets for entry in ticket.Feed),
                default=499,
            ) + 1
            for index, ticket in enumerate(tickets):
                if ticket.ID != ticket_id:
                    continue
                now = utc_now()
                entry = FeedEntry(
                    ID=next_feed_id,
                    Body=request.Body.strip(),
                    IsPrivate=request.IsPrivate,
                    IsRichHtml=request.IsRichHtml,
                    CreatedUid=request.CreatedUid.strip(),
                    CreatedFullName=request.CreatedFullName.strip(),
                    AuthorType=request.AuthorType,
                    CreatedDate=now,
                )
                updated = ticket.model_copy(
                    update={
                        "Feed": [*ticket.Feed, entry],
                        "ModifiedDate": now,
                        "StatusName": TicketStatus.in_process,
                        "StatusID": STATUS_IDS[TicketStatus.in_process],
                    }
                )
                tickets[index] = updated
                self._save_tickets(tickets)
                return updated, entry
        raise TicketNotFoundError(ticket_id)

    def reset(self) -> int:
        with self._lock:
            if self.seed_file.exists():
                raw = self._read_json(self.seed_file, [])
                tickets = [Ticket.model_validate(item) for item in raw]
            else:
                tickets = []
            self._save_tickets(tickets)
            self._write_json(self.events_file, [])
            return len(tickets)

    def record_event(self, delivery: EventDelivery) -> None:
        with self._lock:
            events = self._read_json(self.events_file, [])
            events.append(delivery.model_dump(mode="json"))
            self._write_json(self.events_file, events)

    def next_event_sequence(self) -> int:
        with self._lock:
            events = self._read_json(self.events_file, [])
            return max((int(item["sequence"]) for item in events), default=0) + 1
