"""
CampusAI: safe official-website sync for the 39 colleges.

This script:
1. Connects to mongodb://localhost:27017/
2. Backs up the current campus_ai.colleges collection to a timestamped JSON file.
3. Updates ONLY official website URLs for matching college records.
4. Does not overwrite courses, fees, admissions, placements, contacts, or other data.

Run from your AI_Campus_Assistant folder:
    python update_colleges.py

If your MongoDB URI/database/collection differ, edit the three settings below.
"""

from datetime import datetime, timezone
from pathlib import Path
import json
from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "campus_ai"
COLLECTION_NAME = "colleges"

OFFICIAL_WEBSITES = {
    "K.S.R.M. College of Engineering": "https://ksrmce.ac.in/",
    "JNTUA College of Engineering": "https://www.jntua.ac.in/",
    "JNTUA College of Engineering, Pulivendula": "https://www.jntua.ac.in/",
    "JNTUA College of Engineering, Kalikiri": "https://www.jntua.ac.in/",
    "Annamacharya Institute of Technology and Sciences": "https://aitsrajampet.ac.in/",
    "Madanapalle Institute of Technology and Science": "https://mits.ac.in/",
    "VIT-AP University": "https://vitap.ac.in/",
    "KL University": "https://www.kluniversity.in/",
    "SRM University-AP": "https://www.srmap.edu.in/",
    "JNTU Kakinada": "https://jntuk.edu.in/",
    "IIIT Sri City": "https://www.iiits.ac.in/",
    "RV College of Engineering": "https://rvce.edu.in/",
    "BMS College of Engineering": "https://www.bmsce.ac.in/",
    "PES University": "https://pes.edu/",
    "Ramaiah Institute of Technology": "https://www.msrit.edu/",
    "Bangalore Institute of Technology": "https://bit-bangalore.edu.in/",
    "Dayananda Sagar College of Engineering": "https://www.dsce.edu.in/",
    "Nitte Meenakshi Institute of Technology": "https://www.nmit.ac.in/",
    "VIT Vellore": "https://vit.ac.in/",
    "Sri Venkateswara College of Engineering and Technology": "https://www.svcet.edu.in/",
    "Viswam Engineering College": "https://viswam.ac.in/",
    "Siddharth Institute of Engineering and Technology": "https://www.sietk.org/",
    "Mohan Babu University": "https://mbu.asia/",
    "Ashoka Women's Engineering College": "https://www.ashokacollege.in/",
    "G. Pulla Reddy Engineering College": "https://www.gprec.ac.in/",
    "G. Pullaiah College of Engineering and Technology": "https://www.gpcet.ac.in/",
    "Dr. K. V. Subba Reddy Institute of Technology": "https://www.kvsr.ac.in/",
    "Ravindra College of Engineering for Women": "https://www.recw.ac.in/",
    "St. John's College of Engineering and Technology": "https://sjcet.ac.in/",
    "Geethanjali College of Engineering and Technology": "https://www.geethanjaliinstitutions.com/",
    "Rajeev Gandhi Memorial College of Engineering and Technology": "https://www.rgmcet.edu.in/",
    "Santhiram Engineering College": "https://www.srecnandyal.edu.in/",
    "IIIT RK Valley (Idupulapaya)": "https://www.rgukt.in/",
    "IIIT Srikakulam (Etcherla)": "https://www.rgukt.in/",
    "IIIT Nuzvid": "https://www.rgukt.in/",
    "Aditya College of Engineering": "https://acet.ac.in/",
    "Sreenivasa Institute of Technology and Management Studies (SITAMS)": "https://sitams.ac.in/",
    "GITAM Deemed to be University - Bengaluru Campus": "https://www.gitam.edu/",
    "Mother Theresa Institute of Engineering and Technology": "https://mtieat.org/",
}

def json_safe(value):
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [json_safe(v) for v in value]
    try:
        from bson import ObjectId
        if isinstance(value, ObjectId):
            return str(value)
    except Exception:
        pass
    return value

def main():
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    collection = client[DATABASE_NAME][COLLECTION_NAME]

    records = list(collection.find({}))
    if not records:
        print("No records found. Check database and collection names.")
        return

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = Path.cwd() / f"campus_ai_colleges_backup_{stamp}.json"
    with backup_path.open("w", encoding="utf-8") as f:
        json.dump([json_safe(doc) for doc in records], f, ensure_ascii=False, indent=2)

    updated = 0
    missing = []
    for college_name, website in OFFICIAL_WEBSITES.items():
        result = collection.update_one(
            {"college_name": college_name},
            {"$set": {"website": website}}
        )
        if result.matched_count:
            updated += result.modified_count
        else:
            missing.append(college_name)

    print("\nCampusAI website sync finished.")
    print(f"College records found before update: {len(records)}")
    print(f"Website entries in script: {len(OFFICIAL_WEBSITES)}")
    print(f"Records whose website value changed: {updated}")
    print(f"Backup saved to: {backup_path}")
    if missing:
        print("\nNames not matched (check spelling in MongoDB):")
        for name in missing:
            print("-", name)
    print("\nNote: This script updates official website URLs only.")
    print("It does NOT invent or populate unverified fees, eligibility, or placement statistics.")
    client.close()

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("\nERROR:", exc)
        print("Check that MongoDB is running and the database/collection names are correct.")
