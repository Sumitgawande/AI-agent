from __future__ import annotations

from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database.models import Session as SessionModel


class SessionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        metadata: Dict[str, Any] | None = None,
        user_id: int | None = None,
        session_id: str | None = None,
    ) -> SessionModel:
        session = SessionModel(id=session_id, metadata_json=metadata or {}, user_id=user_id)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get(self, session_id: str) -> Optional[SessionModel]:
        return self.db.get(SessionModel, session_id)

    def list(self, limit: int = 100, offset: int = 0) -> List[SessionModel]:
        return self.db.execute(select(SessionModel).offset(offset).limit(limit)).scalars().all()

    def update(self, session_id: str, metadata: Dict[str, Any]) -> Optional[SessionModel]:
        session = self.get(session_id)
        if session is None:
            return None
        session.metadata_json = metadata
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def delete(self, session_id: str) -> None:
        session = self.get(session_id)
        if session is None:
            return
        self.db.delete(session)
        self.db.commit()
