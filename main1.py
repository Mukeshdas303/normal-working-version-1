from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import csv
import os
import json
import uuid
from datetime import datetime

app = FastAPI()

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- FILE CONFIG ----------------
FILE_NAME = "Back_data.csv"

# store latest submission in memory
LATEST_RESPONSE = {}

# ---------------- CREATE CSV FILE ----------------
if not os.path.exists(FILE_NAME):
    with open(FILE_NAME, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Submission ID",
            "Name", "Email", "Phone", "Age", "DOB", "Nationality", "Marital Status",
            "Address", "City", "State", "Pincode", "Country", "LinkedIn", "Portfolio",
            "Gender", "Position", "Experience Years", "Annual Income",
            "Highest Qualification", "Notice Period", "Current Company", "Skills",
            "Timestamp"
        ])

# ---------------- NORMALIZER ----------------
def normalize_payload(data: dict):

    def to_int(v):
        try:
            if v in [None, "", "none", "na"]:
                return 0
            return int(float(v))
        except:
            return 0

    def to_float(v):
        try:
            if v in [None, "", "none", "na"]:
                return 0.0
            cleaned = str(v).replace("LPA", "").replace("lpa", "").strip()
            return float(cleaned)
        except:
            return 0.0

    def to_list(v):
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                return json.loads(v)
            except:
                return [v]
        return []

    clean = {
        "name": str(data.get("name", "")),
        "email": str(data.get("email", "")),
        "phone": str(data.get("phone", "")),
        "age": to_int(data.get("age")),
        "dob": str(data.get("dob", "")),
        "nationality": str(data.get("nationality", "")),
        "marital_status": str(data.get("marital_status", "")),
        "address": str(data.get("address", "")),
        "city": str(data.get("city", "")),
        "state": str(data.get("state", "")),
        "pincode": to_int(data.get("pincode")),
        "country": str(data.get("country", "")),
        "linkedin": str(data.get("linkedin", "")),
        "portfolio": str(data.get("portfolio", "")),
        "gender": str(data.get("gender", "")),
        "position": str(data.get("position", "")),
        "experience_years": to_int(data.get("experience_years")),
        "annual_income": to_float(data.get("annual_income")),
        "highest_qualification": str(data.get("highest_qualification", "")),
        "notice_period": to_int(data.get("notice_period")),
        "current_company": str(data.get("current_company", "")),
        "skills": to_list(data.get("skills")),
    }

    return clean

# ---------------- SAVE TO CSV ----------------
def save_to_csv(data_dict, submission_id, timestamp):

    with open(FILE_NAME, mode="a", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            submission_id,
            data_dict["name"],
            data_dict["email"],
            data_dict["phone"],
            data_dict["age"],
            data_dict["dob"],
            data_dict["nationality"],
            data_dict["marital_status"],
            data_dict["address"],
            data_dict["city"],
            data_dict["state"],
            data_dict["pincode"],
            data_dict["country"],
            data_dict["linkedin"],
            data_dict["portfolio"],
            data_dict["gender"],
            data_dict["position"],
            data_dict["experience_years"],
            data_dict["annual_income"],
            data_dict["highest_qualification"],
            data_dict["notice_period"],
            data_dict["current_company"],
            ", ".join(data_dict["skills"]),
            timestamp
        ])

# ---------------- SUBMIT ENDPOINT ----------------
@app.post("/submit")
async def submit_form(request: Request):

    data = await request.json()

    print("\n📥 Raw Data Received:")
    print(data)

    clean_data = normalize_payload(data)

    print("\n🧹 Cleaned Data:")
    print(clean_data)

    submission_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().isoformat()

    save_to_csv(clean_data, submission_id, timestamp)

    global LATEST_RESPONSE
    LATEST_RESPONSE = {
        "submission_id": submission_id,
        "timestamp": timestamp,
        **clean_data
    }

    return {
        "status": "success",
        "data": LATEST_RESPONSE
    }

# ---------------- GET LATEST ----------------
@app.get("/latest")
def get_latest():
    return LATEST_RESPONSE if LATEST_RESPONSE else {}

# ---------------- GET BY ID ----------------
@app.get("/submission/{submission_id}")
def get_submission_by_id(submission_id: str):

    if not os.path.exists(FILE_NAME):
        return {"error": "No data file found"}

    with open(FILE_NAME, mode="r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row["Submission ID"] == submission_id:

                return {
                    "submission_id": row["Submission ID"],
                    "name": row["Name"],
                    "email": row["Email"],
                    "phone": row["Phone"],
                    "age": int(row["Age"]) if row["Age"] else 0,
                    "dob": row["DOB"],
                    "nationality": row["Nationality"],
                    "marital_status": row["Marital Status"],
                    "address": row["Address"],
                    "city": row["City"],
                    "state": row["State"],
                    "pincode": int(row["Pincode"]) if row["Pincode"] else 0,
                    "country": row["Country"],
                    "linkedin": row["LinkedIn"],
                    "portfolio": row["Portfolio"],
                    "gender": row["Gender"],
                    "position": row["Position"],
                    "experience_years": int(row["Experience Years"]) if row["Experience Years"] else 0,
                    "annual_income": float(row["Annual Income"]) if row["Annual Income"] else 0.0,
                    "highest_qualification": row["Highest Qualification"],
                    "notice_period": int(row["Notice Period"]) if row["Notice Period"] else 0,
                    "current_company": row["Current Company"],
                    "skills": [s.strip() for s in row["Skills"].split(",")] if row["Skills"] else [],
                    "timestamp": row["Timestamp"]
                }

    return {"error": "Submission ID not found"}

# ---------------- HEALTH CHECK ----------------
@app.get("/")
def health():
    return {"status": "API running"}
