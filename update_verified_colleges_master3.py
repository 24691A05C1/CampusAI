from pymongo import MongoClient
from datetime import datetime
from pathlib import Path
import json

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "campus_ai"
COLLECTION = "colleges"

UPDATES = {
    "Madanapalle Institute of Technology and Science": {
        "contact_phone": "+91-8571-280255",
        "placement_info": (
            "The university has an active Training and Placement Cell. "
            "Official placement statistics are published year-wise, "
            "including 2026, 2025 and previous batches."
        ),
        "fee_url": "https://mits.ac.in/scholarship-fees",
        "placement_url": "https://mits.ac.in/placement",
        "data_sources": {
            "fees": "https://mits.ac.in/scholarship-fees",
            "placements": "https://mits.ac.in/placement",
            "placement_team": "https://mits.ac.in/placementcontact",
            "contact": "https://mits.ac.in/contactus"
        }
    },

    "Ashoka Women's Engineering College": {
        "contact_email": "admissions@ashokacollege.in",
        "contact_phone": "+91 7680076600",
        "placement_info": (
            "The Training and Placement Cell publishes placement "
            "records for 2025-26, 2024-25 and 2023-24."
        ),
        "placement_url": "https://www.ashokacollege.in/placement-overview/",
        "data_sources": {
            "contact": "https://www.ashokacollege.in/contact-us/",
            "placements": "https://www.ashokacollege.in/placement-overview/"
        }
    },

    "BMS College of Engineering": {
        "contact_email": "placement@bmsce.ac.in",
        "contact_phone": "+91 9900513488",
        "placement_info": (
            "The Training and Placement Cell coordinates campus "
            "recruitment and publishes placement-related information."
        ),
        "placement_url": "https://www.bmsce.ac.in/home/About-Placements",
        "data_sources": {
            "placements": "https://www.bmsce.ac.in/home/About-Placements",
            "placement_contact": "https://www.bmsce.ac.in/home/Placement-Contact-Us"
        }
    },

    "Mohan Babu University": {
        "placement_info": (
            "The Career Development Centre coordinates student "
            "placements and internships. The official university "
            "website publishes placement information."
        ),
        "placement_url": "https://www.mbu.asia/placements/",
        "data_sources": {
            "placements": "https://www.mbu.asia/placements/"
        }
    },

    "IIIT RK Valley (Idupulapaya)": {
        "contact_email": "director@rguktrkv.ac.in",
        "data_sources": {
            "contact": "https://www.rgukt.in/contact-directory/"
        }
    },

    "IIIT Nuzvid": {
        "contact_email": "director@rguktn.ac.in",
        "data_sources": {
            "contact": "https://www.rgukt.in/contact-directory/"
        }
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
        colleges = list(collection.find({}))

        print("MongoDB connected.")
        print("Total colleges:", len(colleges))

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        backup_file = Path(
            f"campus_ai_master3_backup_{timestamp}.json"
        )

        backup_data = []

        for college in colleges:
            item = dict(college)
            item["_id"] = str(item["_id"])
            backup_data.append(item)

        with open(backup_file, "w", encoding="utf-8") as f:
            json.dump(
                backup_data,
                f,
                indent=4,
                ensure_ascii=False
            )

        print("Backup created:", backup_file)

        updated = 0

        for name, updates in UPDATES.items():

            college = collection.find_one({
                "college_name": name
            })

            if not college:
                print("NOT FOUND:", name)
                continue

            changes = {}

            for field, value in updates.items():

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

                collection.update_one(
                    {"_id": college["_id"]},
                    {"$set": changes}
                )

                updated += 1
                print("UPDATED:", name)
            else:
                print("EXISTING DATA PRESERVED:", name)

        print("\n================================")
        print("MASTER UPDATE 3 COMPLETED")
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