from fastapi import APIRouter, Depends

from auth.deps import get_current_user
from database.session import Session, get_db
from services.dashboard import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db), _: str = Depends(get_current_user)) -> dict:
    return DashboardService.get_summary(db)
