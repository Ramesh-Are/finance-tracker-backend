from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Google Sheet Setup
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
sheet = client.open("FinanceTracker").sheet1

@app.get("/")
async def home():
    return {"message": "Backend Running ✅"}

# ✅ Add Entry
@app.post("/add_entry")
async def add_entry(data: dict):
    date = data.get("date", "")
    salary = data.get("salary", "")
    amount = data.get("amount", "")
    description = data.get("description", "")

    sheet.append_row([date, salary, amount, description])
    return {"message": "Entry saved successfully ✅"}

# ✅ Get Data with Row Numbers (Fix)
@app.get("/get_data")
async def get_data():
    rows = sheet.get_all_values()

    if len(rows) <= 1:
        return []  # No data

    result = []
    for index, row in enumerate(rows[1:], start=2):  
        result.append({
            "row": index,
            "date": row[0] if len(row) > 0 else "",
            "salary": row[1] if len(row) > 1 else "",
            "amount": row[2] if len(row) > 2 else "",
            "description": row[3] if len(row) > 3 else "",
        })

    return result

# ✅ Delete Entry
@app.delete("/delete_entry/{row_number}")
async def delete_entry(row_number: int):
    try:
        sheet.delete_row(row_number)
        return {"message": "Deleted successfully ✅"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
