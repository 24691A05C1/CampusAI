from pymongo import MongoClient


MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "campus_ai"
COLLECTION = "colleges"


CHECK_FIELDS = {
    "Courses": "courses",
    "Admission Information": "admission_info",
    "Fee Structure": "fee_structure",
    "Placement Information": "placement_info",
    "Contact Email": "contact_email",
    "Contact Phone": "contact_phone",
    "Official Website": "website"
}


def is_missing(value):
    return (
        value is None
        or value == ""
        or value == []
        or value == {}
    )


def main():

    print("\n========================================")
    print("       CAMPUSAI DATABASE AUDIT")
    print("========================================")

    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000
    )

    try:

        client.admin.command("ping")
        print("\nMongoDB connected successfully.")

        collection = client[DB_NAME][COLLECTION]

        colleges = list(collection.find({}))

        total = len(colleges)

        print(f"\nTotal college records: {total}")

        print("\n========================================")
        print("       FIELD COMPLETION SUMMARY")
        print("========================================")

        missing_records = {}

        for label, field in CHECK_FIELDS.items():

            missing = [
                college.get("college_name", "Unknown College")
                for college in colleges
                if is_missing(college.get(field))
            ]

            completed = total - len(missing)

            missing_records[label] = missing

            print(f"\n{label}")
            print(f"Completed: {completed}/{total}")
            print(f"Missing: {len(missing)}")

        print("\n========================================")
        print("       COLLEGES NEEDING UPDATES")
        print("========================================")

        for label, names in missing_records.items():

            print(f"\n--- {label} ---")

            if not names:
                print("All colleges have this field.")
            else:
                for name in names:
                    print(f"- {name}")

        # Course count for each college
        print("\n========================================")
        print("       COURSE LIST AUDIT")
        print("========================================")

        for college in colleges:

            name = college.get("college_name", "Unknown College")
            courses = college.get("courses", [])

            if isinstance(courses, list):
                course_count = len(courses)
            else:
                course_count = 1 if not is_missing(courses) else 0

            print(f"{name}: {course_count} courses")

        # Data source audit
        print("\n========================================")
        print("       DATA SOURCE AUDIT")
        print("========================================")

        source_count = 0
        no_source = []

        for college in colleges:

            name = college.get("college_name", "Unknown College")
            sources = college.get("data_sources")

            if isinstance(sources, dict) and sources:
                source_count += 1
            else:
                no_source.append(name)

        print(f"Colleges with data sources: {source_count}/{total}")
        print(f"Colleges without data sources: {len(no_source)}")

        for name in no_source:
            print(f"- {name}")

        # Verification date audit
        verified_count = sum(
            1 for college in colleges
            if not is_missing(college.get("data_verified_on"))
        )

        print("\n========================================")
        print("       VERIFICATION SUMMARY")
        print("========================================")

        print(f"Records with verification dates: {verified_count}/{total}")

        print("\n========================================")
        print("       AUDIT COMPLETED")
        print("========================================")

        print("No database records were modified.")

    except Exception as error:

        print("\nAUDIT ERROR:", error)

    finally:

        client.close()
        print("\nMongoDB connection closed.")


if __name__ == "__main__":
    main()