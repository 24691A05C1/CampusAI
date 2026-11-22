from pymongo import MongoClient
from datetime import datetime
from pathlib import Path
import json

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "campus_ai"
COLLECTION = "colleges"

UPDATES = {

    "JNTU Kakinada": {
        "placement_info": (
            "JNTU Kakinada coordinates placement activities through "
            "its Training and Placement Office and university "
            "placement administration. Activities include campus "
            "recruitment drives, pooled placements, internships, "
            "industry interaction and student skill development. "
            "Placement opportunities depend on the programme, "
            "affiliated institution and student eligibility. "
            "A consolidated current university-wide placement "
            "percentage was not confirmed."
        ),
        "placement_url": "https://jntuk.edu.in/ugc-disclosure.php"
    },

    "IIIT Sri City": {
        "placement_info": (
            "According to the official placement archive, the "
            "2025 graduating batch recorded 93.60% placement "
            "as of 30 May 2025. The overall average CTC was "
            "Rs. 18.44 LPA, median CTC Rs. 14.32 LPA and "
            "maximum CTC Rs. 120 LPA. CSE average CTC was "
            "Rs. 19.24 LPA and ECE average CTC was Rs. 14.85 LPA. "
            "These are historical batch-specific figures."
        ),
        "placement_url": (
            "https://iiits.ac.in/campus-placement-archive/"
        )
    },

    "RV College of Engineering": {
        "placement_info": (
            "RV College of Engineering has an active Training "
            "and Placement Department that coordinates campus "
            "recruitment and industry interaction. Its published "
            "2024-25 placement growth data reports 936 offers "
            "and 862 students selected, with a highest salary "
            "of Rs. 67 LPA. The report marks these figures with "
            "an asterisk, so they should be treated as the "
            "reported 2024-25 figures rather than guaranteed "
            "final outcomes."
        ),
        "placement_url": (
            "https://rvce.rveducationalinstitutions.com/wp-content/"
            "uploads/2025/10/autonomous-guidelines.pdf"
        )
    },

    "PES University": {
        "placement_info": (
            "PES University provides placement support through "
            "its career development and placement activities. "
            "According to its NIRF 2026 Engineering submission, "
            "1,068 UG students were placed in the 2024-25 "
            "graduating cohort, with a median salary of "
            "Rs. 13.05 LPA. The university recruits students "
            "for technology, administration, business development, "
            "marketing, finance and other roles. These figures "
            "are historical and refer to the reported UG cohort."
        ),
        "placement_url": "https://pes.edu/placements/"
    },

    "Ramaiah Institute of Technology": {
        "placement_info": (
            "Ramaiah Institute of Technology has a dedicated "
            "Department of Placement and Training established "
            "in 1997. It coordinates campus recruitment with "
            "national and international organisations and "
            "provides aptitude training, communication skills, "
            "mock interviews, group discussions, internships "
            "and industry interaction. The official placement "
            "page publishes placement highlights and registration "
            "information. Outcomes vary by branch and batch."
        ),
        "placement_url": "https://www.msrit.edu/placement.html"
    },

    "Bangalore Institute of Technology": {
        "placement_info": (
            "Bangalore Institute of Technology has a dedicated "
            "Department of Training and Placement established "
            "in 1994. Its official placement page reports "
            "702 offers for 2024-25 and describes training "
            "in personality development, communication, aptitude, "
            "logical reasoning, group discussions and mock "
            "interviews. The department also supports internships "
            "and industry interaction. Placement outcomes "
            "vary by programme and graduating batch."
        ),
        "placement_url": (
            "https://bit-bangalore.edu.in/placement-about"
        )
    }
}


def is_missing(value):
    if value is None:
        return True

    if isinstance(value, str):
        return not value.strip()

    return False


def main():

    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000
    )

    try:
        client.admin.command("ping")

        collection = client[DB_NAME][COLLECTION]
        colleges = list(collection.find({}))

        print("MongoDB connected.")
        print("Total colleges:", len(colleges))

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        backup_file = Path(
            f"campus_ai_placement_batch2_backup_{timestamp}.json"
        )

        backup_data = []

        for college in colleges:
            item = dict(college)
            item["_id"] = str(item["_id"])
            backup_data.append(item)

        with open(backup_file, "w", encoding="utf-8") as file:
            json.dump(
                backup_data,
                file,
                indent=4,
                ensure_ascii=False
            )

        print("Backup created:", backup_file)

        updated = 0

        for name, details in UPDATES.items():

            college = collection.find_one({
                "college_name": name
            })

            if not college:
                print("NOT FOUND:", name)
                continue

            changes = {}

            if is_missing(college.get("placement_info")):
                changes["placement_info"] = details["placement_info"]

            if is_missing(college.get("placement_url")):
                changes["placement_url"] = details["placement_url"]

            existing_sources = college.get("data_sources", {})

            if not isinstance(existing_sources, dict):
                existing_sources = {}

            new_sources = dict(existing_sources)
            new_sources["placements"] = details["placement_url"]

            if new_sources != existing_sources:
                changes["data_sources"] = new_sources

            if changes:

                changes["data_verified_on"] = (
                    datetime.now().strftime("%Y-%m-%d")
                )

                collection.update_one(
                    {"_id": college["_id"]},
                    {"$set": changes}
                )

                updated += 1

                print("UPDATED:", name)
                print("Fields:", list(changes.keys()))

            else:
                print("EXISTING DATA PRESERVED:", name)

        print("\n================================")
        print("PLACEMENT UPDATE BATCH 2 COMPLETED")
        print("================================")
        print("Total colleges:", len(colleges))
        print("Colleges covered:", len(UPDATES))
        print("Colleges updated:", updated)
        print("Backup:", backup_file)

    except Exception as error:
        print("ERROR:", error)

    finally:
        client.close()
        print("MongoDB connection closed.")


if __name__ == "__main__":
    main()