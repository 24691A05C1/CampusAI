from pymongo import MongoClient
from datetime import datetime
from pathlib import Path
import json


MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "campus_ai"
COLLECTION = "colleges"


UPDATES = {

    "Aditya College of Engineering": {
        "courses": [
            "B.Tech Civil Engineering",
            "B.Tech Electrical and Electronics Engineering",
            "B.Tech Mechanical Engineering",
            "B.Tech Electronics and Communication Engineering",
            "B.Tech Computer Science and Engineering",
            "B.Tech Information Technology",
            "B.Tech Computer Science and Engineering (Artificial Intelligence and Machine Learning)",
            "B.Tech Computer Science and Engineering (Data Science)",
            "B.Tech Computer Science and Engineering (Internet of Things)",
            "M.Tech Thermal Engineering",
            "M.Tech Embedded Systems",
            "M.Tech Computer Science and Engineering",
            "Master of Business Administration (MBA)",
            "Master of Computer Applications (MCA)"
        ],
        "admission_info": (
            "Refer to the official institution website for current "
            "admission eligibility, entrance examinations, application "
            "dates and programme availability. Check the latest approved "
            "intake before applying. The published programme document "
            "lists some programmes with zero intake for AY 2025-26."
        ),
        "admission_url": "https://acet.ac.in/",
        "data_sources": {
            "courses": "https://acet.ac.in/ACET/mandatory_disclosure/3.1_Programmes.pdf",
            "admission_info": "https://acet.ac.in/"
        }
    },

    "Sreenivasa Institute of Technology and Management Studies (SITAMS)": {
        "courses": [
            "B.Tech Computer Science and Engineering",
            "B.Tech Computer Science and Engineering (Artificial Intelligence and Machine Learning)",
            "B.Tech Computer Science and Engineering (Artificial Intelligence)",
            "B.Tech Computer Science and Engineering (Data Science)",
            "B.Tech Electronics and Communication Engineering",
            "B.Tech Electrical and Electronics Engineering",
            "B.Tech Civil Engineering",
            "B.Tech Mechanical Engineering",
            "Master of Business Administration (MBA)",
            "Master of Computer Applications (MCA)",
            "M.Tech Mechanical Engineering",
            "M.Tech Electrical and Electronics Engineering",
            "M.Tech Electronics and Communication Engineering",
            "M.Tech Computer Science and Engineering"
        ],
        "admission_info": (
            "Refer to the official SITAMS admissions website for "
            "current B.Tech eligibility, AP EAPCET counselling, "
            "management quota, lateral entry and application details."
        ),
        "admission_url": "https://sitams.ac.in/undergraduate-courses/",
        "data_sources": {
            "courses": "https://sitams.ac.in/undergraduate-courses/",
            "admission_info": "https://sitams.ac.in/"
        }
    },

    "GITAM Deemed to be University - Bengaluru Campus": {
        "courses": [
            "B.Tech Computer Science and Engineering",
            "B.Tech Computer Science and Engineering (Artificial Intelligence and Machine Learning)",
            "B.Tech Computer Science and Engineering (Cyber Security)",
            "B.Tech Computer Science and Engineering (Data Science)",
            "M.Tech Data Science",
            "Ph.D Computer Science and Engineering"
        ],
        "admission_info": (
            "Refer to the official GITAM admissions portal for "
            "Bengaluru campus programme availability, eligibility, "
            "GAT examination requirements, application dates and "
            "admission procedures."
        ),
        "admission_url": "https://www.gitam.edu/about/campus-life/bengaluru",
        "data_sources": {
            "courses": "https://www.gitam.edu/about/campus-life/bengaluru",
            "admission_info": "https://programmes.gitam.edu/ug/"
        }
    },

    "Mother Theresa Institute of Engineering and Technology": {
        "courses": [
            "B.Tech Computer Science and Engineering",
            "B.Tech Computer Science and Engineering (Data Science)",
            "B.Tech Computer Science and Engineering (Artificial Intelligence)",
            "B.Tech Artificial Intelligence and Data Science",
            "B.Tech Electronics and Communication Engineering",
            "B.Tech Electrical and Electronics Engineering",
            "B.Tech Civil Engineering",
            "M.Tech Computer Science and Engineering",
            "Master of Business Administration (MBA)",
            "Master of Computer Applications (MCA)"
        ],
        "admission_info": (
            "Refer to the official Mother Theresa Institute admissions "
            "page for current eligibility, AP EAPCET counselling, "
            "management quota, application dates and admission "
            "procedures. Verify the current approved programme intake."
        ),
        "admission_url": "https://mtieat.org/admissions",
        "data_sources": {
            "courses": "https://mtieat.org/admissions",
            "admission_info": "https://mtieat.org/admissions"
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
            / f"campus_ai_colleges_before_batch9_{datetime.now():%Y%m%d_%H%M%S}.json"
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

            # Add courses only if existing courses are empty
            if is_empty(doc.get("courses")):
                fields["courses"] = info["courses"]

            # Add admission information only if empty
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
                "preserved. Current programme availability and intake "
                "should be confirmed using the latest official documents. "
                "No unsupported fee or placement figures added."
            )

            collection.update_one(
                {"_id": doc["_id"]},
                {"$set": fields}
            )

            processed += 1

            print(f"UPDATED: {name}")

        print("\n====================================")
        print("CampusAI Batch 9 update completed.")
        print("====================================")

        print(f"Total college records: {len(documents)}")
        print(f"Batch 9 colleges found: {found}/{len(UPDATES)}")
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