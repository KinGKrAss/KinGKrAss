from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from auth.deps import get_current_user
from database.models import AuditLog, BackupRecord, User, UserPermission
from database.session import get_db
from schemas.astraea import (
    AstraeaSummary,
    AuditLogResponse,
    BackupRecordCreate,
    BackupRecordResponse,
    UserPermissionCreate,
    UserPermissionResponse,
)

router = APIRouter(prefix="/astraea", tags=["astraea"])


# ── Audit Logs ────────────────────────────────────────────────────────────────

@router.get("/audit-logs", response_model=list[AuditLogResponse])
def list_audit_logs(
    skip: int = 0,
    limit: int = 200,
    user_filter: str | None = None,
    resource_filter: str | None = None,
    action_filter: str | None = None,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> list[AuditLog]:
    q = select(AuditLog).order_by(AuditLog.timestamp.desc())
    if user_filter:
        q = q.where(AuditLog.user == user_filter)
    if resource_filter:
        q = q.where(AuditLog.resource == resource_filter)
    if action_filter:
        q = q.where(AuditLog.action == action_filter)
    return list(db.scalars(q.offset(skip).limit(limit)))


@router.post("/audit-logs", response_model=AuditLogResponse, status_code=status.HTTP_201_CREATED)
def create_audit_log_entry(
    user: str,
    action: str,
    resource: str,
    resource_id: str | None = None,
    details: str | None = None,
    ip_address: str | None = None,
    success: bool = True,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> AuditLog:
    log = AuditLog(
        user=user,
        action=action,
        resource=resource,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address,
        success=success,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


# ── Permissions ───────────────────────────────────────────────────────────────

@router.get("/permissions", response_model=list[UserPermissionResponse])
def list_permissions(
    user_id: int | None = None,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> list[UserPermission]:
    q = select(UserPermission)
    if user_id is not None:
        q = q.where(UserPermission.user_id == user_id)
    return list(db.scalars(q))


@router.post("/permissions", response_model=UserPermissionResponse, status_code=status.HTTP_201_CREATED)
def create_permission(
    data: UserPermissionCreate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> UserPermission:
    if not db.get(User, data.user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    perm = UserPermission(**data.model_dump())
    db.add(perm)
    db.commit()
    db.refresh(perm)
    return perm


@router.delete("/permissions/{perm_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_permission(
    perm_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> None:
    perm = db.get(UserPermission, perm_id)
    if not perm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
    db.delete(perm)
    db.commit()


# ── Backups ───────────────────────────────────────────────────────────────────

@router.get("/backups", response_model=list[BackupRecordResponse])
def list_backups(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> list[BackupRecord]:
    return list(db.scalars(select(BackupRecord).order_by(BackupRecord.created_at.desc())))


@router.post("/backups", response_model=BackupRecordResponse, status_code=status.HTTP_201_CREATED)
def trigger_backup(
    data: BackupRecordCreate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> BackupRecord:
    record = BackupRecord(filename=data.filename, status="pending")
    db.add(record)
    db.commit()
    db.refresh(record)
    # Mark completed immediately (in production: hand off to background task)
    record.status = "completed"
    record.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(record)
    return record


@router.get("/backups/{backup_id}", response_model=BackupRecordResponse)
def get_backup(
    backup_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> BackupRecord:
    backup = db.get(BackupRecord, backup_id)
    if not backup:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Backup not found")
    return backup


# ── Summary ───────────────────────────────────────────────────────────────────

@router.get("/summary", response_model=AstraeaSummary)
def get_summary(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> AstraeaSummary:
    total_logs = db.scalar(select(func.count()).select_from(AuditLog)) or 0
    failed = (
        db.scalar(select(func.count()).select_from(AuditLog).where(AuditLog.success.is_(False))) or 0
    )
    active_perms = (
        db.scalar(
            select(func.count()).select_from(UserPermission).where(UserPermission.granted.is_(True))
        ) or 0
    )
    total_backups = db.scalar(select(func.count()).select_from(BackupRecord)) or 0
    last_backup = db.scalar(
        select(BackupRecord.completed_at)
        .where(BackupRecord.status == "completed")
        .order_by(BackupRecord.completed_at.desc())
        .limit(1)
    )

    return AstraeaSummary(
        total_audit_entries=total_logs,
        failed_actions=failed,
        active_permissions=active_perms,
        total_backups=total_backups,
        last_backup_at=last_backup,
    )
