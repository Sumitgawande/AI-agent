from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Generator

from ..database.engine import SessionLocal
from ..memory.memory import PostgresMemory
from ..repositories.message_repository import MessageRepository
from ..repositories.session_repository import SessionRepository


class ConversationService:
    def __init__(self) -> None:
        self.db = SessionLocal()
        self.session_repo = SessionRepository(self.db)
        self.message_repo = MessageRepository(self.db)
        self.memory = PostgresMemory(self.session_repo, self.message_repo)

    def create_session(
        self,
        metadata: Dict[str, Any] | None = None,
        user_id: int | None = None,
        session_id: str | None = None,
    ):
        return self.session_repo.create(metadata=metadata, user_id=user_id, session_id=session_id)

    def get_session(self, session_id: str):
        return self.session_repo.get(session_id)

    def list_sessions(self, limit: int = 100, offset: int = 0):
        return self.session_repo.list(limit=limit, offset=offset)

    def delete_session(self, session_id: str) -> None:
        self.message_repo.delete_by_session(session_id)
        self.session_repo.delete(session_id)

    def update_summary(self, session_id: str, summary: str):
        session = self.get_session(session_id)
        if session is None:
            return None
        session.summary = summary
        session.summary_updated_at = datetime.utcnow()
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def add_message(self, session_id: str, role: str, content: str, metadata: Dict[str, Any] | None = None):
        session = self.get_session(session_id)
        if session is None:
            raise ValueError("Session not found")
        session.updated_at = datetime.utcnow()
        self.db.add(session)
        self.db.commit()
        return self.message_repo.create(session_id=session_id, role=role, content=content, metadata=metadata)

    def get_messages(self, session_id: str, limit: int = 100, offset: int = 0):
        return self.message_repo.list_by_session(session_id, limit=limit, offset=offset)

    def close(self) -> None:
        self.db.close()


def get_conversation_service() -> Generator[ConversationService, None, None]:
    service = ConversationService()
    try:
        yield service
    finally:
        service.close()
