from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class DiplomaticDocumentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=256)
    language: str = Field(..., min_length=2, max_length=8)
    document_type: str = Field(..., pattern="^(memo|treaty|letter|report|note|directive)$")
    content: str = Field(..., min_length=1)
    tags: str | None = Field(None, max_length=256)
    is_archived: bool = False


class DiplomaticDocumentCreate(DiplomaticDocumentBase):
    pass


class DiplomaticDocumentUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=256)
    language: str | None = Field(None, min_length=2, max_length=8)
    document_type: str | None = Field(None, pattern="^(memo|treaty|letter|report|note|directive)$")
    content: str | None = Field(None, min_length=1)
    tags: str | None = Field(None, max_length=256)
    is_archived: bool | None = None


class DiplomaticDocumentResponse(DiplomaticDocumentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------

class CorrespondenceBase(BaseModel):
    subject: str = Field(..., min_length=1, max_length=256)
    sender: str = Field(..., min_length=1, max_length=128)
    recipient: str = Field(..., min_length=1, max_length=128)
    sent_date: date
    status: str = Field("draft", pattern="^(draft|sent|received|archived)$")
    body: str | None = None


class CorrespondenceCreate(CorrespondenceBase):
    document_id: int | None = None


class CorrespondenceUpdate(BaseModel):
    subject: str | None = Field(None, min_length=1, max_length=256)
    sender: str | None = Field(None, min_length=1, max_length=128)
    recipient: str | None = Field(None, min_length=1, max_length=128)
    sent_date: date | None = None
    status: str | None = Field(None, pattern="^(draft|sent|received|archived)$")
    body: str | None = None
    document_id: int | None = None


class CorrespondenceResponse(CorrespondenceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    document_id: int | None


# ---------------------------------------------------------------------------

class DiplomatiaSummary(BaseModel):
    total_documents: int
    archived_documents: int
    active_documents: int
    languages: list[str]
    total_correspondence: int
    pending_correspondence: int
