from pymongo import MongoClient
from datetime import datetime
from pathlib import Path
import json

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "campus_ai"
COLLECTION = "colleges"

UPDATES = {
    "KL University": {
        "contact_email": "registraroffice@kluniversity.in",
        "contact_phone": "08645-246948",
        "source": "https://www.kluniversity.in/IQAC/pdfs/ssr.pdf"
    },

    "Sri Venkateswara College of Engineering and Technology": {
        "contact_email": "principal@svcetedu.org",
        "contact_phone": "7729999200",
        "source": "https://svcet.in/wp-content/uploads/2024/Mandatory_Disclosure.pdf"
    },

    "Siddharth Institute of Engineering and Technology": {
        "contact_phone": "08577-264999",
        "source": "https://www.sietk.org/pio_sietk.php"
    },

    "Bangalore Institute of Technology": {
        "contact_phone": "+91-80-26615865",
        "source": "https://bit-bangalore.edu.in/contact"
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
            f"campus_ai_contacts_batch3_backup_{timestamp}.json"
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

                print("\nUPDATED:", name)
                print("Fields:", list(changes.keys()))

            else:
                print("EXISTING DATA PRESERVED:", name)

        print("\n================================")
        print("CONTACT UPDATE BATCH 3 COMPLETED")
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