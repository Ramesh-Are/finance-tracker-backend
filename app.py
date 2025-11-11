from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials

app = FastAPI()

# ✅ Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Google Sheets Auth
def get_gspread_client():
    # Render Deployment
    if "GOOGLE_CREDENTIALS" in os.environ:
        creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            creds_json,
            [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ],
        )
        return gspread.authorize(creds)

    # Local development
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "credentials.json",
        [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ],
    )
    return gspread.authorize(creds)


client = get_gspread_client()
sheet = client.open("FinanceTracker").sheet1  # ✅ Must match your sheet name

# ✅ Root
@app.get("/")
async def home():
    return {"message": "Finance API Running ✅"}


# ✅ Add an entry
@app.post("/add_entry")
async def add_entry(data: dict):
    date = data.get("date", "")
    salary = data.get("salary", "")
    amount = data.get("amount", "")
    description = data.get("description", "")

    sheet.append_row([date, salary, amount, description])
    return {"message": "Entry saved ✅"}


# ✅ Get all entries with row numbers FOR DELETE
@app.get("/get_data")
async def get_data():
    rows = sheet.get_all_values()

    if not rows:
        return []

    result = []
    # Start from row 2 (skip headers)
    for row_index in range(2, len(rows) + 1):
        row = sheet.row_values(row_index)

        # Ensure 4 columns exist
        while len(row) < 4:
            row.append("")

        result.append({
            "row": row_index,   # ✅ real Google Sheet row number
            "date": row[0],
            "salary": row[1],
            "amount": row[2],
            "description": row[3]
        })

    return result


@app.delete("/delete_entry/{row_number}")
async def delete_entry(row_number: int):
    try:
        row = sheet.row_values(row_number)

        # ✅ Check if row is empty
        if len(row) == 0:
            raise HTTPException(status_code=400, detail="Row is empty — cannot delete")

        sheet.delete_row(row_number)
        return {"message": f"Row {row_number} deleted ✅"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Delete failed: {str(e)}")


