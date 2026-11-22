from pymongo import MongoClient
from datetime import datetime
from pathlib import Path
import json

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "campus_ai"
COLLECTION = "colleges"

UPDATES = {
    "JNTUA College of Engineering, Kalikiri": {
        "contact_email": "principal.cek@jntua.ac.in",
        "contact_phone": "+91 6304907071",
        "source": "https://www.jntuacek.ac.in/contact-us/"
    },

    "Madanapalle Institute of Technology and Science": {
        "contact_phone": "+91-8571-280255",
        "source": "https://mits.ac.in/contactus"
    },

    "JNTU Kakinada": {
        "contact_email": "registrar@jntuk.edu.in",
        "contact_phone": "+91 884 230 0900",
        "source": "https://jntuk.edu.in/contacts"
    },

    "G. Pullaiah College of Engineering and Technology": {
        "contact_email": "principal@gpcet.ac.in",
        "contact_phone": "08518-285088",
        "source": "https://www.gpcet.ac.in/contact-us/"
    },

    "Dr. K. V. Subba Reddy Institute of Technology": {
        "contact_email": "info@drkvsrit.in",
        "contact_phone": "7660003345",
        "source": "https://drkvsrit.ac.in/contact/index.html"
    },

    "Geethanjali College of Engineering and Technology": {
        "contact_email": "info@gcet.edu.in",
        "contact_phone": "9182058187",
        "source": "https://gcet.edu.in/img/downloads/manda_disclo.pdf"
    },

    "Rajeev Gandhi Memorial College of Engineering and Technology": {
        "contact_email": "principal.9@jntua.ac.in",
        "contact_phone": "08514-275203",
        "source": "https://rgmcet.edu.in/assets/img/documents/UGC-Compliance%20Report.pdf"
    },

    "Santhiram Engineering College": {
        "contact_email": "principal@srecnandyal.edu.in",
        "contact_phone": "+91-9866308475",
        "source": "https://www.srecnandyal.edu.in/Contact-us.php"
    },

    "Aditya College of Engineering": {
        "contact_email": "office@acet.ac.in",
        "contact_phone": "0884-2326212",
        "source": "https://acet.ac.in/"
    },

    "St. John's College of Engineering and Technology": {
        "contact_email": "principal@sjcet.ac.in",
        "contact_phone": "+91-9963623801",
        "source": "https://www.sjcet.ac.in/contact.php"
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
            f"campus_ai_contacts_batch1_backup_{timestamp}.json"
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

                print("UPDATED:", name)
                print("Fields:", list(changes.keys()))

            else:
                print("EXISTING DATA PRESERVED:", name)

        print("\n================================")
        print("CONTACT UPDATE BATCH 1 COMPLETED")
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