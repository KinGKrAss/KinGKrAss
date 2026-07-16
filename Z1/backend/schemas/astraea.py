from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime
    user: str
    action: str
    resource: str
    resource_id: str | None
    details: str | None
    ip_address: str | None
    success: bool


# ---------------------------------------------------------------------------

class UserPermissionCreate(BaseModel):
    user_id: int
    resource: str = Field(..., min_length=1, max_length=64)
    action: str = Field(..., pattern="^(read|write|admin)$")
    granted: bool = True


class UserPermissionResponse(UserPermissionCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


# ---------------------------------------------------------------------------

class BackupRecordCreate(BaseModel):
    filename: str = Field(..., min_length=1, max_length=256)


class BackupRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    size_bytes: int | None
    status: str
    created_at: datetime
    completed_at: datetime | None


# ---------------------------------------------------------------------------

class AstraeaSummary(BaseModel):
    total_audit_entries: int
    failed_actions: int
    active_permissions: int
    total_backups: int
    last_backup_at: datetime | None
