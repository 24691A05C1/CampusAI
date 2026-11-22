from pymongo import MongoClient
from datetime import datetime
from pathlib import Path
import json

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "campus_ai"
COLLECTION = "colleges"

UPDATES = {

    "Dayananda Sagar College of Engineering": {
        "fee_structure": (
            "The college provides an online fee-payment portal for "
            "B.E., M.Tech, MBA and MCA programmes. A complete public "
            "2026-27 programme-wise fee schedule was not confirmed "
            "from the official page. Fees may vary by admission "
            "category and programme. Students should obtain the "
            "applicable written fee structure from the admissions "
            "office before payment."
        ),
        "fee_url": (
            "https://www.dsce.edu.in/admissions/pay-fee-online"
        )
    },

    "Sri Venkateswara College of Engineering and Technology": {
        "fee_structure": (
            "The college's official mandatory disclosure lists "
            "UG Engineering and Technology fees of Rs. 52,800. "
            "The disclosure is associated with the 2024 admission "
            "cycle and should be treated as a historical approved "
            "fee reference, not a confirmed 2026-27 amount. "
            "Current fees may vary by admission category and "
            "government notifications."
        ),
        "fee_url": (
            "https://svcet.in/wp-content/uploads/2024/"
            "Mandatory_Disclosure.pdf"
        )
    },

    "Siddharth Institute of Engineering and Technology": {
        "fee_structure": (
            "The official 2026-27 AICTE approval document confirms "
            "the institution's approved programmes and intake, "
            "but does not provide a complete current B.Tech tuition "
            "schedule. The exact fee should be checked against the "
            "latest AP EAPCET counselling fee notification and "
            "the college's admission office. Do not assume one "
            "amount applies to all admission categories."
        ),
        "fee_url": (
            "https://www.sietk.org/AICTE/2026-27.pdf"
        )
    },

    "Mohan Babu University": {
        "fee_structure": (
            "Official university fee documents list B.Tech "
            "programme-wise fees. The published 2024-25 MBU quota "
            "schedule lists CSE and several related programmes "
            "with total fees of Rs. 10,00,000, paid year-wise as "
            "Rs. 2,25,000, Rs. 2,50,000, Rs. 2,75,000 and "
            "Rs. 2,50,000. These are historical published figures; "
            "they must not be assumed to apply to every quota or "
            "the 2026-27 admission year. Confirm the latest "
            "programme-wise fee schedule with the university."
        ),
        "fee_url": (
            "https://www.mbu.asia/wp-content/uploads/2024/10/"
            "Fee-Structure-for-all-Courses-running-by-MBU-MBU-Quota-seats.pdf"
        )
    },

    "Ashoka Women's Engineering College": {
        "fee_structure": (
            "The latest publicly reported 2025-26 fee information "
            "lists total B.Tech fees of Rs. 2,10,000 for the "
            "four-year programme and Rs. 1,70,000 for lateral-entry "
            "B.Tech. These figures are secondary-source information, "
            "not a confirmed 2026-27 official fee notification. "
            "Confirm the current amount and applicable admission "
            "category directly with the college."
        ),
        "fee_url": "https://www.ashokacollege.in/"
    },

    "G. Pullaiah College of Engineering and Technology": {
        "fee_structure": (
            "The official college admission page lists B.Tech "
            "tuition at Rs. 60,900 per year. The page also describes "
            "the AP EAPCET and management admission categories. "
            "Confirm whether this amount remains applicable to "
            "the 2026-27 admission cycle and whether additional "
            "charges apply."
        ),
        "fee_url": (
            "https://www.gpcet.ac.in/admissionprocedure/"
        )
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
            f"campus_ai_fee_batch4_backup_{timestamp}.json"
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
        print("FEE UPDATE BATCH 4 COMPLETED")
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