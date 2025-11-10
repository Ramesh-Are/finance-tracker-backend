from fastapi import FastAPI
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

# Google Sheet Setup
def get_gspread_client():
    # If running on Render
    if "GOOGLE_CREDENTIALS" in os.environ:
        creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            creds_json,
            ["https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive"]
        )
        return gspread.authorize(creds)

    # Local PC
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "credentials.json",
        ["https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive"]
    )
    return gspread.authorize(creds)


client = get_gspread_client()
sheet = client.open("Finance Tracker").sheet1


@app.get("/")
async def home():
    return {"message": "Finance Tracker Backend Running ✅"}


@app.post("/add_entry")
async def add_entry(data: dict):
    date = data.get("date", "")
    salary = data.get("salary", "")
    amount = data.get("amount", "")
    description = data.get("description", "")

    sheet.append_row([date, salary, amount, description])

    return {"message": "Entry saved successfully ✅"}
