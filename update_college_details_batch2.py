"""
CampusAI verified college update - Batch 2
Updates only empty fields for colleges with official programme/admission sources.
Does not invent fees, placements, facilities, or contact details.
"""
from pymongo import MongoClient
from datetime import datetime
import json
from pathlib import Path

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "campus_ai"
COLLECTION = "colleges"

# Each programme list is taken from the linked institution programme page.
# Existing non-empty course lists and other specific data are preserved.
UPDATES = {
    "VIT-AP University": {
        "courses": [
            "B.Tech Biotechnology",
            "B.Tech Computer Science and Engineering",
            "B.Tech CSE (Artificial Intelligence and Machine Learning)",
            "B.Tech CSE (Blockchain)",
            "B.Tech Computer Science and Business Systems",
            "B.Tech CSE (Cyber Security)",
            "B.Tech CSE (Data Analytics)",
            "B.Tech CSE (Software Engineering)",
            "B.Tech Electrical and Electronics Engineering",
            "B.Tech Electronics and Communication Engineering",
            "B.Tech ECE (Embedded Systems)",
            "B.Tech ECE (VLSI)",
            "B.Tech Electronics and Computer Engineering",
            "B.Tech Mechanical Engineering",
            "B.Tech Mechanical Engineering (Automotive Design)",
            "B.Tech Mechanical Engineering (Robotics)"
        ],
        "admission_info": "Refer to the official VIT-AP admissions portal for the current admission route, eligibility, application dates and programme availability. Confirm the applicable year before applying.",
        "admission_url": "https://vit.ac.in/ap-2",
        "data_sources": {
            "courses": "https://vit.ac.in/ap-2",
            "admission_info": "https://vit.ac.in/ap-2"
        }
    },
    "SRM University-AP": {
        "courses": [
            "B.Tech Computer Science and Engineering",
            "B.Tech Electronics and Communication Engineering",
            "B.Tech Electrical and Electronics Engineering",
            "B.Tech Mechanical Engineering",
            "B.Tech Civil Engineering",
            "B.Tech Health Engineering",
            "B.Tech Defence Engineering",
            "B.Tech Energy Engineering",
            "B.Tech Semiconductor Engineering",
            "B.Tech Artificial Intelligence",
            "B.Tech Quantum Computing and Engineering"
        ],
        "admission_info": "Refer to the official SRM University-AP engineering admissions page and current admission booklet for programme-specific eligibility, entrance/admission criteria, tuition fees and deadlines.",
        "admission_url": "https://www.srmap.edu.in/admission/engineering/",
        "data_sources": {
            "courses": "https://www.srmap.edu.in/admission/",
            "admission_info": "https://www.srmap.edu.in/admission/engineering/"
        }
    },
    "IIIT Sri City": {
        "courses": [
            "B.Tech Computer Science and Engineering",
            "B.Tech Electronics and Communication Engineering",
            "B.Tech Artificial Intelligence and Data Science"
        ],
        "admission_info": "Refer to the institute's official admissions page and current JoSAA/CSAB or other applicable official counselling notices for the current admission route and eligibility.",
        "admission_url": "https://iiits.ac.in/",
        "data_sources": {
            "courses": "https://iiits.ac.in/academics/b-tech-programme/regulations/",
            "admission_info": "https://iiits.ac.in/"
        }
    },
    "VIT Vellore": {
        "courses": [
            "B.Tech Biotechnology",
            "B.Tech Chemical Engineering",
            "B.Tech Civil Engineering",
            "B.Tech Computer Science and Engineering",
            "B.Tech CSE (Artificial Intelligence and Machine Learning)",
            "B.Tech CSE (Artificial Intelligence and Data Engineering)",
            "B.Tech CSE (Bioinformatics)",
            "B.Tech CSE and Business Systems",
            "B.Tech CSE (Cyber Security)",
            "B.Tech CSE (Data Science)",
            "B.Tech Electrical and Electronics Engineering",
            "B.Tech Electronics and Communication Engineering",
            "B.Tech Electronics and Instrumentation Engineering",
            "B.Tech Information Technology",
            "B.Tech Mechanical Engineering"
        ],
        "admission_info": "Refer to the official VIT UG admissions portal for the current VITEEE process, eligibility, programme availability, fee category and deadlines.",
        "admission_url": "https://vit.ac.in/admissions/undergraduate",
        "data_sources": {
            "courses": "https://vit.ac.in/engineering-programmes-vellore-campus",
            "admission_info": "https://vit.ac.in/admissions/programmes-offered"
        }
    }
}

def is_empty(value):
    return value is None or value == "" or value == []

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
client.admin.command("ping")
collection = client[DB_NAME][COLLECTION]

documents = list(collection.find({}))
backup_path = Path.cwd() / f"campus_ai_colleges_before_batch2_{datetime.now():%Y%m%d_%H%M%S}.json"
with backup_path.open("w", encoding="utf-8") as f:
    json.dump(documents, f, ensure_ascii=False, indent=2, default=str)

changed = 0
matched = 0

for college_name, info in UPDATES.items():
    doc = collection.find_one({"college_name": college_name})
    if not doc:
        print(f"NOT FOUND: {college_name}")
        continue

    matched += 1
    set_fields = {}

    if is_empty(doc.get("courses")):
        set_fields["courses"] = info["courses"]

    for key in ("admission_info", "admission_url"):
        if is_empty(doc.get(key)):
            set_fields[key] = info[key]

    # Merge source URLs without discarding existing source entries.
    existing_sources = doc.get("data_sources") or {}
    if not isinstance(existing_sources, dict):
        existing_sources = {}
    merged_sources = dict(existing_sources)
    for key, url in info["data_sources"].items():
        merged_sources.setdefault(key, url)
    if merged_sources != existing_sources:
        set_fields["data_sources"] = merged_sources

    set_fields["data_verified_on"] = datetime.now().strftime("%Y-%m-%d")
    set_fields["data_verification_note"] = (
        "Programme/admission links checked against official institution sources. "
        "Existing non-empty fields preserved; fees and placement figures were not guessed."
    )

    if set_fields:
        collection.update_one({"_id": doc["_id"]}, {"$set": set_fields})
        changed += 1
        print(f"UPDATED: {college_name}")
    else:
        print(f"NO CHANGE NEEDED: {college_name}")

print("\nCampusAI Batch 2 update finished.")
print(f"Total college records in database: {len(documents)}")
print(f"Batch 2 colleges found: {matched}/{len(UPDATES)}")
print(f"College documents updated: {changed}")
print(f"Backup: {backup_path}")
print("Fees, placement statistics, facilities and contacts were not invented.")
client.close()
