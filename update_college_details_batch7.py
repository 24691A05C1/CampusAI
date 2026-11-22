from pymongo import MongoClient
from datetime import datetime
from pathlib import Path
import json


MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "campus_ai"
COLLECTION = "colleges"


UPDATES = {

    "Ravindra College of Engineering for Women": {
        "courses": [
            "B.Tech Computer Science and Engineering",
            "B.Tech Computer Science and Engineering (Artificial Intelligence)",
            "B.Tech Electronics and Communication Engineering"
        ],
        "admission_info": (
            "Refer to the official college admission procedure for "
            "current eligibility, AP EAPCET counselling, management "
            "quota and lateral-entry admission details."
        ),
        "admission_url": "https://www.recw.ac.in/admission-procedure/",
        "data_sources": {
            "courses": "https://www.recw.ac.in/programmes/",
            "admission_info": "https://www.recw.ac.in/admission-procedure/"
        }
    },

    "St. John's College of Engineering and Technology": {
        "courses": [
            "B.Tech Computer Science and Engineering",
            "B.Tech Computer Science and Artificial Intelligence",
            "B.Tech Computer Science and Engineering (Data Science)",
            "B.Tech Computer Science and Engineering (Artificial Intelligence and Machine Learning)",
            "B.Tech Electrical and Electronics Engineering",
            "B.Tech Civil Engineering",
            "B.Tech Mechanical Engineering",
            "B.Tech Electronics and Communication Engineering"
        ],
        "admission_info": (
            "Refer to the official St. John's College website for "
            "current B.Tech eligibility, AP EAPCET admission, "
            "management quota and application procedures."
        ),
        "admission_url": "https://sjcet.ac.in/",
        "data_sources": {
            "courses": "https://sjcet.ac.in/exam.php?+Syllabus=&id=13&title=Course+Structure+",
            "admission_info": "https://sjcet.ac.in/"
        }
    },

    "Geethanjali College of Engineering and Technology": {
        "courses": [
            "B.Tech Civil Engineering",
            "B.Tech Computer Science and Engineering",
            "B.Tech Computer Science and Engineering (Artificial Intelligence and Machine Learning)",
            "B.Tech Computer Science and Engineering (Cyber Security)",
            "B.Tech Computer Science and Engineering (Data Science)",
            "B.Tech Computer Science and Engineering (Internet of Things)",
            "B.Tech Electrical and Electronics Engineering",
            "B.Tech Electronics and Communication Engineering",
            "B.Tech Mechanical Engineering",
            "B.Tech Information Technology"
        ],
        "admission_info": (
            "Refer to the official Geethanjali College website for "
            "current B.Tech eligibility, Telangana EAMCET admission, "
            "application dates and admission procedures."
        ),
        "admission_url": "https://gcet.edu.in/",
        "data_sources": {
            "courses": "https://gcet.edu.in/announcement/MDB_05062024.pdf",
            "admission_info": "https://gcet.edu.in/"
        }
    },

    "Rajeev Gandhi Memorial College of Engineering and Technology": {
        "courses": [
            "B.Tech Civil Engineering",
            "B.Tech Electrical and Electronics Engineering",
            "B.Tech Mechanical Engineering",
            "B.Tech Electronics and Communication Engineering",
            "B.Tech Computer Science and Engineering",
            "B.Tech Computer Science and Engineering (Data Science)",
            "B.Tech Computer Science and Engineering (Artificial Intelligence and Machine Learning)",
            "B.Tech Computer Science and Engineering (Cyber Security)"
        ],
        "admission_info": (
            "Refer to the official RGMCET admissions portal for "
            "current B.Tech eligibility, AP EAPCET counselling, "
            "management quota and application details."
        ),
        "admission_url": "https://administration.rgmcet.edu.in/contact/index.php",
        "data_sources": {
            "courses": "https://www.rgmcet.edu.in/courses_offered",
            "admission_info": "https://administration.rgmcet.edu.in/contact/index.php"
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
            / f"campus_ai_colleges_before_batch7_{datetime.now():%Y%m%d_%H%M%S}.json"
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

            # Add courses only when empty
            if is_empty(doc.get("courses")):
                fields["courses"] = info["courses"]

            # Add admission details only when empty
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
        print("CampusAI Batch 7 update completed.")
        print("====================================")

        print(f"Total college records: {len(documents)}")
        print(f"Batch 7 colleges found: {found}/{len(UPDATES)}")
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