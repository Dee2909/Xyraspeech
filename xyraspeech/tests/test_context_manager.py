"""Unit tests for ContextManager and Memory Extraction."""

from xyraspeech.app.orchestration.context_manager import ContextManager


def test_name_extraction_english():
    mgr = ContextManager()
    ctx = mgr.get_or_create("session_1")

    ctx.add_user_message("Hello, my name is Arun and I am testing this.")
    assert ctx.user_name == "Arun"


def test_name_extraction_tamil():
    mgr = ContextManager()
    ctx = mgr.get_or_create("session_2")

    ctx.add_user_message("வணக்கம், என் பெயர் அருண்.")
    assert ctx.user_name == "அருண்"


def test_history_bounding():
    mgr = ContextManager()
    ctx = mgr.get_or_create("session_3")

    for i in range(30):
        ctx.add_user_message(f"Message {i}")
        ctx.add_assistant_message(f"Response {i}")

    # Bounded to MAX_CONTEXT_MESSAGES (20)
    assert len(ctx.messages) <= 20
