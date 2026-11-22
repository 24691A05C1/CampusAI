from pymongo import MongoClient
from datetime import datetime
from pathlib import Path
import json

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "campus_ai"
COLLECTION = "colleges"

# Information taken from official college websites.
VERIFIED_UPDATES = {

    "K.S.R.M. College of Engineering": {
        "admission_url": "https://ksrmce.ac.in/admissions/ug",
        "fee_url": "https://ksrmce.ac.in/academics/fee-structure",
        "placement_url": "https://ksrmce.ac.in/placements",
        "data_sources": {
            "courses": "https://www.ksrmce.ac.in/academics/courses-intake",
            "admissions": "https://ksrmce.ac.in/admissions/ug",
            "fees": "https://ksrmce.ac.in/academics/fee-structure",
            "placements": "https://ksrmce.ac.in/placements"
        }
    },

    "JNTUA College of Engineering, Pulivendula": {
        "contact_email": "principal.cep@jntua.ac.in",
        "contact_phone": "9000551427",
        "fee_url": "https://jntuacep.ac.in/academics/fee-structures.php",
        "data_sources": {
            "contact": "https://jntuacep.ac.in/contact-us/",
            "fees": "https://jntuacep.ac.in/academics/fee-structures.php"
        }
    },

    "Ramaiah Institute of Technology": {
        "contact_email": "principal@msrit.edu",
        "contact_phone": "+91-80-23600822",
        "admission_url": "https://www.msrit.edu/admissions.html",
        "placement_url": "https://www.msrit.edu/placement.html",
        "data_sources": {
            "admissions": "https://www.msrit.edu/admissions.html",
            "placements": "https://www.msrit.edu/placement.html",
            "contact": "https://msrit.edu/contact-us.html"
        }
    },

    "Ravindra College of Engineering for Women": {
        "contact_email": "principal@recw.ac.in",
        "contact_phone": "+91-8639756876",
        "placement_url": "https://www.recw.ac.in/contact-us/",
        "data_sources": {
            "contact": "https://www.recw.ac.in/contact-us/"
        }
    },

    "IIIT Srikakulam (Etcherla)": {
        "contact_email": "tnpsi@rguktsklm.ac.in",
        "contact_phone": "9491321146",
        "placement_url": "https://placements.rguktsklm.ac.in/",
        "data_sources": {
            "placements": "https://placements.rguktsklm.ac.in/"
        }
    },

    "IIIT RK Valley (Idupulapaya)": {
        "admission_url": "https://rgukt.in/admissions/ug-admissions/2026/",
        "data_sources": {
            "admissions": "https://rgukt.in/admissions/ug-admissions/2026/",
            "contact": "https://rgukt.in/contact-us/"
        }
    },

    "IIIT Nuzvid": {
        "admission_url": "https://rgukt.in/admissions/ug-admissions/2026/",
        "data_sources": {
            "admissions": "https://rgukt.in/admissions/ug-admissions/2026/",
            "contact": "https://rgukt.in/contact-us/"
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

        print("\nMongoDB connected successfully.")
        print("Total college records:", len(colleges))

        # BACKUP
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        backup_file = Path(
            f"campus_ai_master_backup_{timestamp}.json"
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

        print("\nBackup created:", backup_file)

        updated = 0
        unchanged = 0
        not_found = []

        # PROCESS ALL COLLEGES
        for college in colleges:

            name = college.get("college_name", "")

            if name not in VERIFIED_UPDATES:
                unchanged += 1
                continue

            updates = VERIFIED_UPDATES[name]
            set_values = {}

            for field, value in updates.items():

                if field == "data_sources":

                    existing = college.get("data_sources", {})

                    if not isinstance(existing, dict):
                        existing = {}

                    merged = dict(existing)

                    for source_name, source_url in value.items():
                        merged[source_name] = source_url

                    if merged != existing:
                        set_values["data_sources"] = merged

                elif is_missing(college.get(field)):
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
                unchanged += 1
                print("ALREADY COMPLETE:", name)

        # FINAL AUDIT
        latest = list(collection.find({}))

        fields = [
            "courses",
            "admission_info",
            "admission_url",
            "fee_structure",
            "fee_url",
            "placement_info",
            "placement_url",
            "contact_email",
            "contact_phone",
            "website",
            "data_sources"
        ]

        report_file = Path(
            f"campus_ai_master_report_{timestamp}.txt"
        )

        with open(report_file, "w", encoding="utf-8") as report:

            report.write("CAMPUSAI MASTER DATABASE AUDIT\n")
            report.write("=" * 45 + "\n")

            report.write(
                f"Total colleges: {len(latest)}\n"
            )

            report.write(
                f"Colleges updated: {updated}\n\n"
            )

            for field in fields:

                missing = [
                    c.get("college_name", "Unknown")
                    for c in latest
                    if is_missing(c.get(field))
                ]

                report.write(f"\n{field}\n")
                report.write(
                    f"Completed: {len(latest) - len(missing)}/{len(latest)}\n"
                )
                report.write(
                    f"Missing: {len(missing)}\n"
                )

                for name in missing:
                    report.write(f"- {name}\n")

        print("\n====================================")
        print("CAMPUSAI MASTER UPDATE COMPLETED")
        print("====================================")
        print("Total colleges checked:", len(latest))
        print("Colleges updated:", updated)
        print("Other colleges unchanged:", unchanged)
        print("Backup:", backup_file)
        print("Audit report:", report_file)

    except Exception as error:
        print("\nERROR:", error)

    finally:
        client.close()
        print("\nMongoDB connection closed.")


if __name__ == "__main__":
    main()