from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from ..repositories.message_repository import MessageRepository
from ..repositories.session_repository import SessionRepository


class Memory(ABC):
    @abstractmethod
    def load(self, session_id: str) -> List[Dict[str, Any]]:
        ...

    @abstractmethod
    def save(self, session_id: str, message: Dict[str, Any]) -> None:
        ...

    @abstractmethod
    def summarize(self, session_id: str) -> str:
        ...

    @abstractmethod
    def clear(self, session_id: str) -> None:
        ...


class PostgresMemory(Memory):
    def __init__(self, session_repo: SessionRepository, message_repo: MessageRepository) -> None:
        self.session_repo = session_repo
        self.message_repo = message_repo

    def load(self, session_id: str) -> List[Dict[str, Any]]:
        messages = self.message_repo.list_by_session(session_id)
        return [
            {
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at.isoformat(),
                "metadata": message.metadata,
            }
            for message in messages
        ]

    def save(self, session_id: str, message: Dict[str, Any]) -> None:
        self.message_repo.create(
            session_id=session_id,
            role=message["role"],
            content=message["content"],
            metadata=message.get("metadata", {}),
        )

    def summarize(self, session_id: str) -> str:
        session = self.session_repo.get(session_id)
        return session.summary if session is not None else ""

    def clear(self, session_id: str) -> None:
        self.message_repo.delete_by_session(session_id)
        session = self.session_repo.get(session_id)
        if session is not None:
            self.session_repo.delete(session_id)
