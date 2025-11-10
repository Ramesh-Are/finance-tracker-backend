from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials
from fastapi import FastAPI, HTTPException

app = FastAPI()

# Enable CORS so your HTML can call the API
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
sheet = client.open("FinanceTracker").sheet1  # Make sure this name matches your Google Sheet

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

    sheet.append_row([date, salary, amount, description])
    return {"message": "Entry saved successfully ✅"}

# Get all entries
@app.get("/get_data")
async def get_data():
    rows = sheet.get_all_values()  # Returns all rows including headers
    return rows
@app.get("/get_data")
async def get_data():
    rows = sheet.get_all_values()
    # Add row numbers so frontend can delete
    data_with_index = []
    for i, row in enumerate(rows[1:], start=2):  # start=2 because row 1 is headers
        data_with_index.append({
            "row": i,
            "date": row[0],
            "salary": row[1],
            "amount": row[2],
            "description": row[3]
        })
    return data_with_index
@app.delete("/delete_entry/{row_number}")
async def delete_entry(row_number: int):
    try:
        sheet.delete_row(row_number)
        return {"message": f"Entry in row {row_number} deleted successfully!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


