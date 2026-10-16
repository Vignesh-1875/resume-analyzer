
import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

client = MongoClient(
    os.getenv("MONGODB_URI"),
    serverSelectionTimeoutMS=15000
)

db = client[os.getenv("MONGODB_DB", "resume_analyzer")]

users_collection = db["users"]
resume_analyses_collection = db["resume_analyses"]
job_matches_collection = db["job_matches"]
interview_sessions_collection = db["interview_sessions"]


def save_resume_analysis(user_id, filename, analysis):
    document = {
        "user_id": str(user_id),
        "filename": filename,
        "analysis": analysis,
        "created_at": datetime.now(timezone.utc)
    }

    result = resume_analyses_collection.insert_one(document)
    return str(result.inserted_id)


def get_resume_history(user_id):
    return list(
        resume_analyses_collection.find(
            {"user_id": str(user_id)},
            {"_id": 0}
        ).sort("created_at", -1)
    )
