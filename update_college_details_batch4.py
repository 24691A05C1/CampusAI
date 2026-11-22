from pymongo import MongoClient
from datetime import datetime
from pathlib import Path
import json


# MongoDB connection
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "campus_ai"
COLLECTION = "colleges"


# College details
UPDATES = {

    "PES University": {
        "courses": [
            "B.Tech Computer Science and Engineering",
            "B.Tech Computer Science and Engineering (Artificial Intelligence and Machine Learning)",
            "B.Tech Electronics and Communication Engineering",
            "B.Tech Electrical and Electronics Engineering",
            "B.Tech Mechanical Engineering"
        ],
        "admission_info": (
            "Refer to the official PES University admissions portal for "
            "current-year eligibility, entrance examinations, application "
            "dates and admission procedures."
        ),
        "admission_url": "https://www.pes.edu/admissions/",
        "data_sources": {
            "courses": "https://www.pes.edu/",
            "admission_info": "https://www.pes.edu/admissions/"
        }
    },

    "Ramaiah Institute of Technology": {
        "courses": [
            "B.E. Computer Science and Engineering",
            "B.E. Information Science and Engineering",
            "B.E. Artificial Intelligence and Machine Learning",
            "B.E. Computer Science and Engineering (Data Science)",
            "B.E. Electronics and Communication Engineering",
            "B.E. Electrical and Electronics Engineering",
            "B.E. Mechanical Engineering",
            "B.E. Civil Engineering",
            "B.E. Chemical Engineering",
            "B.E. Biotechnology",
            "B.E. Industrial Engineering and Management",
            "B.E. Medical Electronics Engineering",
            "B.E. Electronics and Instrumentation Engineering",
            "B.E. Telecommunication Engineering"
        ],
        "admission_info": (
            "Refer to the official Ramaiah Institute of Technology admissions "
            "page for current-year eligibility, entrance examinations, "
            "seat allocation and application details."
        ),
        "admission_url": "https://www.msrit.edu/admissions.html",
        "data_sources": {
            "courses": "https://www.msrit.edu/",
            "admission_info": "https://www.msrit.edu/admissions.html"
        }
    },

    "Bangalore Institute of Technology": {
        "courses": [
            "B.E. Computer Science and Engineering",
            "B.E. Information Science and Engineering",
            "B.E. Artificial Intelligence and Machine Learning",
            "B.E. Electronics and Communication Engineering",
            "B.E. Electrical and Electronics Engineering",
            "B.E. Mechanical Engineering",
            "B.E. Civil Engineering",
            "B.E. Chemical Engineering",
            "B.E. Industrial Engineering and Management",
            "B.E. Electronics and Instrumentation Engineering",
            "B.E. Medical Electronics Engineering"
        ],
        "admission_info": (
            "Refer to the official Bangalore Institute of Technology website "
            "for current-year admission eligibility, entrance examination "
            "requirements, application dates and admission procedures."
        ),
        "admission_url": "https://bit-bangalore.edu.in/",
        "data_sources": {
            "courses": "https://bit-bangalore.edu.in/",
            "admission_info": "https://bit-bangalore.edu.in/"
        }
    },

    "Dayananda Sagar College of Engineering": {
        "courses": [
            "B.E. Computer Science and Engineering",
            "B.E. Information Science and Engineering",
            "B.E. Artificial Intelligence and Machine Learning",
            "B.E. Computer Science and Engineering (Data Science)",
            "B.E. Computer Science and Engineering (Cyber Security)",
            "B.E. Computer Science and Engineering (IoT and Cyber Security including Blockchain Technology)",
            "B.E. Computer Science and Design",
            "B.E. Electrical and Electronics Engineering",
            "B.E. Electronics and Communication Engineering",
            "B.E. Electronics and Instrumentation Engineering",
            "B.E. Mechanical Engineering",
            "B.E. Medical Electronics Engineering",
            "B.E. Electronics and Telecommunication Engineering",
            "B.E. Robotics and Artificial Intelligence"
        ],
        "admission_info": (
            "Refer to the official DSCE admissions portal for current-year "
            "eligibility, entrance route, seat category and application dates. "
            "Verify programme availability for the relevant admission year."
        ),
        "admission_url": "https://admissions.dayanandasagar.edu/dsce/",
        "data_sources": {
            "courses": "https://www.dsce.edu.in/homepage",
            "admission_info": "https://admissions.dayanandasagar.edu/dsce/"
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
            / f"campus_ai_colleges_before_batch4_{datetime.now():%Y%m%d_%H%M%S}.json"
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

            # Add courses only if the existing course list is empty
            if is_empty(doc.get("courses")):
                fields["courses"] = info["courses"]

            # Add admission details only if fields are empty
            for key in ("admission_info", "admission_url"):
                if is_empty(doc.get(key)):
                    fields[key] = info[key]

            # Preserve existing sources and add missing source links
            old_sources = doc.get("data_sources") or {}

            if not isinstance(old_sources, dict):
                old_sources = {}

            merged_sources = dict(old_sources)

            for key, url in info["data_sources"].items():
                merged_sources.setdefault(key, url)

            if merged_sources != old_sources:
                fields["data_sources"] = merged_sources

            # Update verification metadata
            fields["data_verified_on"] = datetime.now().strftime("%Y-%m-%d")

            fields["data_verification_note"] = (
                "Course and admissions reference links recorded from "
                "institution websites. Existing non-empty values preserved. "
                "No unsupported fee amounts or placement figures added."
            )

            collection.update_one(
                {"_id": doc["_id"]},
                {"$set": fields}
            )

            processed += 1

            print(f"UPDATED: {name}")

        print("\n====================================")
        print("CampusAI Batch 4 update completed.")
        print("====================================")
        print(f"Total college records: {len(documents)}")
        print(f"Batch 4 colleges found: {found}/{len(UPDATES)}")
        print(f"College documents processed: {processed}")
        print(f"Backup file: {backup}")

        print("\nNo unsupported fee amounts or placement figures were invented.")

    except Exception as error:
        print("\nERROR:", error)

    finally:
        client.close()
        print("\nMongoDB connection closed.")


if __name__ == "__main__":
    main()