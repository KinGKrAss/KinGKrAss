from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from auth.deps import get_current_user
from database.models import Correspondence, DiplomaticDocument
from database.session import get_db
from schemas.diplomatia import (
    CorrespondenceCreate,
    CorrespondenceResponse,
    CorrespondenceUpdate,
    DiplomatiaSummary,
    DiplomaticDocumentCreate,
    DiplomaticDocumentResponse,
    DiplomaticDocumentUpdate,
)

router = APIRouter(prefix="/diplomatia", tags=["diplomatia"])


# ── Documents ─────────────────────────────────────────────────────────────────

@router.get("/documents", response_model=list[DiplomaticDocumentResponse])
def list_documents(
    skip: int = 0,
    limit: int = 100,
    language: str | None = None,
    document_type: str | None = None,
    archived: bool | None = None,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> list[DiplomaticDocument]:
    q = select(DiplomaticDocument)
    if language:
        q = q.where(DiplomaticDocument.language == language)
    if document_type:
        q = q.where(DiplomaticDocument.document_type == document_type)
    if archived is not None:
        q = q.where(DiplomaticDocument.is_archived == archived)
    return list(db.scalars(q.order_by(DiplomaticDocument.created_at.desc()).offset(skip).limit(limit)))


@router.post("/documents", response_model=DiplomaticDocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(
    data: DiplomaticDocumentCreate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> DiplomaticDocument:
    doc = DiplomaticDocument(**data.model_dump())
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.get("/documents/{doc_id}", response_model=DiplomaticDocumentResponse)
def get_document(
    doc_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> DiplomaticDocument:
    doc = db.get(DiplomaticDocument, doc_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return doc


@router.put("/documents/{doc_id}", response_model=DiplomaticDocumentResponse)
def update_document(
    doc_id: int,
    data: DiplomaticDocumentUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> DiplomaticDocument:
    doc = db.get(DiplomaticDocument, doc_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(doc, field, value)
    db.commit()
    db.refresh(doc)
    return doc


@router.delete("/documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    doc_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> None:
    doc = db.get(DiplomaticDocument, doc_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    db.delete(doc)
    db.commit()


@router.post("/documents/{doc_id}/archive", response_model=DiplomaticDocumentResponse)
def archive_document(
    doc_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> DiplomaticDocument:
    doc = db.get(DiplomaticDocument, doc_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    doc.is_archived = True
    db.commit()
    db.refresh(doc)
    return doc


# ── Correspondence ────────────────────────────────────────────────────────────

@router.get("/correspondence", response_model=list[CorrespondenceResponse])
def list_correspondence(
    skip: int = 0,
    limit: int = 100,
    status_filter: str | None = None,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> list[Correspondence]:
    q = select(Correspondence).order_by(Correspondence.sent_date.desc())
    if status_filter:
        q = q.where(Correspondence.status == status_filter)
    return list(db.scalars(q.offset(skip).limit(limit)))


@router.post("/correspondence", response_model=CorrespondenceResponse, status_code=status.HTTP_201_CREATED)
def create_correspondence(
    data: CorrespondenceCreate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> Correspondence:
    if data.document_id and not db.get(DiplomaticDocument, data.document_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    corr = Correspondence(**data.model_dump())
    db.add(corr)
    db.commit()
    db.refresh(corr)
    return corr


@router.put("/correspondence/{corr_id}", response_model=CorrespondenceResponse)
def update_correspondence(
    corr_id: int,
    data: CorrespondenceUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> Correspondence:
    corr = db.get(Correspondence, corr_id)
    if not corr:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Correspondence not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(corr, field, value)
    db.commit()
    db.refresh(corr)
    return corr


@router.delete("/correspondence/{corr_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_correspondence(
    corr_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> None:
    corr = db.get(Correspondence, corr_id)
    if not corr:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Correspondence not found")
    db.delete(corr)
    db.commit()


# ── Summary ───────────────────────────────────────────────────────────────────

@router.get("/summary", response_model=DiplomatiaSummary)
def get_summary(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> DiplomatiaSummary:
    total_docs = db.scalar(select(func.count()).select_from(DiplomaticDocument)) or 0
    archived = (
        db.scalar(
            select(func.count()).select_from(DiplomaticDocument).where(DiplomaticDocument.is_archived.is_(True))
        ) or 0
    )
    lang_rows = db.execute(
        select(DiplomaticDocument.language).distinct()
    ).scalars().all()
    total_corr = db.scalar(select(func.count()).select_from(Correspondence)) or 0
    pending_corr = (
        db.scalar(
            select(func.count()).select_from(Correspondence).where(Correspondence.status == "draft")
        ) or 0
    )

    return DiplomatiaSummary(
        total_documents=total_docs,
        archived_documents=archived,
        active_documents=total_docs - archived,
        languages=list(lang_rows),
        total_correspondence=total_corr,
        pending_correspondence=pending_corr,
    )
