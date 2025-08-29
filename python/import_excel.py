#!/usr/bin/env python3
"""
Import transactions from an Excel workbook into Firestore.
Requires: pandas, openpyxl, google-cloud-firestore, google-auth
Auth: set GOOGLE_APPLICATION_CREDENTIALS to your Firebase service account JSON.
Workbook expectation:
 - Sheet "Transactions" with columns:
   date (YYYY-MM-DD), amount (float; negative for expense), category, payee, payer, account, notes, uid (optional)
If uid is missing, provide --uid CLI arg.
"""
import argparse
import pandas as pd
from datetime import datetime
from google.cloud import firestore

def month_key(date_str):
    dt = datetime.fromisoformat(date_str)
    return f"{dt.year}-{dt.month:02d}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("excel_file", help="Path to Excel workbook")
    ap.add_argument("--sheet", default="Transactions", help="Sheet name [Transactions]")
    ap.add_argument("--uid", help="Default UID for all rows (if no 'uid' column)")
    args = ap.parse_args()

    df = pd.read_excel(args.excel_file, sheet_name=args.sheet)
    required = ["date","amount"]
    for c in required:
        if c not in df.columns:
            raise SystemExit(f"Missing required column: {c}")

    if "uid" not in df.columns and not args.uid:
        raise SystemExit("Provide --uid if 'uid' column is missing.")

    df = df.fillna("")
    client = firestore.Client()
    batch = client.batch()
    col = client.collection("transactions")
    count = 0
    for _, row in df.iterrows():
        date_str = str(row["date"])[:10]
        doc = {
            "uid": row["uid"] if "uid" in df.columns and row["uid"] else args.uid,
            "date": datetime.fromisoformat(date_str),
            "month": month_key(date_str),
            "amount": float(row["amount"]),
            "category": str(row.get("category","")),
            "payee": str(row.get("payee","")),
            "payer": str(row.get("payer","")),
            "account": str(row.get("account","")),
            "notes": str(row.get("notes","")),
        }
        batch.create(col.document(), doc)
        count += 1
        if count % 400 == 0:
            batch.commit()
            batch = client.batch()
    if count % 400 != 0:
        batch.commit()
    print(f"Imported {count} rows into 'transactions'.")

if __name__ == "__main__":
    main()
