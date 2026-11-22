# CampusAI — Complete Flask + MongoDB Project

## Included
- Student registration and login with password hashing
- Student dashboard with live counts from MongoDB
- College search by name, college ID, location, courses and description
- College profiles: courses, facilities, admissions, fees, scholarships, placements and contact details
- Google Maps search link based on saved college location
- College comparison using the fields available in the database
- Question-paper resource links stored separately from official college websites
- Scholarship Finder with official Government of India NSP and Andhra Pradesh JnanaBhumi links
- Placement insights based only on information present in college records
- CampusAI rule-based assistant and per-user chat history
- `/health` endpoint for MongoDB connectivity

## Requirements
- Python 3.10 or newer
- MongoDB Community Server running locally, or a MongoDB Atlas URI

## Windows setup
1. Extract the ZIP.
2. Open the extracted `AI_Campus_Assistant` folder in VS Code.
3. Open **Terminal → New Terminal**.
4. Run:
   ```powershell
   py -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   python app.py
   ```
   If PowerShell blocks activation, use Command Prompt and run:
   ```bat
   venv\Scripts\activate.bat
   ```
5. Ensure MongoDB is running.
6. Open `http://127.0.0.1:5000`.

## Database
The application uses:
- MongoDB URI: `mongodb://localhost:27017/` by default
- Database: `campus_ai`
- Collections: `users`, `colleges`, `conversations`

**Important:** The app uses your existing records as-is. Startup does not automatically insert, update or delete college records. Do not edit MongoDB Compass to use this ZIP.

Your college documents can contain:
`college_id`, `college_name`, `location`, `courses`, `facilities`, `description`, `admission_info`, `eligibility`, `fee_structure`, `placement_info`, `placement_details`, `contact_email`, `contact_phone`, `website`, `college_timings`, `question_papers_website`, and optional scholarship fields such as `scholarships`, `scholarship_info`, or `financial_aid`.

If a field is missing, the dashboard shows that the information is not available. Fee data is never presented as scholarship data. Question-paper links are shown only when a separate valid HTTP(S) resource URL is saved; the official homepage is not substituted as a question-paper link.

## Official scholarship resources included
- Andhra Pradesh JnanaBhumi: https://jnanabhumi.ap.gov.in/
- National Scholarship Portal student page: https://scholarships.gov.in/Students
- National Scholarship Portal scheme list: https://scholarships.gov.in/All-Scholarships

## Notes
- The built-in assistant is a keyword/rule-based guide, not a live generative AI service.
- The semester/year/subject fields on Question Papers help label your search; the external college resource controls what is actually available.
- No PDF upload feature is included.
- Set a strong `SECRET_KEY` and `MONGO_URI` environment variables before deployment. Disable debug mode and use HTTPS in production.
