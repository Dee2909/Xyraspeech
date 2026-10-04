"""Bounded Conversation Context and Memory Manager."""

import re
import time
import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from xyraspeech.app.core.config import settings


class ConversationMessage(BaseModel):
    """A single turn in the conversation history."""
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message text")
    language: str = Field(default="en", description="Language code")
    timestamp: float = Field(default_factory=time.time)


class ConversationContext(BaseModel):
    """Stateful, bounded memory context for an ongoing conversation session."""
    conversation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    messages: List[ConversationMessage] = Field(default_factory=list)
    user_name: Optional[str] = None
    user_preferences: Dict[str, Any] = Field(default_factory=dict)
    detected_topics: List[str] = Field(default_factory=list)
    primary_language: Optional[str] = None

    def add_user_message(self, text: str, language: str = "en") -> None:
        """Appends user message and updates memory cues."""
        self.extract_memory_cues(text)
        self.messages.append(ConversationMessage(role="user", content=text, language=language))
        self._trim_history()

    def add_assistant_message(self, text: str, language: str = "en") -> None:
        """Appends assistant response."""
        self.messages.append(ConversationMessage(role="assistant", content=text, language=language))
        self._trim_history()

    def _trim_history(self) -> None:
        """Enforces bounded history length."""
        if len(self.messages) > settings.MAX_CONTEXT_MESSAGES:
            self.messages = self.messages[-settings.MAX_CONTEXT_MESSAGES:]

    def extract_memory_cues(self, text: str) -> None:
        """Extracts user profile details such as name and preferences."""
        # English patterns: "my name is Arun", "I am Arun", "call me Arun"
        en_name_match = re.search(r"\b(?:my name is|i am|call me|this is)\s+([A-Z][a-zA-Z]+)", text, re.IGNORECASE)
        if en_name_match:
            self.user_name = en_name_match.group(1).capitalize()

        # Tamil patterns: "என் பெயர் அருண்", "எனது பெயர் அருண்"
        ta_name_match = re.search(r"(?:என்|எனது)\s+பெயர்\s+([\u0B80-\u0BFFa-zA-Z]+)", text)
        if ta_name_match:
            self.user_name = ta_name_match.group(1)

    def get_context_prompt_snippet(self) -> str:
        """Builds concise context summary for the LLM system prompt."""
        parts = []
        if self.user_name:
            parts.append(f"User's name is {self.user_name}.")
        if self.detected_topics:
            parts.append(f"Recent topics discussed: {', '.join(self.detected_topics[-3:])}.")

        recent_dialogue = []
        for msg in self.messages[-6:]:
            role_label = "User" if msg.role == "user" else "Assistant"
            recent_dialogue.append(f"{role_label}: {msg.content}")

        if recent_dialogue:
            parts.append("Recent Conversation History:\n" + "\n".join(recent_dialogue))

        return "\n".join(parts)


class ContextManager:
    """Manages active conversation contexts."""

    def __init__(self):
        self._contexts: Dict[str, ConversationContext] = {}

    def get_or_create(self, conversation_id: Optional[str] = None) -> ConversationContext:
        """Retrieves existing context or creates a new one."""
        cid = conversation_id or str(uuid.uuid4())
        if cid not in self._contexts:
            self._contexts[cid] = ConversationContext(conversation_id=cid)
        return self._contexts[cid]

    def clear(self, conversation_id: str) -> None:
        """Clears memory for a given conversation."""
        if conversation_id in self._contexts:
            del self._contexts[conversation_id]


context_manager = ContextManager()
