from pymongo import MongoClient
from datetime import datetime
from pathlib import Path
import json

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "campus_ai"
COLLECTION = "colleges"

UPDATES = {

    "K.S.R.M. College of Engineering": {
        "fee_structure": (
            "The official college fee page lists annual B.Tech fees: "
            "CSE Rs. 1,15,000; ECE Rs. 1,15,000; EEE Rs. 1,10,000; "
            "Civil Rs. 1,10,000; Mechanical Rs. 1,10,000. "
            "CSE Data Science and CSE AI & ML are listed at Rs. 1,25,000 "
            "per year. Admission fee is Rs. 5,000. Fees are subject to "
            "revision by APSCHE and the university. Confirm the current "
            "academic year's applicable fee with the college."
        ),
        "fee_url": "https://www.ksrmce.ac.in/academics/fee-structure"
    },

    "Madanapalle Institute of Technology and Science": {
        "fee_structure": (
            "Official fee structure for AY 2026-27. B.Tech fees are "
            "listed per semester and vary by programme and scholarship. "
            "Civil, Mechanical and EEE base fee: Rs. 50,000 per semester. "
            "CSE and ECE base fee: Rs. 99,000 per semester. "
            "CSE AI & Data Science, AI & ML and Cyber Security base fee: "
            "Rs. 1,25,000 per semester. Eligible students may receive "
            "scholarship-based reductions. Final fees depend on the "
            "published eligibility criteria."
        ),
        "fee_url": "https://mits.ac.in/scholarship-fees"
    },

    "Annamacharya Institute of Technology and Sciences": {
        "fee_structure": (
            "The official institutional disclosure contains historical "
            "B.Tech fee details for AY 2022-23. It lists A-category "
            "tuition at Rs. 68,700 per year for the listed UG programmes. "
            "B-category figures vary by branch: Civil, EEE and Mechanical "
            "Rs. 90,000; ECE Rs. 1,50,000; CSE, AI & DS and AI & ML "
            "Rs. 1,90,000 per year. These are historical figures, not "
            "confirmed current fees. Contact the college for the latest "
            "AP EAPCET and management-quota fee structure."
        ),
        "fee_url": "https://aitsrajampet.ac.in/pdf/Academic-Infrastructure-Instructional-Details-min.pdf"
    },

    "JNTUA College of Engineering": {
        "fee_structure": (
            "The official college fee page states that students pay "
            "tuition and other fees as prescribed by the Government "
            "of Andhra Pradesh. Eligible students may receive government "
            "ePASS scholarships. The website provides a B.Tech fee "
            "document for the 2019-20 admitted batch, which is historical. "
            "A current numeric fee amount was not confirmed. Contact the "
            "college or check the latest government counselling notice "
            "for the applicable amount."
        ),
        "fee_url": "https://jntuacea.ac.in/academics/fees"
    },

    "VIT-AP University": {
        "fee_structure": (
            "The official VIT-AP website provides a Fees and Scholarships "
            "section covering B.Tech and other programmes. The current "
            "public page does not expose a readable programme-wise numeric "
            "B.Tech fee table in the available page text. Therefore, no "
            "unverified amount has been inserted. Students should check "
            "the official fee page and confirm the applicable programme, "
            "admission category and scholarship before payment."
        ),
        "fee_url": "https://www.vitap.ac.in/fees-and-scholarships"
    },

    "KL University": {
        "fee_structure": (
            "KL University's official Annual Report 2022-23 contains "
            "historical Vijayawada-campus B.Tech fee details. It lists "
            "semester tuition fees by programme, including CSE "
            "Rs. 1,30,000 per semester, AI & Data Science "
            "Rs. 1,25,000, IoT Rs. 1,20,000 and ECE Rs. 1,20,000. "
            "A one-time admission fee of Rs. 15,000 is also listed. "
            "These are 2022-23 figures and must not be treated as "
            "current 2026-27 fees. Confirm the latest fee with KL "
            "University admissions."
        ),
        "fee_url": "https://www.kluniversity.in/pdfs/Annual%20Report%202022-23.pdf"
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
            f"campus_ai_fee_batch2_backup_{timestamp}.json"
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
        print("FEE UPDATE BATCH 2 COMPLETED")
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