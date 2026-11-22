from pymongo import MongoClient
from datetime import datetime
from pathlib import Path
import json

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "campus_ai"
COLLECTION = "colleges"

UPDATES = {
    "Madanapalle Institute of Technology and Science": {
        "contact_email": "principal@mits.ac.in",
        "source": "https://mits.ac.in/assets/pdf/admin/Mandatory%20Disclosures%20-%202024-25.pdf"
    },

    "RV College of Engineering": {
        "contact_email": "principal@rvce.edu.in",
        "contact_phone": "+91-80-68188111",
        "source": "https://naac.rvce.edu.in/profile"
    },

    "Dayananda Sagar College of Engineering": {
        "contact_phone": "+91-80-42161751",
        "source": "https://www.amces2020.dsce.edu.in/contact-us"
    },

    "Mohan Babu University": {
        "contact_email": "admissions@mbu.asia",
        "contact_phone": "+91-9469465946",
        "source": "https://www.mbu.asia/contact-us/"
    },

    "IIIT RK Valley (Idupulapaya)": {
        "contact_phone": "7670905568",
        "source": "https://www.rgukt.in/pdfdoc/RITSection41b0604.pdf"
    },

    "IIIT Nuzvid": {
        "contact_phone": "9618422757",
        "source": "https://www.rgukt.in/pdfdoc/RITSection41b0604.pdf"
    }
}


def is_missing(value):
    return value is None or (
        isinstance(value, str) and not value.strip()
    )


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
            f"campus_ai_contacts_batch2_backup_{timestamp}.json"
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
        not_found = 0

        for name, details in UPDATES.items():

            college = collection.find_one({
                "college_name": name
            })

            if not college:
                print("NOT FOUND:", name)
                not_found += 1
                continue

            changes = {}

            for field in ["contact_email", "contact_phone"]:
                value = details.get(field)

                if value and is_missing(college.get(field)):
                    changes[field] = value

            sources = college.get("data_sources", {})

            if not isinstance(sources, dict):
                sources = {}

            new_sources = dict(sources)
            new_sources["contact"] = details["source"]

            if new_sources != sources:
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
        print("CONTACT UPDATE BATCH 2 COMPLETED")
        print("================================")
        print("Colleges covered:", len(UPDATES))
        print("Colleges updated:", updated)
        print("Colleges not found:", not_found)
        print("Backup:", backup_file)

    except Exception as error:
        print("ERROR:", error)

    finally:
        client.close()
        print("MongoDB connection closed.")


if __name__ == "__main__":
    main()