from pymongo import MongoClient
from datetime import datetime
from pathlib import Path
import json

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "campus_ai"
COLLECTION = "colleges"


UPDATES = {

    "Nitte Meenakshi Institute of Technology": {
        "placement_info": (
            "According to the official placement page, NMIT reported "
            "863 students placed out of 1,024 eligible students during "
            "the 2025-26 placement season, with 1,263 offers and "
            "234 recruiters. The reported average salary was Rs. 5.75 LPA, "
            "median salary Rs. 5.40 LPA and highest salary Rs. 37.60 LPA. "
            "For 2024-25, 831 students were placed out of 1,000 eligible "
            "students. Figures are institution-reported and batch-specific."
        ),
        "placement_url": "https://nitte.edu.in/nmit/placement.php"
    },

    "Sri Venkateswara College of Engineering and Technology": {
        "placement_info": (
            "The college provides career guidance and placement-related "
            "support through its institutional activities. Students should "
            "check the official college website or contact the placement "
            "department for the latest branch-wise placement records, "
            "recruiter list, eligible student count and salary details. "
            "A reliable current consolidated placement percentage and "
            "salary figure could not be confirmed."
        ),
        "placement_url": "https://www.svcet.edu.in/"
    },

    "Siddharth Institute of Engineering and Technology": {
        "placement_info": (
            "According to the institute's mandatory disclosure, "
            "936 UG students were placed out of 1,039 outgoing students "
            "in 2024-25. For the same year, 85 PG students were placed "
            "out of 111 outgoing students. The disclosure also reports "
            "932 UG placements in 2023-24 and 638 in 2022-23. "
            "These are historical institutional figures, not a guarantee "
            "of future placement outcomes."
        ),
        "placement_url": (
            "https://sietk.org/files/Mandatory%20Disclosures.pdf"
        )
    },

    "G. Pullaiah College of Engineering and Technology": {
        "placement_info": (
            "GPCET has a dedicated Placement and Training Department "
            "that supports internships, recruitment preparation, "
            "industry interaction and employability development. "
            "The official placement records publish student selections "
            "and company-wise CTC details for different graduating years. "
            "Students should refer to the official placement record for "
            "the relevant batch rather than relying on a single package "
            "figure as a general placement guarantee."
        ),
        "placement_url": "https://www.gpcet.ac.in/placement-record/"
    },

    "Dr. K. V. Subba Reddy Institute of Technology": {
        "placement_info": (
            "The institute provides placement and career-related support "
            "for engineering students. Students should contact the "
            "institution's placement department for current recruiter "
            "details, branch-wise placement outcomes, eligible student "
            "counts and salary information. A reliable current "
            "consolidated placement percentage and salary figure "
            "could not be confirmed from the available official information."
        ),
        "placement_url": "https://www.kvsr.ac.in/"
    },

    "Ravindra College of Engineering for Women": {
        "placement_info": (
            "The official college placement page states that 90% of "
            "eligible students are placed. The website also provides "
            "historical placed-student records, including company names, "
            "branches and CTC information for earlier graduating batches. "
            "The 90% figure is an institution-published claim and should "
            "not be interpreted as a verified placement rate for every "
            "individual batch."
        ),
        "placement_url": "https://www.recw.ac.in/placed-students/"
    },

    "St. John's College of Engineering and Technology": {
        "placement_info": (
            "The college has a Training and Placement Cell that conducts "
            "career guidance, recruitment preparation, communication "
            "skills development and internship-related activities. "
            "Its official website lists recruiters and historical "
            "student placement records. A historical 2020-21 record "
            "reports 75 students placed, an average package of "
            "Rs. 3.60 LPA and a highest package of Rs. 5 LPA. "
            "These figures are not current placement statistics."
        ),
        "placement_url": "https://sjcet.ac.in/placement.php"
    },

    "Geethanjali College of Engineering and Technology": {
        "placement_info": (
            "The college's placement and training activities should be "
            "checked through its official engineering institution "
            "website. Students should confirm current placement records, "
            "recruiter participation, branch-wise selections and salary "
            "figures directly with the placement department. "
            "A reliable current consolidated placement percentage "
            "and salary figure could not be confirmed."
        ),
        "placement_url": (
            "https://www.geethanjaliinstitutions.com/"
        )
    },

    "Rajeev Gandhi Memorial College of Engineering and Technology": {
        "placement_info": (
            "According to the college's official website, its "
            "2025-26 placement updates report 597 placements across "
            "listed recruiters and companies. The website also displays "
            "ongoing 2026-27 placement activity. These figures represent "
            "the college's published placement updates and should be "
            "checked against the latest batch-wise records."
        ),
        "placement_url": "https://www.rgmcet.edu.in/"
    },

    "Santhiram Engineering College": {
        "placement_info": (
            "According to the official placement records, the college "
            "reported 347 placements in 2024-25, with an average package "
            "of Rs. 3.58 LPA and highest package of Rs. 4.25 LPA. "
            "For 2023-24, it reported 289 placements, an average package "
            "of Rs. 4.44 LPA and highest package of Rs. 7 LPA. "
            "The website also provides company-wise and branch-wise "
            "placement details. These figures are historical."
        ),
        "placement_url": (
            "https://srecnandyal.edu.in/Placement_Records.php"
        )
    },

    "IIIT RK Valley (Idupulapaya)": {
        "placement_info": (
            "RGUKT operates a Career Development and Placement Cell "
            "that supports internships, campus recruitment, employability "
            "training and career guidance. Its official information "
            "brochure lists a campus placement contact for RK Valley. "
            "A current independently confirmed campus-specific "
            "placement percentage and salary summary was not established. "
            "Students should contact the RK Valley placement cell for "
            "the latest batch-wise figures."
        ),
        "placement_url": "https://rgukt.in/contact-directory/"
    },

    "IIIT Srikakulam (Etcherla)": {
        "placement_info": (
            "RGUKT provides Career Development and Placement Cell "
            "support across its campuses, including internship "
            "opportunities, recruitment preparation, soft-skills "
            "training and career guidance. A current independently "
            "confirmed Srikakulam campus-specific placement percentage "
            "and salary summary was not established. Students should "
            "contact the campus administration for the latest figures."
        ),
        "placement_url": "https://rgukt.in/contact-directory/"
    },

    "IIIT Nuzvid": {
        "placement_info": (
            "RGUKT provides Career Development and Placement Cell "
            "support for internships, campus recruitment, employability "
            "training and career guidance. A historical RGUKT information "
            "brochure lists a placement contact for Nuzvid campus. "
            "A current independently confirmed Nuzvid-specific "
            "placement percentage and salary summary was not established. "
            "Students should contact the campus placement department "
            "for the latest batch-wise results."
        ),
        "placement_url": "https://rgukt.in/contact-directory/"
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
            f"campus_ai_placement_batch3_backup_{timestamp}.json"
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
        not_found = 0

        for name, details in UPDATES.items():

            college = collection.find_one({
                "college_name": name
            })

            if not college:
                print("NOT FOUND:", name)
                not_found += 1
                continue

            changes = {}

            if is_missing(college.get("placement_info")):
                changes["placement_info"] = details["placement_info"]

            if is_missing(college.get("placement_url")):
                changes["placement_url"] = details["placement_url"]

            existing_sources = college.get("data_sources", {})

            if not isinstance(existing_sources, dict):
                existing_sources = {}

            new_sources = dict(existing_sources)
            new_sources["placements"] = details["placement_url"]

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
        print("PLACEMENT UPDATE BATCH 3 COMPLETED")
        print("================================")
        print("Total colleges:", len(colleges))
        print("Colleges covered:", len(UPDATES))
        print("Colleges updated:", updated)
        print("Colleges not found:", not_found)
        print("Backup:", backup_file)

    except Exception as error:
        print("ERROR:", error)

    finally:
        client.close()
        print("MongoDB connection closed.")


if __name__ == "__main__":
    main()