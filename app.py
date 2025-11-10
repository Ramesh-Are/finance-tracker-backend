from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Google Sheets Setup
def get_gspread_client():
    if "GOOGLE_CREDENTIALS" in os.environ:
        creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            creds_json,
            ["https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive"]
        )
        return gspread.authorize(creds)

    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "credentials.json",
        ["https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive"]
    )
    return gspread.authorize(creds)

client = get_gspread_client()
sheet = client.open("FinanceTracker").sheet1  # Make sure this matches your Google Sheet name

# Root
@app.get("/")
async def home():
    return {"message": "Finance Tracker Backend Running ✅"}

# Add a new entry
@app.post("/add_entry")
async def add_entry(data: dict):
    date = data.get("date", "")
    salary = data.get("salary", "")
    amount = data.get("amount", "")
    description = data.get("description", "")

    if not date or (salary == "" and amount == "") or not description:
        raise HTTPException(status_code=400, detail="Invalid data")

    sheet.append_row([date, salary, amount, description])
    return {"message": "Entry saved successfully ✅"}

# Get all entries (with row numbers)
@app.get("/get_data")
async def get_d_




