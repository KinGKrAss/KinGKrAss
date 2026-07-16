import os

from sqlalchemy import select
from sqlalchemy.orm import Session

from auth.security import hash_password
from database.models import User


def ensure_default_admin(session: Session) -> None:
    admin_password = os.getenv("Z1_BOOTSTRAP_ADMIN_PASSWORD")
    if not admin_password:
        return

    user = session.scalar(select(User).where(User.username == "admin"))
    if user:
        return

    session.add(
        User(
            username="admin",
            hashed_password=hash_password(admin_password),
            role="admin",
        )
    )
    session.commit()
