from pymongo import MongoClient
from datetime import datetime
from pathlib import Path
import json


MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "campus_ai"
COLLECTION = "colleges"


RGUKT_GENERAL_COURSES = [
    "Six-Year Integrated B.Tech Programme",
    "Pre-University Course (PUC) - MPC",
    "Pre-University Course (PUC) - MBiPC",
    "B.Tech Chemical Engineering",
    "B.Tech Civil Engineering",
    "B.Tech Computer Science and Engineering",
    "B.Tech Computer Science and Engineering (Artificial Intelligence and Machine Learning)",
    "B.Tech Electrical and Electronics Engineering",
    "B.Tech Electronics and Communication Engineering",
    "B.Tech Mechanical Engineering",
    "B.Tech Metallurgical and Materials Engineering"
]


UPDATES = {

    "Santhiram Engineering College": {
        "courses": [
            "B.Tech Electrical and Electronics Engineering",
            "B.Tech Electronics and Communication Engineering",
            "B.Tech Computer Science and Engineering",
            "B.Tech Computer Science and Engineering (Data Science)",
            "B.Tech Computer Science and Engineering (Artificial Intelligence and Machine Learning)",
            "B.Tech Computer Science and Design",
            "M.Tech Embedded Systems",
            "M.Tech VLSI",
            "M.Tech Computer Science and Engineering",
            "M.Tech Computer Science and Engineering (Artificial Intelligence and Machine Learning)",
            "Master of Business Administration (MBA)",
            "Master of Computer Applications (MCA)"
        ],
        "admission_info": (
            "Admissions are offered through Category A government "
            "counselling and Category B management admissions. Refer "
            "to the official admissions page for current eligibility, "
            "entrance examinations and application details."
        ),
        "admission_url": "https://srecnandyal.edu.in/Admissions.php",
        "data_sources": {
            "courses": "https://srecnandyal.edu.in/Courses_Offer.php",
            "admission_info": "https://srecnandyal.edu.in/Admissions.php"
        }
    },

    "IIIT RK Valley (Idupulapaya)": {
        "courses": RGUKT_GENERAL_COURSES,
        "admission_info": (
            "RGUKT offers a six-year integrated programme consisting "
            "of two years of PUC followed by four years of B.Tech. "
            "Admission is generally based on the official RGUKT "
            "admission notification and eligibility criteria. "
            "Engineering branches are allotted after PUC based on "
            "academic performance and reservation rules."
        ),
        "admission_url": "https://admissions.rgukt.in/",
        "data_sources": {
            "courses": "https://rgukt.in/academics/programmes/undergraduate-programmes/",
            "admission_info": "https://admissions.rgukt.in/"
        }
    },

    "IIIT Srikakulam (Etcherla)": {
        "courses": [
            "Six-Year Integrated B.Tech Programme",
            "Pre-University Course (PUC) - MPC",
            "Pre-University Course (PUC) - MBiPC",
            "B.Tech Civil Engineering",
            "B.Tech Computer Science and Engineering",
            "B.Tech Computer Science and Engineering (Artificial Intelligence and Machine Learning)",
            "B.Tech Electrical and Electronics Engineering",
            "B.Tech Electronics and Communication Engineering",
            "B.Tech Mechanical Engineering"
        ],
        "admission_info": (
            "RGUKT offers a six-year integrated programme consisting "
            "of two years of PUC followed by four years of B.Tech. "
            "Admission is based on the official RGUKT admission "
            "notification and eligibility criteria. Engineering "
            "branches are allotted after PUC based on academic "
            "performance and reservation rules. Verify the current "
            "campus-specific branch availability in the prospectus."
        ),
        "admission_url": "https://admissions.rgukt.in/",
        "data_sources": {
            "courses": "https://rgukt.in/academics/programmes/undergraduate-programmes/",
            "admission_info": "https://admissions.rgukt.in/"
        }
    },

    "IIIT Nuzvid": {
        "courses": RGUKT_GENERAL_COURSES,
        "admission_info": (
            "RGUKT offers a six-year integrated programme consisting "
            "of two years of PUC followed by four years of B.Tech. "
            "Admission is based on the official RGUKT admission "
            "notification and eligibility criteria. Engineering "
            "branches are allotted after PUC based on academic "
            "performance and reservation rules."
        ),
        "admission_url": "https://admissions.rgukt.in/",
        "data_sources": {
            "courses": "https://rguktn.ac.in/",
            "admission_info": "https://admissions.rgukt.in/"
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
            / f"campus_ai_colleges_before_batch8_{datetime.now():%Y%m%d_%H%M%S}.json"
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
                "preserved. RGUKT campus-specific programme availability "
                "should be checked against the latest prospectus. "
                "No unsupported fee or placement figures added."
            )

            collection.update_one(
                {"_id": doc["_id"]},
                {"$set": fields}
            )

            processed += 1

            print(f"UPDATED: {name}")

        print("\n====================================")
        print("CampusAI Batch 8 update completed.")
        print("====================================")

        print(f"Total college records: {len(documents)}")
        print(f"Batch 8 colleges found: {found}/{len(UPDATES)}")
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