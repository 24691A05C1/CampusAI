from pymongo import MongoClient
from datetime import datetime
from pathlib import Path
import json

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "campus_ai"
COLLECTION = "colleges"

UPDATES = {
    "Dayananda Sagar College of Engineering": {
        "contact_email": "ppl-dsce@dayanandasagar.edu",
        "source": "https://dsca.edu.in/wp-content/uploads/2023/12/NAAC_SSR_Final_submitted_08122021.pdf"
    },

    "Siddharth Institute of Engineering and Technology": {
        "contact_email": "sietk_ptr@yahoo.com",
        "source": "https://www.sietk.org/naac/c3/R%26D_Policy.pdf"
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
            f"campus_ai_contacts_batch4_backup_{timestamp}.json"
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

            if is_missing(college.get("contact_email")):
                changes["contact_email"] = details["contact_email"]

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

                print("\nUPDATED:", name)
                print("Fields:", list(changes.keys()))

            else:
                print("EXISTING EMAIL PRESERVED:", name)

        print("\n================================")
        print("CONTACT UPDATE BATCH 4 COMPLETED")
        print("================================")
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