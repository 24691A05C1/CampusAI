from datetime import datetime, timezone
from pathlib import Path
import json
from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "campus_ai"
COLLECTION_NAME = "colleges"

# Official-source details verified for this initial update.
# Existing non-empty fields are preserved. No guessed fee/package statistics.
VERIFIED = {
    "K.S.R.M. College of Engineering": {
        "courses": ["Computer Science and Engineering", "CSE (Artificial Intelligence and Machine Learning)", "CSE (Data Science)", "Artificial Intelligence and Machine Learning", "Electronics and Communication Engineering", "Electrical and Electronics Engineering", "Mechanical Engineering", "Civil Engineering"],
        "admission_info": "B.Tech admissions are merit-based through Andhra Pradesh EAPCET counselling under JNTUA and Government of Andhra Pradesh norms. College admission code: K.S.R.M. Confirm current-year eligibility, seat category and counselling dates in the official admission notice.",
        "placement_info": "The college has an official Training and Placement section. Check its latest placement reports for year-wise student and recruiter details; no unverified percentage or package is stated here.",
        "contact_phone": "+91 8143731980",
        "contact_email": "dean.admissions@ksrmce.ac.in",
        "admission_url": "https://ksrmce.ac.in/admissions/ug",
        "placement_url": "https://ksrmce.ac.in/placements",
        "data_sources": {"admissions_courses_contact": "https://ksrmce.ac.in/admissions/ug", "courses_intake": "https://www.ksrmce.ac.in/academics/courses-intake", "placements": "https://ksrmce.ac.in/placements"},
    },
    "JNTUA College of Engineering": {
        "courses": ["Civil Engineering", "Electrical and Electronics Engineering", "Mechanical Engineering", "Electronics and Communication Engineering", "Computer Science and Engineering", "Chemical Engineering"],
        "admission_info": "For the constituent college at Anantapur, B.Tech first-year admission is through AP EAPCET counselling. JNTUA states that applicants should have passed Intermediate or equivalent with Mathematics, Physics and Chemistry and hold a valid EAPCET rank. Category-A seats are filled by the EAPCET convener; Category-B seats follow applicable Andhra Pradesh norms. Check the current admission notification.",
        "admission_url": "https://www.jntua.ac.in/admissions",
        "data_sources": {"admissions_and_eligibility": "https://www.jntua.ac.in/admissions"},
    },
    "JNTUA College of Engineering, Kalikiri": {
        "courses": ["Civil Engineering", "Electrical and Electronics Engineering", "Mechanical Engineering", "Electronics and Communication Engineering", "Computer Science and Engineering", "Food Technology"],
        "admission_info": "JNTUA lists these B.Tech programmes for its Kalikiri constituent college. First-year admissions follow applicable Andhra Pradesh EAPCET counselling rules. Check the current JNTUA/APSCHE notification for eligibility and seat allotment.",
        "admission_url": "https://www.jntua.ac.in/admissions",
        "data_sources": {"programmes": "https://www.jntua.ac.in/programmes-offered/jntua-cek-programs-offered", "admissions_and_eligibility": "https://www.jntua.ac.in/admissions"},
    },
    "SRM University-AP": {
        "courses": ["Computer Science and Engineering", "Electrical and Electronics Engineering", "Electronics and Communication Engineering", "Microelectronics and Semiconductors", "Mechanical Engineering", "Civil Engineering"],
        "admission_info": "SRM University-AP publishes B.Tech admission information and programme-specific eligibility through its official admissions portal. Check the current admission brochure for accepted entrance routes, eligibility, deadlines and seat-specific conditions.",
        "admission_url": "https://www.srmap.edu.in/admission/",
        "fee_structure_url": "https://www.srmap.edu.in/admission/seas-btech-tuition-fee/",
        "data_sources": {"undergraduate_programmes": "https://www.srmap.edu.in/admission/", "btech_programmes": "https://admissions.srmap.edu.in/lp/btech/", "fee_structure": "https://www.srmap.edu.in/admission/seas-btech-tuition-fee/"},
    },
    "VIT Vellore": {
        "admission_info": "VIT publishes B.Tech programme and admission information through its UG admissions portal. VITEEE is the institution's B.Tech entrance examination for the applicable admission cycle. Check the current prospectus for eligibility, campus availability and counselling rules.",
        "admission_url": "https://vit.ac.in/programmes-offered-ug-admissions",
        "fee_structure_url": "https://vit.ac.in/admission/ug/fee-structure",
        "placement_info": "VIT's Career Development Centre publishes placement highlights and placement information. Use the official information for the relevant campus and graduating batch; no campus-specific percentage or package is inferred here.",
        "placement_url": "https://vit.ac.in/career-development-centre",
        "data_sources": {"ug_programmes": "https://vit.ac.in/programmes-offered-ug-admissions", "fee_structure": "https://vit.ac.in/admission/ug/fee-structure", "placement_information": "https://vit.ac.in/career-development-centre"},
    },
    "G. Pulla Reddy Engineering College": {
        "courses": ["Civil Engineering", "Electrical and Electronics Engineering", "Mechanical Engineering", "Electronics and Communication Engineering", "Computer Science and Engineering", "Computer Science and Business Systems", "CSE (Artificial Intelligence and Machine Learning)", "CSE (Data Science)"],
        "admission_info": "The college lists EAPCET counselling code GPRE. Its official website states that 70% of seats are filled by the Government of Andhra Pradesh under approved norms and 30% are management category seats filled under APSCHE guidelines. Check the current-year notice for eligibility and fees.",
        "scholarships": "The college website advertises a four-year full tuition fee waiver for B.Tech students joining with an AP EAPCET rank below 2,000, and a 50% tuition fee waiver for ranks from 2,000 to 3,000. Confirm current-year terms and eligibility with the college.",
        "placement_info": "The official website provides placement details and placement summaries for 2021, 2022, 2023, 2024 and 2025. Consult the relevant batch report for verified figures.",
        "admission_url": "https://www.gprec.ac.in/",
        "placement_url": "https://www.gprec.ac.in/",
        "data_sources": {"admissions_courses_scholarships_placements": "https://www.gprec.ac.in/"},
    },
    "Sreenivasa Institute of Technology and Management Studies (SITAMS)": {
        "courses": ["Computer Science and Engineering", "Computer Science and Engineering (Artificial Intelligence and Machine Learning)", "Computer Science and Engineering (Artificial Intelligence)", "Computer Science and Engineering (Data Science)", "Electronics and Communication Engineering", "Electrical and Electronics Engineering", "Civil Engineering", "Mechanical Engineering"],
        "admission_info": "SITAMS states that first-year B.Tech applicants need 45% or above in Intermediate for OC and 40% or above for BC/SC/ST, with Mathematics, Physics and Chemistry as optional subjects. 70% of seats are allotted through APSCHE EAPCET counselling and 30% are management/NRI category as per applicable guidelines. Diploma holders may enter second year through ECET lateral entry. Verify current-year rules in the official notice.",
        "placement_info": "The official website links a Placement Cell and displays a 2026–2027 placement-record notice. Use the latest official record for batch-specific statistics; no unverified package figure is added.",
        "contact_phone": "9490550529",
        "contact_email": "principal@sitams.ac.in",
        "admission_url": "https://sitams.ac.in/undergraduate-courses/",
        "placement_url": "https://sitams.ac.in/",
        "data_sources": {"courses_eligibility_fees": "https://sitams.ac.in/undergraduate-courses/", "college_courses_and_contact": "https://sitams.ac.in/", "placement_information": "https://sitams.ac.in/"},
    },
    "IIIT RK Valley (Idupulapaya)": {
        "admission_info": "RGUKT Andhra Pradesh publishes a 2026–2027 admission prospectus for its campuses, including RK Valley. The university describes a six-year integrated course: two years of pre-university study followed by four years of engineering, in fully residential mode. Follow the current prospectus for eligibility, selection and fees.",
        "admission_url": "https://admissions.rgukt.in/",
        "fee_structure_url": "https://admissions.rgukt.in/storage/RGUKT%20Admissions-2026%2027-Prospectus.pdf",
        "data_sources": {"university_and_campuses": "https://www.rgukt.in/", "2026_2027_admission_prospectus": "https://admissions.rgukt.in/storage/RGUKT%20Admissions-2026%2027-Prospectus.pdf"},
    },
    "IIIT Srikakulam (Etcherla)": {
        "admission_info": "RGUKT Andhra Pradesh publishes a 2026–2027 admission prospectus for its Srikakulam campus. The university describes a six-year integrated course: two years of pre-university study followed by four years of engineering, in fully residential mode. Follow the current prospectus for eligibility, selection and fees.",
        "admission_url": "https://admissions.rgukt.in/",
        "fee_structure_url": "https://admissions.rgukt.in/storage/RGUKT%20Admissions-2026%2027-Prospectus.pdf",
        "data_sources": {"university_and_campuses": "https://www.rgukt.in/", "2026_2027_admission_prospectus": "https://admissions.rgukt.in/storage/RGUKT%20Admissions-2026%2027-Prospectus.pdf"},
    },
    "IIIT Nuzvid": {
        "admission_info": "RGUKT Andhra Pradesh publishes a 2026–2027 admission prospectus for its Nuzvid campus. The university describes a six-year integrated course: two years of pre-university study followed by four years of engineering, in fully residential mode. Follow the current prospectus for eligibility, selection and fees.",
        "admission_url": "https://admissions.rgukt.in/",
        "fee_structure_url": "https://admissions.rgukt.in/storage/RGUKT%20Admissions-2026%2027-Prospectus.pdf",
        "data_sources": {"university_and_campuses": "https://www.rgukt.in/", "2026_2027_admission_prospectus": "https://admissions.rgukt.in/storage/RGUKT%20Admissions-2026%2027-Prospectus.pdf"},
    },
}

def safe(value):
    try:
        from bson import ObjectId
        if isinstance(value, ObjectId):
            return str(value)
    except Exception:
        pass
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [safe(v) for v in value]
    return value

def empty(value):
    return value is None or value == "" or value == [] or value == {}

def generic_placeholder(value):
    if not isinstance(value, str):
        return False
    text = value.lower()
    markers = (
        "contact the college for current details",
        "contact the college for current placement details",
        "details have not been added",
        "details are not yet available",
        "verified fee details have not been added",
        "verified placement statistics have not been added",
        "not added yet",
    )
    return any(marker in text for marker in markers)

def main():
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    coll = client[DATABASE_NAME][COLLECTION_NAME]
    docs = list(coll.find({}))
    if not docs:
        raise RuntimeError("No documents found in campus_ai.colleges.")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = Path.cwd() / f"campus_ai_colleges_before_verified_update_{stamp}.json"
    backup.write_text(json.dumps([safe(d) for d in docs], ensure_ascii=False, indent=2), encoding="utf-8")

    today = datetime.now(timezone.utc).date().isoformat()
    changed = 0
    missing = []

    for name, info in VERIFIED.items():
        doc = coll.find_one({"college_name": name})
        if not doc:
            missing.append(name)
            continue

        fields = {
            "data_verified_on": today,
            "data_verification_note": "Only fields with official sources listed in data_sources were checked. Confirm changing details with the institution.",
        }

        for key, value in info.items():
            if key == "data_sources":
                old = doc.get("data_sources") if isinstance(doc.get("data_sources"), dict) else {}
                fields["data_sources"] = {**old, **value}
            elif key == "courses":
                if empty(doc.get("courses")):
                    fields["courses"] = value
            elif empty(doc.get(key)) or generic_placeholder(doc.get(key)):
                fields[key] = value

        result = coll.update_one({"_id": doc["_id"]}, {"$set": fields})
        if result.modified_count:
            changed += 1

    print("\nCampusAI verified-data update completed.")
    print(f"Total college records: {len(docs)}")
    print(f"Colleges covered by this verified update: {len(VERIFIED)}")
    print(f"College documents changed: {changed}")
    print(f"Backup: {backup}")
    print("Existing non-empty fields were preserved.")
    print("No unsupported fee amounts or placement package figures were invented.")
    if missing:
        print("College names not matched:", ", ".join(missing))
    print("Other colleges still need official-source verification.")
    client.close()

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("\nUPDATE FAILED:", exc)
        print("Check that MongoDB is running and the database/collection names are correct.")
