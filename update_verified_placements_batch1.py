from pymongo import MongoClient
from datetime import datetime
from pathlib import Path
import json

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "campus_ai"
COLLECTION = "colleges"

UPDATES = {

    "JNTUA College of Engineering": {
        "placement_info": (
            "According to the official JNTUA Directorate of "
            "Industrial Relations and Placements report for "
            "academic year 2023-24, JNTUA College of Engineering, "
            "Anantapur reported 166 UG students and 5 PG students "
            "placed, making 171 placed students in total. "
            "The placement office supports campus recruitment, "
            "internships and off-campus opportunities. "
            "These figures are historical and should not be "
            "treated as current-year placement statistics."
        ),
        "placement_url": (
            "https://placements.jntua.ac.in/wp-content/uploads/"
            "2025/03/D-IRAP-JNTUA-Placement-Data-Year-2023-24-2.pdf"
        )
    },

    "JNTUA College of Engineering, Pulivendula": {
        "placement_info": (
            "According to the official JNTUA Directorate of "
            "Industrial Relations and Placements report for "
            "academic year 2023-24, the Pulivendula campus "
            "reported 31 UG students placed out of 307 registered "
            "UG students. The report is a historical placement "
            "record. Current placement outcomes may differ by "
            "branch and graduating batch."
        ),
        "placement_url": (
            "https://placements.jntua.ac.in/wp-content/uploads/"
            "2025/03/D-IRAP-JNTUA-Placement-Data-Year-2023-24-2.pdf"
        )
    },

    "JNTUA College of Engineering, Kalikiri": {
        "placement_info": (
            "According to the official JNTUA Directorate of "
            "Industrial Relations and Placements report for "
            "academic year 2023-24, the Kalikiri campus "
            "reported 105 UG students placed out of 410 "
            "registered UG students. The college also publishes "
            "recruitment information and placement updates "
            "through its Training and Placement section. "
            "These figures are historical."
        ),
        "placement_url": (
            "https://placements.jntua.ac.in/wp-content/uploads/"
            "2025/03/D-IRAP-JNTUA-Placement-Data-Year-2023-24-2.pdf"
        )
    },

    "VIT-AP University": {
        "placement_info": (
            "VIT-AP University has a Career Development Centre "
            "that coordinates campus recruitment, Dream Offers, "
            "Super Dream Offers, internships and industry "
            "collaborations. The official placement section "
            "publishes year-wise offer information and recruiter "
            "updates. Placement outcomes vary by graduating "
            "batch, programme and eligibility. Students should "
            "consult the official placement statistics for "
            "the relevant year rather than assuming a single "
            "university-wide placement percentage."
        ),
        "placement_url": (
            "https://vitap.ac.in/cdc-dream"
        )
    },

    "KL University": {
        "placement_info": (
            "KL University provides placement support through "
            "its career development and training activities. "
            "Its official publications describe campus "
            "recruitment, company participation, placement "
            "training and student achievements. Placement "
            "statistics and salary packages vary by academic "
            "year, programme and student eligibility. "
            "A current consolidated placement percentage "
            "and average package should be confirmed from "
            "the latest official placement report."
        ),
        "placement_url": (
            "https://www.kluniversity.in/"
        )
    },

    "SRM University-AP": {
        "placement_info": (
            "SRM University-AP publishes placement information "
            "through its Directorate of Corporate Relations "
            "and Career Services (CR&CS). Its official placement "
            "page currently highlights a highest CTC of "
            "Rs. 55 LPA, average package of Rs. 9 LPA+, "
            "1,200+ recruitment partners and hiring across "
            "10+ countries. These are university-published "
            "headline figures; they should not be interpreted "
            "as guaranteed salaries or as a branch-specific "
            "placement percentage. Check the official placement "
            "tracker for year-wise details."
        ),
        "placement_url": (
            "https://www.srmap.edu.in/crcs/"
        )
    }
}


def is_missing(value):
    if value is None:
        return True

    if isinstance(value, str):
        return not value.strip()

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
            f"campus_ai_placement_batch1_backup_{timestamp}.json"
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
        print("PLACEMENT UPDATE BATCH 1 COMPLETED")
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