from pymongo import MongoClient
from datetime import datetime
from pathlib import Path
import json

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "campus_ai"
COLLECTION = "colleges"

UPDATES = {

    "JNTU Kakinada": {
        "fee_structure": (
            "JNTUK publishes separate fee information for domestic "
            "and international admissions. Its published 2024-25 "
            "NRI/OCI/FN B.Tech tuition was USD 3,000 per year, with "
            "USD 100 registration/admission fee. This is an "
            "international admission figure, NOT the domestic "
            "AP EAPCET fee. The current domestic B.Tech fee should "
            "be confirmed through the latest AP counselling/government "
            "fee notification."
        ),
        "fee_url": "https://dfur.jntuk.edu.in/fee"
    },

    "IIIT Sri City": {
        "fee_structure": (
            "Official JoSAA/CSAB admission fee documents publish "
            "programme fees by academic year. The official 2025-26 "
            "UG admission document listed tuition of Rs. 1,75,000 "
            "per semester, hostel establishment fee of Rs. 22,000 "
            "per semester, mess fee of Rs. 22,000 per semester, "
            "one-time admission fee Rs. 17,000, refundable caution "
            "deposit Rs. 20,000 and alumni fee Rs. 2,000. "
            "These are 2025-26 figures, not confirmed 2026-27 "
            "JoSAA figures. Check the latest admission circular."
        ),
        "fee_url": (
            "https://iiits.ac.in/admissions/b-tech-programme/josaa-csab/"
        )
    },

    "RV College of Engineering": {
        "fee_structure": (
            "The official AICTE mandatory disclosure (January 2023) "
            "listed CET tuition of Rs. 58,806 per year and additional "
            "annual fees of Rs. 40,000. These are historical disclosed "
            "figures and must not be treated as current 2026-27 fees. "
            "RVCE publishes separate admission fee documents for "
            "KEA/CET, COMEDK, management and NRI categories. "
            "The applicable current amount depends on admission quota."
        ),
        "fee_url": "https://oldback.rvce.edu.in/Admission"
    },

    "PES University": {
        "fee_structure": (
            "PES University publishes separate B.Tech fee schedules "
            "for different admission routes, including CET and JEE "
            "Main quota. The official fee page also distinguishes "
            "programme-wise tuition and management/NRI categories. "
            "The displayed 2027-28 figures should not be treated as "
            "2026-27 fees. Confirm the applicable academic year and "
            "admission quota with the university."
        ),
        "fee_url": "https://pes.edu/fee/"
    },

    "Ramaiah Institute of Technology": {
        "fee_structure": (
            "The official admissions page publishes separate "
            "2026-27 fee documents for first-year B.E./B.Arch and "
            "higher-semester B.E./B.Arch students. Fees vary by "
            "admission category and course. Refer to the official "
            "year-labelled fee documents for exact amounts rather "
            "than applying one amount to all students."
        ),
        "fee_url": "https://msrit.edu/admissions.html"
    },

    "Bangalore Institute of Technology": {
        "fee_structure": (
            "The official BIT admission page identifies separate "
            "B.E. admission seat categories: KCET, COMEDK and "
            "Management, with a separate SNQ category. The accessible "
            "admission page does not provide a complete current "
            "programme-wise fee table. Exact tuition and other "
            "charges must be confirmed through the applicable "
            "2026-27 counselling notification or college office."
        ),
        "fee_url": "https://bit-bangalore.edu.in/admission-be"
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
            f"campus_ai_fee_batch3_backup_{timestamp}.json"
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

            if is_missing(college.get("fee_structure")):
                changes["fee_structure"] = details["fee_structure"]

            if is_missing(college.get("fee_url")):
                changes["fee_url"] = details["fee_url"]

            existing_sources = college.get("data_sources", {})

            if not isinstance(existing_sources, dict):
                existing_sources = {}

            new_sources = dict(existing_sources)
            new_sources["fees"] = details["fee_url"]

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
        print("FEE UPDATE BATCH 3 COMPLETED")
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