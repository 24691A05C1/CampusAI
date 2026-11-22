from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
collection = client["campus_ai"]["colleges"]

college = collection.find_one(
    {"college_name": "K.S.R.M. College of Engineering"}
)

if college:
    print("\nCOLLEGE DOCUMENT FIELD STRUCTURE\n")

    for key, value in college.items():
        print(f"\n{key}:")
        print("Type:", type(value).__name__)
        print("Value:", repr(value)[:1000])

else:
    print("College not found.")

client.close()