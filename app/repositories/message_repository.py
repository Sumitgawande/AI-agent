from __future__ import annotations

from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database.models import Message as MessageModel


class MessageRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, session_id: str, role: str, content: str, metadata: Dict[str, Any] | None = None) -> MessageModel:
        message = MessageModel(session_id=session_id, role=role, content=content, metadata_json=metadata or {})
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def list_by_session(self, session_id: str, limit: int = 100, offset: int = 0) -> List[MessageModel]:
        stmt = select(MessageModel).where(MessageModel.session_id == session_id).order_by(MessageModel.created_at).offset(offset).limit(limit)
        return self.db.execute(stmt).scalars().all()

    def delete_by_session(self, session_id: str) -> None:
        messages = self.list_by_session(session_id)
        for message in messages:
            self.db.delete(message)
        self.db.commit()
