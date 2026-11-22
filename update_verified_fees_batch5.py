from pymongo import MongoClient
from datetime import datetime
from pathlib import Path
import json

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "campus_ai"
COLLECTION = "colleges"

UPDATES = {

    "Dr. K. V. Subba Reddy Institute of Technology": {
        "fee_structure": (
            "The official college fee page publishes B.Tech fees "
            "by branch and admission category. The listed EAMCET "
            "convener tuition is Rs. 45,700 per year plus Rs. 2,500 "
            "university fee. Management-category tuition varies by "
            "branch, with published amounts ranging from Rs. 50,700 "
            "to Rs. 1,20,000 per year, plus university fee. "
            "Confirm the applicable 2026-27 amount with the college."
        ),
        "fee_url": (
            "https://www.drkvsrit.ac.in/fee-structure/index.html"
        )
    },

    "Ravindra College of Engineering for Women": {
        "fee_structure": (
            "The official fee page lists convener-seat tuition "
            "of Rs. 43,000 per year for the displayed B.Tech "
            "programmes. Category-B fees vary by branch: the "
            "published table lists Rs. 1,29,000 for CSE and "
            "CSE (Artificial Intelligence), and Rs. 60,000 for "
            "ECE. The page was published in April 2025. "
            "Confirm the applicable 2026-27 fees before admission."
        ),
        "fee_url": "https://www.recw.ac.in/fee-structure/"
    },

    "St. John's College of Engineering and Technology": {
        "fee_structure": (
            "A complete current official programme-wise B.Tech "
            "fee schedule could not be confirmed from the available "
            "official information. Fees may depend on AP EAPCET "
            "convener admission or management admission. Students "
            "should obtain the applicable 2026-27 fee notification "
            "from the college before payment. No unverified amount "
            "has been assumed."
        ),
        "fee_url": "https://sjcet.ac.in/"
    },

    "Geethanjali College of Engineering and Technology": {
        "fee_structure": (
            "A current official 2026-27 B.Tech fee schedule was "
            "not confirmed from the available official source. "
            "The applicable amount may differ between convener "
            "and management categories. Contact the institution "
            "for the latest approved B.Tech tuition and additional "
            "charges. Do not confuse hostel fees or pharmacy "
            "programme fees with engineering tuition."
        ),
        "fee_url": (
            "https://www.geethanjaliinstitutions.com/"
        )
    },

    "Rajeev Gandhi Memorial College of Engineering and Technology": {
        "fee_structure": (
            "The official APHERMC fee document for 2023-24 lists "
            "annual B.Tech tuition of Rs. 46,200 for RGMCET "
            "(counselling code RGIT). This is a historical "
            "government fee reference and must not be treated "
            "as the confirmed 2026-27 amount. Current fees may "
            "differ by admission category and government orders."
        ),
        "fee_url": (
            "https://www.rgmcet.edu.in/assets/img/documents/"
            "Fee%20Structure/B.TECH-FEE-2023-24.pdf"
        )
    },

    "Santhiram Engineering College": {
        "fee_structure": (
            "The college's official admissions page confirms "
            "Category-A admissions through AP EAPCET counselling "
            "and Category-B management admissions. A complete "
            "current 2026-27 B.Tech fee schedule was not confirmed "
            "from the official page. Obtain the applicable fee "
            "details directly from the college. No unverified "
            "tuition amount has been inserted."
        ),
        "fee_url": (
            "https://srecnandyal.edu.in/Admissions.php"
        )
    },

    "IIIT RK Valley (Idupulapaya)": {
        "fee_structure": (
            "RGUKT Andhra Pradesh operates a six-year integrated "
            "programme consisting of two years of pre-university "
            "study followed by four years of engineering. Fees "
            "depend on student eligibility, scholarship status "
            "and the applicable academic-year circular. The "
            "university's 2026-27 fee amount for this campus "
            "should be confirmed through its latest official "
            "fee notification. Do not apply ordinary four-year "
            "B.Tech college fee assumptions."
        ),
        "fee_url": "https://rgukt.in/"
    },

    "IIIT Srikakulam (Etcherla)": {
        "fee_structure": (
            "RGUKT Srikakulam follows the university's six-year "
            "integrated programme: two years of pre-university "
            "education followed by four years of engineering. "
            "The applicable tuition and other charges depend on "
            "the academic-year fee circular and scholarship "
            "eligibility. Confirm the 2026-27 amount with the "
            "official university before admission."
        ),
        "fee_url": "https://rgukt.in/"
    },

    "IIIT Nuzvid": {
        "fee_structure": (
            "RGUKT Nuzvid follows a six-year integrated programme "
            "with two years of pre-university education and four "
            "years of engineering. Its official website published "
            "a 2026-27 tuition-fee circular for students not "
            "eligible for government scholarships. The circular "
            "requires payment but the amount must be checked "
            "against the applicable individual fee assessment. "
            "Scholarship eligibility affects the payable amount."
        ),
        "fee_url": (
            "https://rguktn.ac.in/downloads/"
            "Tution_Fee_Circular_APL_Students_07102026_AY2026-2027.pdf"
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
            f"campus_ai_fee_batch5_backup_{timestamp}.json"
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
        print("FEE UPDATE BATCH 5 COMPLETED")
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