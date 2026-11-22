from pymongo import MongoClient
from datetime import datetime
from pathlib import Path
import json


MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "campus_ai"
COLLECTION = "colleges"


UPDATES = {

    "Mohan Babu University": {
        "courses": [
            "B.Tech Computer Science and Engineering",
            "B.Tech Computer Science and Engineering (Artificial Intelligence and Machine Learning)",
            "B.Tech Computer Science and Engineering (Cyber Security)",
            "B.Tech Computer Science and Engineering (Data Science)",
            "B.Tech Computer Science and Engineering (Artificial Intelligence and Data Science)",
            "B.Tech Computer Science and Engineering (DevOps)",
            "B.Tech Computer Science and Engineering (Cloud Computing)",
            "B.Tech Information Technology",
            "B.Tech Electrical and Electronics Engineering",
            "B.Tech Electronics and Communication Engineering",
            "B.Tech Electronics and Computer Engineering",
            "B.Tech Electronics and Instrumentation Engineering",
            "B.Tech Mechanical Engineering",
            "B.Tech Civil Engineering"
        ],
        "admission_info": (
            "Refer to the official Mohan Babu University admissions portal "
            "for current eligibility, entrance requirements, application "
            "dates, fees and admission procedures."
        ),
        "admission_url": "https://www.mbu.asia/admissions/ug-courses/",
        "data_sources": {
            "courses": "https://www.mbu.asia/admissions/ug-courses/",
            "admission_info": "https://www.mbu.asia/admissions/ug-courses/"
        }
    },

    "Ashoka Women's Engineering College": {
        "courses": [
            "B.Tech Computer Science and Engineering",
            "B.Tech Electronics and Communication Engineering",
            "B.Tech Electrical and Electronics Engineering",
            "B.Tech Civil Engineering"
        ],
        "admission_info": (
            "Refer to the official Ashoka Women's Engineering College "
            "website for current admission eligibility, AP EAPCET "
            "counselling, management quota and application details."
        ),
        "admission_url": "https://www.ashokacollege.in/",
        "data_sources": {
            "courses": "https://www.ashokacollege.in/about/mandatory-disclosures/",
            "admission_info": "https://www.ashokacollege.in/"
        }
    },

    "G. Pullaiah College of Engineering and Technology": {
        "courses": [
            "B.Tech Computer Science and Engineering",
            "B.Tech Computer Science and Engineering (Artificial Intelligence)",
            "B.Tech Civil Engineering",
            "B.Tech Electronics and Communication Engineering",
            "B.Tech Electrical and Electronics Engineering",
            "B.Tech Mechanical Engineering"
        ],
        "admission_info": (
            "Refer to the official GPCET website for current B.Tech "
            "admission eligibility, AP EAPCET counselling, seat availability "
            "and application details."
        ),
        "admission_url": "https://www.gpcet.ac.in/",
        "data_sources": {
            "courses": "https://www.gpcet.ac.in/",
            "admission_info": "https://www.gpcet.ac.in/"
        }
    },

    "Dr. K. V. Subba Reddy Institute of Technology": {
        "courses": [
            "B.Tech Computer Science and Engineering",
            "B.Tech Computer Science and Engineering (Artificial Intelligence)",
            "B.Tech Computer Science and Engineering (Artificial Intelligence and Machine Learning)",
            "B.Tech Computer Science and Engineering (Data Science)",
            "B.Tech Electronics and Communication Engineering",
            "B.Tech Electrical and Electronics Engineering",
            "B.Tech Civil Engineering",
            "B.Tech Mechanical Engineering"
        ],
        "admission_info": (
            "Refer to the official Dr. K. V. Subba Reddy Institute "
            "website for current admission eligibility, AP EAPCET "
            "counselling, application dates and admission procedures."
        ),
        "admission_url": "https://www.drkvsrit.ac.in/",
        "data_sources": {
            "courses": "https://www.drkvsrit.ac.in/",
            "admission_info": "https://www.drkvsrit.ac.in/"
        }
    }
}


def is_empty(value):
    return value is None or value == "" or value == []


def main():

    print("Connecting to MongoDB...")

    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000
    )

    try:

        client.admin.command("ping")

        print("MongoDB connected successfully.")

        collection = client[DB_NAME][COLLECTION]

        documents = list(collection.find({}))

        # Create backup before updating
        backup = (
            Path.cwd()
            / f"campus_ai_colleges_before_batch6_{datetime.now():%Y%m%d_%H%M%S}.json"
        )

        with backup.open("w", encoding="utf-8") as file:
            json.dump(
                documents,
                file,
                ensure_ascii=False,
                indent=2,
                default=str
            )

        print(f"Backup created: {backup}")

        found = 0
        processed = 0

        for name, info in UPDATES.items():

            doc = collection.find_one({
                "college_name": name
            })

            if not doc:
                print(f"NOT FOUND: {name}")
                continue

            found += 1

            fields = {}

            # Add courses only when the existing list is empty
            if is_empty(doc.get("courses")):
                fields["courses"] = info["courses"]

            # Add admission information only when empty
            for key in ("admission_info", "admission_url"):

                if is_empty(doc.get(key)):
                    fields[key] = info[key]

            # Preserve existing data sources
            old_sources = doc.get("data_sources") or {}

            if not isinstance(old_sources, dict):
                old_sources = {}

            merged_sources = dict(old_sources)

            for key, url in info["data_sources"].items():
                merged_sources.setdefault(key, url)

            if merged_sources != old_sources:
                fields["data_sources"] = merged_sources

            # Update verification metadata
            fields["data_verified_on"] = datetime.now().strftime(
                "%Y-%m-%d"
            )

            fields["data_verification_note"] = (
                "Course and admission reference information recorded "
                "using institution sources. Existing non-empty fields "
                "preserved. No unsupported fee or placement figures added."
            )

            collection.update_one(
                {"_id": doc["_id"]},
                {"$set": fields}
            )

            processed += 1

            print(f"UPDATED: {name}")

        print("\n====================================")
        print("CampusAI Batch 6 update completed.")
        print("====================================")

        print(f"Total college records: {len(documents)}")
        print(f"Batch 6 colleges found: {found}/{len(UPDATES)}")
        print(f"College documents processed: {processed}")
        print(f"Backup file: {backup}")

        print("\nExisting non-empty fields were preserved.")
        print("No unsupported fee or placement figures were invented.")

    except Exception as error:

        print("\nERROR:", error)

    finally:

        client.close()

        print("\nMongoDB connection closed.")


if __name__ == "__main__":
    main()