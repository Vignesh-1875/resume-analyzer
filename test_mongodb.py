import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

uri = os.getenv("MONGODB_URI")

try:
    client = MongoClient(
        uri,
        serverSelectionTimeoutMS=15000
    )

    client.admin.command("ping")
    print("SUCCESS: MongoDB Atlas connected!")

    db = client["resume_analyzer"]
    db["connection_test"].insert_one(
        {"message": "MongoDB connection successful"}
    )

    print("SUCCESS: Test document inserted!")

except Exception as e:
    print("CONNECTION ERROR:", repr(e))

finally:
    if "client" in locals():
        client.close()