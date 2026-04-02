"""Chat routes for the MVP API."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

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
