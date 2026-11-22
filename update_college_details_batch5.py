from pymongo import MongoClient
from datetime import datetime
from pathlib import Path
import json

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "campus_ai"
COLLECTION = "colleges"


UPDATES = {

    "Nitte Meenakshi Institute of Technology": {
        "courses": [
            "B.Tech Aeronautical Engineering",
            "B.Tech Artificial Intelligence and Data Science",
            "B.Tech Artificial Intelligence and Machine Learning",
            "B.Tech Civil Engineering",
            "B.Tech Computer Science and Engineering",
            "B.Tech Computer Science and Business Systems",
            "B.Tech Electrical and Electronics Engineering",
            "B.Tech Electronics and Communication Engineering",
            "B.Tech Electronics (VLSI Design and Technology)",
            "B.Tech Information Science and Engineering",
            "B.Tech Mechanical Engineering",
            "B.Tech Robotics and Artificial Intelligence"
        ],
        "admission_info": (
            "Refer to the official Nitte admissions portal for current "
            "eligibility, NUCAT requirements, application procedure "
            "and admission dates."
        ),
        "admission_url": "https://nitte.edu.in/admissions.php",
        "data_sources": {
            "courses": "https://nitte.edu.in/admissions.php",
            "admission_info": "https://nitte.edu.in/admissions.php"
        }
    },

    "Sri Venkateswara College of Engineering and Technology": {
        "courses": [
            "B.Tech Computer Science and Engineering",
            "B.Tech Information Technology",
            "B.Tech Artificial Intelligence and Machine Learning",
            "B.Tech Artificial Intelligence",
            "B.Tech Computer Science and Engineering (Data Science)",
            "B.Tech Computer Science and Engineering (Cyber Security)",
            "B.Tech Computer Science and Engineering (Internet of Things)",
            "B.Tech Computer Science and Business Systems",
            "B.Tech Electronics and Communication Engineering",
            "B.Tech Electrical and Electronics Engineering",
            "B.Tech Mechanical Engineering",
            "B.Tech Civil Engineering",
            "B.Tech Electronics and Communication Engineering (Biomedical Engineering)"
        ],
        "admission_info": (
            "Refer to the official SVCET website for current admission "
            "eligibility, AP EAPCET counselling, management quota "
            "and application details."
        ),
        "admission_url": "https://svcet.in/",
        "data_sources": {
            "courses": "https://svcet.in/wp-content/uploads/2024/Mandatory_Disclosure.pdf",
            "admission_info": "https://svcet.in/"
        }
    },

    "Viswam Engineering College": {
        "courses": [
            "B.Tech Computer Science and Engineering",
            "B.Tech Computer Science and Engineering (Artificial Intelligence and Machine Learning)",
            "B.Tech Computer Science and Engineering (Artificial Intelligence and Data Science)",
            "B.Tech Computer Science and Engineering (Artificial Intelligence)",
            "B.Tech Computer Science and Technology",
            "B.Tech Cyber Security",
            "B.Tech Electronics and Communication Engineering",
            "B.Tech Electrical and Electronics Engineering",
            "B.Tech Mechanical Engineering",
            "B.Tech Civil Engineering"
        ],
        "admission_info": (
            "Refer to the official Viswam Engineering College website "
            "for current B.Tech admission eligibility, AP EAPCET "
            "counselling and application details."
        ),
        "admission_url": "https://viswam.ac.in/course-admission/",
        "data_sources": {
            "courses": "https://viswam.ac.in/",
            "admission_info": "https://viswam.ac.in/course-admission/"
        }
    },

    "Siddharth Institute of Engineering and Technology": {
        "courses": [
            "B.Tech Civil Engineering",
            "B.Tech Electrical and Electronics Engineering",
            "B.Tech Mechanical Engineering",
            "B.Tech Electronics and Communication Engineering",
            "B.Tech Computer Science and Engineering",
            "B.Tech Computer Science and Information Technology",
            "B.Tech Agricultural Engineering",
            "B.Tech Computer Science and Engineering (Artificial Intelligence and Machine Learning)",
            "B.Tech Computer Science and Engineering (Internet of Things and Cyber Security including Blockchain Technology)"
        ],
        "admission_info": (
            "Refer to the official Siddharth Institute website for "
            "current admission eligibility, AP EAPCET counselling, "
            "application dates and admission procedures."
        ),
        "admission_url": "https://www.sietk.org/",
        "data_sources": {
            "courses": "https://www.sietk.org/naac/dvv/c1/1.2.2.%20Program%20course%20structure%20with%20electives.pdf",
            "admission_info": "https://www.sietk.org/"
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
            / f"campus_ai_colleges_before_batch5_{datetime.now():%Y%m%d_%H%M%S}.json"
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

            # Add courses only if empty
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

            # Verification metadata
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
        print("CampusAI Batch 5 update completed.")
        print("====================================")

        print(f"Total college records: {len(documents)}")
        print(f"Batch 5 colleges found: {found}/{len(UPDATES)}")
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