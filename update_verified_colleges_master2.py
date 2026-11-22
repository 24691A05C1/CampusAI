from pymongo import MongoClient
from datetime import datetime
from pathlib import Path
import json

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "campus_ai"
COLLECTION = "colleges"

UPDATES = {

    "JNTUA College of Engineering": {
        "contact_email": "placements.cea@jntua.ac.in",
        "placement_url": "https://jntuacea.ac.in/placements",
        "data_sources": {
            "placements": "https://jntuacea.ac.in/placements"
        }
    },

    "Annamacharya Institute of Technology and Sciences": {
        "contact_email": "aitsap@yahoo.co.in",
        "contact_phone": "9848998641",
        "placement_info": (
            "The official Training and Placement Cell coordinates "
            "campus recruitment, employability training and "
            "placement activities."
        ),
        "placement_url": "https://aitsrajampet.ac.in/t-and-p-cell",
        "data_sources": {
            "contact": "https://www.aitsrajampet.ac.in/contactus",
            "placements": "https://aitsrajampet.ac.in/t-and-p-cell"
        }
    },

    "VIT-AP University": {
        "contact_email": "admission@vitap.ac.in",
        "contact_phone": "0863 2370444",
        "data_sources": {
            "contact": "https://www.vitap.ac.in/contact-us"
        }
    },

    "SRM University-AP": {
        "contact_email": "info@srmap.edu.in",
        "contact_phone": "080-6988-6999",
        "fee_url": "https://www.srmap.edu.in/admission/seas-btech-tuition-fee/",
        "data_sources": {
            "fees": "https://www.srmap.edu.in/admission/seas-btech-tuition-fee/"
        }
    },

    "IIIT Sri City": {
        "contact_email": "contact@iiits.in",
        "contact_phone": "+91 70328 51919",
        "placement_url": "https://iiits.ac.in/contact-us/",
        "data_sources": {
            "contact": "https://iiits.ac.in/contact-us/"
        }
    },

    "PES University": {
        "contact_email": "admissions@pes.edu",
        "contact_phone": "+91 80 26721983",
        "fee_url": "https://pes.edu/fee/",
        "placement_url": "https://pes.edu/contact/",
        "data_sources": {
            "fees": "https://pes.edu/fee/",
            "contact": "https://pes.edu/contact/",
            "admissions": "https://pes.edu/admissions/"
        }
    },

    "Bangalore Institute of Technology": {
        "contact_email": "placement@bit-bangalore.edu.in",
        "placement_url": "https://bit-bangalore.edu.in/placement-team",
        "data_sources": {
            "placements": "https://bit-bangalore.edu.in/placement-team"
        }
    },

    "Dayananda Sagar College of Engineering": {
        "placement_info": (
            "The official placement division coordinates campus "
            "recruitment, internships, pre-placement training "
            "and employer engagement."
        ),
        "placement_url": "https://www.dsce.edu.in/placements/campus-hiring",
        "data_sources": {
            "placements": "https://www.dsce.edu.in/placements/campus-hiring"
        }
    },

    "Nitte Meenakshi Institute of Technology": {
        "contact_email": "enquiry@nitte.edu.in",
        "contact_phone": "080 2216 7800",
        "placement_url": "https://nmit.ac.in/contact-nmit.php",
        "data_sources": {
            "contact": "https://nmit.ac.in/contact-nmit.php"
        }
    },

    "VIT Vellore": {
        "contact_email": "ugadmission@vit.ac.in",
        "contact_phone": "044-462-77555",
        "fee_url": "https://vit.ac.in/admission/ug/fee-structure",
        "placement_url": "https://vit.ac.in/contactus",
        "data_sources": {
            "fees": "https://vit.ac.in/admission/ug/fee-structure",
            "contact": "https://vit.ac.in/contactus"
        }
    }
}


def missing(value):
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

        print("MongoDB connected successfully.")
        print("Total colleges:", len(colleges))

        # Automatic backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        backup_file = Path(
            f"campus_ai_master2_backup_{timestamp}.json"
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
        not_found = []

        for name, updates in UPDATES.items():

            college = collection.find_one({
                "college_name": name
            })

            if not college:
                not_found.append(name)
                print("NOT FOUND:", name)
                continue

            set_values = {}

            for field, value in updates.items():

                if field == "data_sources":

                    existing = college.get("data_sources", {})

                    if not isinstance(existing, dict):
                        existing = {}

                    merged = dict(existing)
                    merged.update(value)

                    if merged != existing:
                        set_values["data_sources"] = merged

                elif missing(college.get(field)):
                    set_values[field] = value

            if set_values:

                set_values["data_verified_on"] = (
                    datetime.now().strftime("%Y-%m-%d")
                )

                collection.update_one(
                    {"_id": college["_id"]},
                    {"$set": set_values}
                )

                updated += 1
                print("UPDATED:", name)

            else:
                print("EXISTING DATA PRESERVED:", name)

        print("\n================================")
        print("MASTER UPDATE 2 COMPLETED")
        print("================================")
        print("Total database records:", len(colleges))
        print("Colleges in this update:", len(UPDATES))
        print("Colleges updated:", updated)
        print("Colleges not found:", len(not_found))
        print("Backup:", backup_file)

        if not_found:
            print("\nNames not found:")
            for name in not_found:
                print("-", name)

        print("\nExisting non-empty fields were preserved.")

    except Exception as error:
        print("ERROR:", error)

    finally:
        client.close()
        print("MongoDB connection closed.")


if __name__ == "__main__":
    main()