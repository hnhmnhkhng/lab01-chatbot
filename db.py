import os
from datetime import datetime, timezone

from bson import ObjectId
from pymongo import MongoClient

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")

client = MongoClient(MONGO_URI)
db = client["chatbot_db"]
conversations = db["conversations"]


def create_conversation():
    now = datetime.now(timezone.utc)
    result = conversations.insert_one(
        {
            "title": "New chat",
            "model": "claude-haiku-4-5",
            "created_at": now,
            "updated_at": now,
            "messages": [],
        }
    )
    return str(result.inserted_id)


def list_conversations():
    docs = conversations.find({}, {"title": 1, "updated_at": 1}).sort("updated_at", -1)
    return [
        {"id": str(d["_id"]), "title": d["title"], "updated_at": d["updated_at"].isoformat()}
        for d in docs
    ]


def get_conversation(conversation_id):
    doc = conversations.find_one({"_id": ObjectId(conversation_id)})
    if not doc:
        return None
    return {
        "id": str(doc["_id"]),
        "title": doc["title"],
        "model": doc.get("model", "claude-haiku-4-5"),
        "messages": [
            {"role": m["role"], "content": m["content"]} for m in doc["messages"]
        ],
    }


def add_message(conversation_id, role, content):
    now = datetime.now(timezone.utc)
    update = {
        "$push": {"messages": {"role": role, "content": content, "timestamp": now}},
        "$set": {"updated_at": now},
    }
    conversations.update_one({"_id": ObjectId(conversation_id)}, update)


def set_model(conversation_id, model):
    conversations.update_one(
        {"_id": ObjectId(conversation_id)},
        {"$set": {"model": model}},
    )


def set_title_if_new(conversation_id, first_message):
    title = first_message.strip()[:50]
    conversations.update_one(
        {"_id": ObjectId(conversation_id), "title": "New chat"},
        {"$set": {"title": title}},
    )


def delete_conversation(conversation_id):
    conversations.delete_one({"_id": ObjectId(conversation_id)})
