from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AuthorKind(str, Enum):
    student = "student"
    pipeline = "pipeline"
    human = "human"


class ConfidenceLevel(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


class ActionDecisionType(str, Enum):
    auto_reply = "auto_reply"
    draft_for_review = "draft_for_review"
    request_information = "request_information"
    escalate = "escalate"
    no_action = "no_action"


class TicketStatus(str, Enum):
    new = "New"
    in_process = "In Process"
    resolved = "Resolved"


STATUS_IDS = {
    TicketStatus.new: 1,
    TicketStatus.in_process: 2,
    TicketStatus.resolved: 3,
}


class FeedEntry(StrictModel):
    ID: int
    Body: str
    IsPrivate: bool = False
    IsRichHtml: bool = False
    CreatedUid: str
    CreatedFullName: str
    AuthorType: AuthorKind
    CreatedDate: datetime


class FeedEntryCreate(StrictModel):
    Body: str = Field(min_length=1, max_length=20_000)
    IsPrivate: bool = False
    IsRichHtml: bool = False
    CreatedUid: str = Field(min_length=1, max_length=200)
    CreatedFullName: str = Field(min_length=1, max_length=200)
    AuthorType: AuthorKind

    @field_validator("Body", "CreatedUid", "CreatedFullName")
    @classmethod
    def reject_blank_strings(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be blank")
        return value


class Ticket(StrictModel):
    ID: int
    Title: str
    Description: str
    StatusID: int
    StatusName: TicketStatus
    TypeID: int
    TypeName: str
    RequestorEmail: str
    RequestorUid: str
    ContactFullName: str
    CreatedDate: datetime
    ModifiedDate: datetime
    ConfidenceTier: ConfidenceLevel | None = None
    ActionDecision: ActionDecisionType | None = None
    DecisionReason: str | None = None
    AssignedTo: str | None = None
    Feed: list[FeedEntry] = Field(default_factory=list)


class TicketCreate(StrictModel):
    Title: str = Field(min_length=1, max_length=500)
    Description: str = Field(min_length=1, max_length=20_000)
    TypeID: int = 1
    TypeName: str = Field(default="General", min_length=1, max_length=200)
    RequestorEmail: str = Field(min_length=3, max_length=320)
    RequestorUid: str = Field(min_length=1, max_length=200)
    ContactFullName: str = Field(min_length=1, max_length=200)

    @field_validator(
        "Title",
        "Description",
        "TypeName",
        "RequestorEmail",
        "RequestorUid",
        "ContactFullName",
    )
    @classmethod
    def reject_blank_strings(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be blank")
        return value


class TicketUpdate(StrictModel):
    StatusName: TicketStatus | None = None
    ConfidenceTier: ConfidenceLevel | None = None
    ActionDecision: ActionDecisionType | None = None
    DecisionReason: str | None = Field(default=None, max_length=2_000)
    AssignedTo: str | None = Field(default=None, max_length=200)


class WebhookEvent(StrictModel):
    eventType: str
    ticketId: int
    author: AuthorKind


class EventDelivery(StrictModel):
    sequence: int
    event: WebhookEvent
    attemptedAt: datetime
    destination: str | None
    delivered: bool
    statusCode: int | None = None
    error: str | None = None


class ResetResult(StrictModel):
    ticketsLoaded: int


class HealthResult(StrictModel):
    status: str = "ok"
