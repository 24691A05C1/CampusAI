from pymongo import MongoClient
from datetime import datetime
from pathlib import Path
import json

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "campus_ai"
COLLECTION = "colleges"

UPDATES = {
    "JNTUA College of Engineering, Pulivendula": {
        "fee_structure": (
            "Official college fee page: B.Tech tuition fee is Rs. 10,000 "
            "per year. First-year special fee is Rs. 6,400 and hostel "
            "admission fee is Rs. 3,500. From the second year, the listed "
            "special fee is Rs. 2,850 and hostel admission fee is Rs. 2,500. "
            "Examination fee is listed separately as Rs. 1,440. "
            "Fees are stated as per Government norms. Confirm the applicable "
            "academic year and individual fee components with the college."
        ),
        "fee_url": "https://jntuacep.ac.in/academics/fee-structures.php"
    },

    "JNTUA College of Engineering, Kalikiri": {
        "fee_structure": (
            "Official college fee page lists B.Tech convener-seat tuition "
            "at Rs. 10,000 per year. It also lists special fees of Rs. 5,500 "
            "at admission and Rs. 2,500 from the second year onwards. "
            "Hostel admission fee is listed as Rs. 2,400. The page does not "
            "clearly specify the academic year; confirm the latest payable "
            "amount with the college."
        ),
        "fee_url": "https://www.jntuacek.ac.in/fee-structure-2/"
    },

    "SRM University-AP": {
        "fee_structure": (
            "Official B.Tech tuition fee page lists annual tuition by "
            "programme. CSE: Rs. 4,00,000; CSE with AI and ML: Rs. 4,00,000; "
            "CSE with Big Data Analytics, Cyber Security, Distributed and "
            "Cloud Computing, or IoT: Rs. 3,60,000; ECE, Mechanical, "
            "Electrical and Electronics, and Civil Engineering: "
            "Rs. 2,50,000. Other specialised programmes have separate fees. "
            "Additional charges: one-time registration fee Rs. 10,000 and "
            "refundable academic caution deposit Rs. 5,000. The university "
            "states that fees are indicative and subject to revision. "
            "Check the official page for the chosen programme."
        ),
        "fee_url": "https://www.srmap.edu.in/admission/seas-btech-tuition-fee/"
    },

    "BMS College of Engineering": {
        "fee_structure": (
            "Official 2026-27 approved management-quota B.E. fee per annum: "
            "Civil Rs. 6 lakh; Electrical and Electronics Rs. 6 lakh; "
            "Industrial Engineering and Management Rs. 6 lakh; "
            "Electronics and Communication Rs. 9 lakh; Mechanical Rs. 6 lakh; "
            "Computer Science and Engineering Rs. 15 lakh; Chemical "
            "Engineering Rs. 4 lakh; Biotechnology Rs. 7 lakh; "
            "AI and ML Rs. 12.5 lakh; AI and Data Science Rs. 12 lakh; "
            "CSE Data Science Rs. 12 lakh; CSE IoT and Cyber Security "
            "Rs. 12 lakh; Computer Science and Business Systems Rs. 10 lakh. "
            "These are management-quota figures only. Hostel fees are extra. "
            "Do not use these amounts for CET or COMEDK seats."
        ),
        "fee_url": "https://www.bmsce.ac.in/home/Under-Graduation"
    },

    "Nitte Meenakshi Institute of Technology": {
        "fee_structure": (
            "Official B.Tech annual fee structure for 2026-27 through "
            "NUCAT 2026. General-category fees by programme: Aeronautical "
            "Rs. 2,75,000; AI and Data Science Rs. 4,00,000; AI and ML "
            "Rs. 4,50,000; Civil Rs. 1,75,000; Computer Science "
            "Rs. 4,50,000; Computer Science and Business Systems "
            "Rs. 3,25,000; Electrical and Electronics Rs. 1,75,000; "
            "Electronics and Communication Rs. 3,00,000; VLSI Design "
            "Rs. 2,50,000; Information Science Rs. 4,50,000; Mechanical "
            "Rs. 1,75,000; Robotics and AI Rs. 3,50,000. Scholarship and "
            "NRI categories have different fees. Annual examination fee "
            "is Rs. 10,000. Refer to the official PDF for all categories."
        ),
        "fee_url": "https://nitte.edu.in/nmit/pdf/NMIT_BTech.pdf"
    },

    "VIT Vellore": {
        "fee_structure": (
            "Official VIT 2026-27 B.Tech academic fee structure uses "
            "programme groups and scholarship categories. Annual tuition: "
            "Group A - Category 0 Rs. 0, Category 1 Rs. 1,73,000, "
            "Category 2 Rs. 2,32,000, Category 3 Rs. 3,40,000, "
            "Category 4 Rs. 3,65,000, Category 5 Rs. 3,95,000. "
            "Group B - Category 0 Rs. 0, Category 1 Rs. 1,95,000, "
            "Category 2 Rs. 3,04,000, Category 3 Rs. 4,02,000, "
            "Category 4 Rs. 4,45,000, Category 5 Rs. 4,90,000. "
            "Group C - Category 0 Rs. 0, Category 1 Rs. 2,07,000, "
            "Category 2 Rs. 2,66,000, Category 3 Rs. 3,74,000, "
            "Category 4 Rs. 3,99,000, Category 5 Rs. 4,29,000. "
            "A refundable one-time caution deposit of Rs. 5,000 applies. "
            "The category depends on the programme and admission allotment. "
            "Check the official fee page before quoting a student's fee."
        ),
        "fee_url": "https://vit.ac.in/admission/ug/fee-structure"
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
            f"campus_ai_fee_batch1_backup_{timestamp}.json"
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

            for field in ("fee_structure", "fee_url"):
                value = details[field]

                if is_missing(college.get(field)):
                    changes[field] = value

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
        print("FEE UPDATE BATCH 1 COMPLETED")
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