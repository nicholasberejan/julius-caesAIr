"""Chat routes for the MVP API."""

from __future__ import annotations

import json

from flask import Blueprint, Response, jsonify, request, stream_with_context

from backend.services.chat_service import ChatService

chat_bp = Blueprint("chat", __name__)
chat_service = ChatService()


@chat_bp.post("/chat")
def chat():
    """Handle a single chat turn."""
    payload = request.get_json(silent=True) or {}
    message = (payload.get("message") or "").strip()
    session_id = payload.get("session_id")

    if not message:
        return jsonify({"error": "A non-empty 'message' field is required."}), 400

    response = chat_service.reply(message=message, session_id=session_id)
    return jsonify(response)


@chat_bp.post("/chat/stream")
def chat_stream():
    """Stream a single chat turn as server-sent events."""
    payload = request.get_json(silent=True) or {}
    message = (payload.get("message") or "").strip()
    session_id = payload.get("session_id")

    if not message:
        return jsonify({"error": "A non-empty 'message' field is required."}), 400

    def generate():
        for event in chat_service.stream_reply(message=message, session_id=session_id):
            yield f"data: {json.dumps(event)}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
