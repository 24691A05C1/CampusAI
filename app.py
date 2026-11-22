from datetime import datetime
from functools import wraps
import os
import re
from urllib.parse import urlparse

from bson.objectid import ObjectId
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "replace-this-with-a-long-random-secret")
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client["campus_ai"]
users = db["users"]
colleges = db["colleges"]
conversations = db["conversations"]

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped

def current_user_id():
    try:
        return ObjectId(session["user_id"])
    except (KeyError, ValueError):
        return None

def safe_external_url(value):
    """Allow only normal public HTTP(S) links stored in college records."""
    if not isinstance(value, str):
        return ""
    value = value.strip()
    parsed = urlparse(value)
    if parsed.scheme in ("http", "https") and parsed.netloc:
        return value
    return ""

app.jinja_env.filters["safe_url"] = safe_external_url

def display_timestamp(value):
    if hasattr(value, "strftime"):
        return value.strftime("%d %b %Y, %I:%M %p")
    if isinstance(value, str):
        return value
    return ""

app.jinja_env.filters["display_timestamp"] = display_timestamp

@app.context_processor
def inject_globals():
    return {"current_year": datetime.now().year}

@app.route("/")
def index():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        if not name or not email or not password:
            flash("Please complete every field.", "error")
        elif not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            flash("Enter a valid email address.", "error")
        elif len(password) < 8:
            flash("Use a password with at least 8 characters.", "error")
        elif password != confirm:
            flash("Your passwords do not match.", "error")
        else:
            try:
                if users.find_one({"email": email}):
                    flash("An account with this email already exists. Please log in.", "error")
                else:
                    users.insert_one({
                        "name": name,
                        "email": email,
                        "password": generate_password_hash(password),
                        "created_at": datetime.now().astimezone()
                    })
                    flash("Your account is ready. Please log in.", "success")
                    return redirect(url_for("login"))
            except PyMongoError:
                flash("Database connection failed. Please check that MongoDB is running.", "error")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        try:
            user = users.find_one({"email": email})
            if user and check_password_hash(user.get("password", ""), password):
                session.clear()
                session["user_id"] = str(user["_id"])
                session["user_name"] = user.get("name", "Student")
                destination = request.args.get("next")
                return redirect(destination if destination and destination.startswith("/") else url_for("dashboard"))
            flash("Email or password is incorrect.", "error")
        except PyMongoError:
            flash("Database connection failed. Please check that MongoDB is running.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))

@app.route("/dashboard")
@login_required
def dashboard():
    total_colleges = colleges.count_documents({})
    total_chats = conversations.count_documents({"user_id": session["user_id"]})
    recent = list(conversations.find({"user_id": session["user_id"]}).sort("created_at", -1).limit(4))
    return render_template("dashboard.html", name=session.get("user_name", "Student"),
                           total_colleges=total_colleges, total_chats=total_chats, recent=recent)

@app.route("/explore-colleges")
@login_required
def explore_colleges():
    query = request.args.get("q", "").strip()

    # Fetch all colleges for the dropdown
    all_colleges = list(
        colleges.find({}, {"college_name": 1}).sort("college_name", 1)
    )

    if query:
        pattern = {"$regex": re.escape(query), "$options": "i"}

        filt = {
            "$or": [
                {"college_name": pattern},
                {"college_id": pattern},
                {"location": pattern},
                {"courses": pattern},
                {"description": pattern}
            ]
        }

        results = list(
            colleges.find(filt).sort("college_name", 1)
        )
    else:
        results = []

    return render_template(
        "explore_colleges.html",
        colleges=results,
        all_colleges=all_colleges,
        query=query
    )
@app.route("/college/<college_id>")
@login_required
def college_details(college_id):
    if not ObjectId.is_valid(college_id):
        flash("That college could not be found.", "error")
        return redirect(url_for("explore_colleges"))
    college = colleges.find_one({"_id": ObjectId(college_id)})
    if not college:
        flash("That college could not be found.", "error")
        return redirect(url_for("explore_colleges"))
    return render_template("college_details.html", college=college)

@app.route("/admissions")
@login_required
def admissions():
    return render_template("admissions.html")


@app.route("/compare-colleges")
@login_required
def compare_colleges():
    all_colleges = list(colleges.find({}).sort("college_name", 1))
    first_id = request.args.get("college1", "")
    second_id = request.args.get("college2", "")
    selected = []
    for college_id in (first_id, second_id):
        if college_id and ObjectId.is_valid(college_id):
            record = colleges.find_one({"_id": ObjectId(college_id)})
            if record:
                selected.append(record)
            else:
                selected.append(None)
        else:
            selected.append(None)
    return render_template("compare_colleges.html", colleges=all_colleges,
                           first_id=first_id, second_id=second_id, selected=selected)


@app.route("/scholarships")
@login_required
def scholarships():
    all_colleges = list(colleges.find({}).sort("college_name", 1))
    scholarship_fields = ("scholarships", "scholarship_info", "financial_aid")
    entries = []
    for college in all_colleges:
        details = next((college.get(key) for key in scholarship_fields if college.get(key)), None)
        entries.append({"college": college, "details": details})
    official_schemes = [
        {"name": "Andhra Pradesh JnanaBhumi – Post Matric Scholarships (RTF/MTF)",
         "description": "Official Andhra Pradesh portal for eligible post-matric scholarship services. Check current eligibility, documents and application notices on the portal.",
         "url": "https://jnanabhumi.ap.gov.in/"},
        {"name": "National Scholarship Portal (NSP)",
         "description": "Government of India portal to explore central and state scholarship schemes, eligibility and application status.",
         "url": "https://scholarships.gov.in/Students"},
        {"name": "NSP – All Scholarships",
         "description": "Browse scholarship schemes listed for the current academic year. Scheme availability and deadlines can change.",
         "url": "https://scholarships.gov.in/All-Scholarships"},
    ]
    return render_template("scholarships.html", entries=entries, official_schemes=official_schemes)


@app.route("/placement-insights")
@login_required
def placement_insights():
    all_colleges = list(colleges.find({}).sort("college_name", 1))
    placement_fields = ("placement_details", "placements", "placement_info", "highest_package", "average_package", "placement_percentage", "recruiters")
    entries = []
    for college in all_colleges:
        details = [(key.replace("_", " ").title(), college.get(key)) for key in placement_fields if college.get(key)]
        entries.append({"college": college, "details": details})
    return render_template("placement_insights.html", entries=entries)

@app.route("/question-papers")
@login_required
def question_papers():
    all_colleges = list(colleges.find({}).sort("college_name", 1))
    selected_id = request.args.get("college_id", "")
    selected = None
    if selected_id and ObjectId.is_valid(selected_id):
        selected = colleges.find_one({"_id": ObjectId(selected_id)})
    paper_url = ""
    if selected:
        candidate = (selected.get("question_papers_website") or "").strip()
        official = (selected.get("website") or "").strip()
        candidate = safe_external_url(candidate)
        official = safe_external_url(official)
        if candidate and candidate.rstrip("/").lower() != official.rstrip("/").lower():
            paper_url = candidate
    return render_template("question_papers.html", colleges=all_colleges,
                           selected_college=selected_id, selected=selected,
                           question_papers_url=paper_url,
                           selected_semester=request.args.get("semester", ""),
                           selected_year=request.args.get("year", ""),
                           selected_subject=request.args.get("subject", ""))

def assistant_reply(question):
    q = question.lower()
    if not question:
        return "Type a question first and I will help you navigate CampusAI."
    if any(k in q for k in ("admission", "eligibility", "apply to college", "documents required")):
        return "Open the Admissions Guide from the dashboard for a general checklist. Admission rules, eligibility, dates and documents vary by college, so confirm the latest requirements in the institution's official notification."
    if any(k in q for k in ("question paper", "previous paper", "exam paper", "past paper")):
        return "Open Previous Question Papers, choose your college, and follow its available examination or library resource link. Some colleges publish papers through their own student portals."
    if any(k in q for k in ("college", "university", "mits", "jnt", "vit", "srm")):
        return "Use Explore Colleges to search the directory. Each college card separates its official homepage from any examination or library resource link available in the directory."
    if any(k in q for k in ("attendance", "syllabus", "timetable", "result", "exam")):
        return "For current attendance, syllabus, timetable, results, and exam notices, check your college's official student portal or examination section. CampusAI links to college resources but does not access private college records."
    if any(k in q for k in ("hello", "hi", "hey")):
        return "Hello! I am your CampusAI guide. I can help you find colleges, examination resources, and navigate this portal."
    if "feature" in q or "how to use" in q:
        return "CampusAI includes a searchable college directory, examination-resource links, a student assistant, and your private chat history. Use the dashboard cards to open each feature."
    return "I can guide you around the CampusAI portal and help locate college and examination resources. Try asking about colleges, question papers, exams, attendance, or how to use the portal. For live academic updates, use your college's official portal."

@app.route("/assistant", methods=["GET", "POST"])
@login_required
def assistant():
    answer = None
    question = ""
    if request.method == "POST":
        question = request.form.get("question", "").strip()
        answer = assistant_reply(question)
        conversations.insert_one({
            "user_id": session["user_id"],
            "question": question,
            "answer": answer,
            "created_at": datetime.now().astimezone()
        })
    return render_template("assistant.html", question=question, answer=answer)

@app.route("/chat-history")
@login_required
def chat_history():
    history = list(conversations.find({"user_id": session["user_id"]}).sort("created_at", -1).limit(100))
    for item in history:
        display_messages = []
        messages = item.get("messages")
        if isinstance(messages, list) and messages:
            for msg in messages:
                if isinstance(msg, dict) and msg.get("content"):
                    display_messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
        else:
            question = item.get("question") or item.get("user_message") or item.get("user") or item.get("message") or ""
            answer = item.get("answer") or item.get("assistant_message") or item.get("bot") or item.get("response") or ""
            if question: display_messages.append({"role": "user", "content": question})
            if answer: display_messages.append({"role": "assistant", "content": answer})
        item["display_messages"] = display_messages
    return render_template("chat_history.html", history=history)

@app.route("/health")
def health():
    try:
        client.admin.command("ping")
        return jsonify(status="ok", database="connected")
    except PyMongoError:
        return jsonify(status="error", database="disconnected"), 503

if __name__ == "__main__":
    # Existing campus_ai records are used as-is. No automatic insert/update/delete
    # is performed on startup, so the user's MongoDB data remains untouched.
    app.run(debug=False, use_reloader=False)
