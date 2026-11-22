from pymongo import MongoClient
from datetime import datetime
from pathlib import Path
import json

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "campus_ai"
COLLECTION = "colleges"

COLLEGE_NAME = "KL University"

# Programmes listed in KL University's official academic document.
COURSES = [
    "B.Tech Biotechnology",
    "B.Tech Civil Engineering",
    "B.Tech Computer Science and Engineering",
    "B.Tech Electronics and Communication Engineering",
    "B.Tech Electrical and Electronics Engineering",
    "B.Tech Mechanical Engineering",
    "B.Tech Artificial Intelligence and Data Science",
    "B.Tech Computer Science and Information Technology",
    "B.Tech Electronics and Computer Science",
    "B.Tech Internet of Things"
]

ADMISSION_INFO = (
    "KL University offers undergraduate engineering programmes. "
    "Its published academic handbook states that B.Tech applicants "
    "should have passed Intermediate or equivalent 10+2. The handbook "
    "specifies minimum 60% marks or equivalent CGPA in Mathematics, "
    "Physics and Chemistry for engineering programmes. Biotechnology "
    "applicants may qualify through Biology, Physics and Chemistry. "
    "The handbook lists KLUEEE, EAMCET and JEE Main as qualifying "
    "admission examination routes. Applicants should check the latest "
    "admission notification for current eligibility and requirements. "
    "The available handbook is an older published document."
)

UPDATES = {
    "courses": COURSES,
    "admission_info": ADMISSION_INFO,
    "admission_url": "https://admissions.kluniversity.in/login-page",
    "data_sources": {
        "official_website": "https://www.kluniversity.in/",
        "programmes": "https://www.kluniversity.in/site/pdfs/2023.pdf",
        "admission_rules": "https://www.kluniversity.in/site/pdfs/bthand.pdf",
        "admissions": "https://admissions.kluniversity.in/login-page"
    }
}


def is_missing(value):
    if value is None:
        return True

    if isinstance(value, str):
        return not value.strip()

    if isinstance(value, (list, dict)):
        return len(value) == 0

    return False


def main():

    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000
    )

    try:
        client.admin.command("ping")

        collection = client[DB_NAME][COLLECTION]

        college = collection.find_one({
            "college_name": COLLEGE_NAME
        })

        if not college:
            print("KL University record not found.")
            return

        print("MongoDB connected.")
        print("KL University record found.")

        # Create backup before modifying the record.
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        backup_file = Path(
            f"kl_university_backup_{timestamp}.json"
        )

        backup_data = dict(college)
        backup_data["_id"] = str(backup_data["_id"])

        with open(backup_file, "w", encoding="utf-8") as file:
            json.dump(
                backup_data,
                file,
                indent=4,
                ensure_ascii=False
            )

        print("Backup created:", backup_file)

        changes = {}

        for field, value in UPDATES.items():

            if field == "data_sources":

                existing = college.get("data_sources", {})

                if not isinstance(existing, dict):
                    existing = {}

                merged = dict(existing)
                merged.update(value)

                if merged != existing:
                    changes[field] = merged

            elif is_missing(college.get(field)):
                changes[field] = value

        if changes:

            changes["data_verified_on"] = (
                datetime.now().strftime("%Y-%m-%d")
            )

            result = collection.update_one(
                {"_id": college["_id"]},
                {"$set": changes}
            )

            print("\nKL UNIVERSITY UPDATED")
            print("Fields updated:", list(changes.keys()))
            print("Modified records:", result.modified_count)

        else:
            print("No missing fields found. Existing data preserved.")

        print("\nKL UNIVERSITY UPDATE COMPLETED")
        print("Backup:", backup_file)

    except Exception as error:
        print("ERROR:", error)

    finally:
        client.close()
        print("MongoDB connection closed.")


if __name__ == "__main__":
    main()