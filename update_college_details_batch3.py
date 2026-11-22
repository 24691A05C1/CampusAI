"""
CampusAI verified college update - Batch 3.
Only adds official-source programme/admission details where fields are empty.
Creates a JSON backup and preserves existing non-empty values.
"""
from pymongo import MongoClient
from datetime import datetime
from pathlib import Path
import json

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "campus_ai"
COLLECTION = "colleges"

UPDATES = {
    "JNTU Kakinada": {
        "courses": [
            "B.Tech Civil Engineering",
            "B.Tech Electrical and Electronics Engineering",
            "B.Tech Mechanical Engineering",
            "B.Tech Electronics and Communication Engineering",
            "B.Tech Computer Science and Engineering",
            "B.Tech Petroleum Engineering",
            "B.Tech Chemical Engineering",
            "B.Tech Petrochemical Engineering"
        ],
        "admission_info": "The university's official academics page states that regular B.Tech admissions are based on AP EAPCET rank. Confirm current-year eligibility, seat allocation and counselling dates through APSCHE and the university.",
        "admission_url": "https://jntuk.edu.in/academics",
        "data_sources": {
            "courses": "https://jntuk.edu.in/academics",
            "admission_info": "https://jntuk.edu.in/academics"
        }
    },
    "RV College of Engineering": {
        "courses": [
            "B.E. Civil Engineering",
            "B.E. Mechanical Engineering",
            "B.E. Electrical and Electronics Engineering",
            "B.E. Electronics and Communication Engineering",
            "B.E. Industrial Engineering and Management",
            "B.E. Electronics and Instrumentation Engineering",
            "B.E. Chemical Engineering",
            "B.E. Computer Science and Engineering",
            "B.E. Electronics and Telecommunication Engineering",
            "B.E. Information Science and Engineering",
            "B.E. Biotechnology",
            "B.E. Aerospace Engineering",
            "B.E. Computer Science and Engineering (Artificial Intelligence and Machine Learning)",
            "B.E. Computer Science and Engineering (Data Science)",
            "B.E. Computer Science and Engineering (Cyber Security)"
        ],
        "admission_info": "Check the official RVCE admissions page for current-year eligibility, entrance route, seat categories and application details. Admission routes and requirements can vary by seat type.",
        "admission_url": "https://rvce.edu.in/admissions",
        "data_sources": {
            "courses": "https://rvce.edu.in/sites/default/files/ug-rulebook-2021-guidelines.pdf",
            "admission_info": "https://rvce.edu.in/admissions"
        }
    },
    "BMS College of Engineering": {
        "courses": [
            "B.E. Civil Engineering",
            "B.E. Mechanical Engineering",
            "B.E. Electrical and Electronics Engineering",
            "B.E. Electronics and Communication Engineering",
            "B.E. Industrial Engineering and Management",
            "B.E. Computer Science and Engineering",
            "B.E. Biotechnology",
            "B.E. Chemical Engineering",
            "B.E. Artificial Intelligence and Machine Learning",
            "B.E. Computer Science and Engineering (Data Science)",
            "B.E. Computer Science and Engineering (Internet of Things and Cyber Security including Blockchain Technology)",
            "B.E. Artificial Intelligence and Data Science"
        ],
        "admission_info": "Refer to the official BMSCE admissions information for current-year eligibility, entrance exam requirements, seat categories and application dates.",
        "admission_url": "https://bmsce.ac.in/home/Under-Graduation",
        "data_sources": {
            "courses": "https://bmsce.ac.in/home/Under-Graduation",
            "admission_info": "https://bmsce.ac.in/home/Under-Graduation"
        }
    }
}

def empty(value):
    return value is None or value == "" or value == []

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
client.admin.command("ping")
col = client[DB_NAME][COLLECTION]
docs = list(col.find({}))

backup = Path.cwd() / f"campus_ai_colleges_before_batch3_{datetime.now():%Y%m%d_%H%M%S}.json"
with backup.open("w", encoding="utf-8") as f:
    json.dump(docs, f, ensure_ascii=False, indent=2, default=str)

found = changed = 0
for name, info in UPDATES.items():
    doc = col.find_one({"college_name": name})
    if not doc:
        print(f"NOT FOUND: {name}")
        continue
    found += 1
    fields = {}
    if empty(doc.get("courses")):
        fields["courses"] = info["courses"]
    for key in ("admission_info", "admission_url"):
        if empty(doc.get(key)):
            fields[key] = info[key]

    sources = doc.get("data_sources") or {}
    if not isinstance(sources, dict):
        sources = {}
    merged = dict(sources)
    for key, value in info["data_sources"].items():
        merged.setdefault(key, value)
    if merged != sources:
        fields["data_sources"] = merged

    fields["data_verified_on"] = datetime.now().strftime("%Y-%m-%d")
    fields["data_verification_note"] = (
        "Course and admission references recorded from official institution pages/documents. "
        "Existing non-empty values preserved; fees and placement figures were not guessed."
    )
    col.update_one({"_id": doc["_id"]}, {"$set": fields})
    changed += 1
    print(f"UPDATED: {name}")

print("\nCampusAI Batch 3 update finished.")
print(f"Total college records: {len(docs)}")
print(f"Batch 3 colleges found: {found}/{len(UPDATES)}")
print(f"College documents processed: {changed}")
print(f"Backup: {backup}")
print("Fees, placement figures, facilities and contact details were not invented.")
client.close()
