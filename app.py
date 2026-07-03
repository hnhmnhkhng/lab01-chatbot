import os

from anthropic import Anthropic
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, render_template, request, stream_with_context

import db

load_dotenv()

app = Flask(__name__)
anthropic_client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

AVAILABLE_MODELS = {"claude-haiku-4-5", "claude-sonnet-5"}
DEFAULT_MODEL = "claude-haiku-4-5"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/conversations", methods=["GET"])
def api_list_conversations():
    return jsonify(db.list_conversations())


@app.route("/api/conversations", methods=["POST"])
def api_create_conversation():
    conversation_id = db.create_conversation()
    return jsonify({"id": conversation_id})


@app.route("/api/conversations/<conversation_id>", methods=["GET"])
def api_get_conversation(conversation_id):
    conversation = db.get_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(conversation)


@app.route("/api/conversations/<conversation_id>", methods=["DELETE"])
def api_delete_conversation(conversation_id):
    db.delete_conversation(conversation_id)
    return jsonify({"ok": True})


@app.route("/api/conversations/<conversation_id>/model", methods=["POST"])
def api_set_model(conversation_id):
    model = request.json.get("model")
    if model not in AVAILABLE_MODELS:
        return jsonify({"error": "invalid model"}), 400
    db.set_model(conversation_id, model)
    return jsonify({"ok": True})


@app.route("/api/conversations/<conversation_id>/chat", methods=["POST"])
def api_chat(conversation_id):
    user_message = request.json["message"]

    conversation = db.get_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": "not found"}), 404

    is_first_message = len(conversation["messages"]) == 0
    db.add_message(conversation_id, "user", user_message)
    if is_first_message:
        db.set_title_if_new(conversation_id, user_message)

    history = conversation["messages"] + [{"role": "user", "content": user_message}]

    def generate():
        full_response = ""
        with anthropic_client.messages.stream(
            model=conversation.get("model", DEFAULT_MODEL),
            max_tokens=4096,
            messages=history,
        ) as stream:
            for text in stream.text_stream:
                full_response += text
                yield text
        db.add_message(conversation_id, "assistant", full_response)

    return Response(stream_with_context(generate()), mimetype="text/plain")


if __name__ == "__main__":
    app.run(debug=True)
