from __future__ import annotations

from typing import Any, Dict, List

from .conversation_service import ConversationService


class ContextBuilder:
    def __init__(self, conversation_service: ConversationService, budget_tokens: int = 2048) -> None:
        self.conversation_service = conversation_service
        self.budget_tokens = budget_tokens

    def _estimate_tokens(self, text: str) -> int:
        return max(1, len(text) // 4)

    def build_context(self, session_id: str, user_message: str) -> Dict[str, Any]:
        system_message = "You are an AI assistant."
        messages = self.conversation_service.get_messages(session_id, limit=200)
        summary = self.conversation_service.get_session(session_id).summary or ""
        token_budget = self.budget_tokens

        context_messages: List[Dict[str, Any]] = [
            {"role": "system", "content": system_message}
        ]
        used_tokens = self._estimate_tokens(system_message)

        if summary:
            summary_tokens = self._estimate_tokens(summary)
            if used_tokens + summary_tokens + self._estimate_tokens(user_message) <= token_budget:
                context_messages.append({"role": "system", "content": summary})
                used_tokens += summary_tokens

        for message in reversed(messages):
            message_tokens = self._estimate_tokens(message.content)
            if used_tokens + message_tokens + self._estimate_tokens(user_message) > token_budget:
                break
            context_messages.insert(1, {"role": message.role, "content": message.content})
            used_tokens += message_tokens

        context_messages.append({"role": "user", "content": user_message})

        return {
            "context": context_messages,
            "summary": summary,
            "token_count": used_tokens + self._estimate_tokens(user_message),
            "budget": self.budget_tokens,
        }
