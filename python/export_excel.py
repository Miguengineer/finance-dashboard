#!/usr/bin/env python3
"""
Export Firestore 'transactions' to an Excel workbook.
Requires: pandas, google-cloud-firestore
Auth: set GOOGLE_APPLICATION_CREDENTIALS to your Firebase service account JSON.
Usage:
  python export_excel.py output.xlsx --uid <your-uid> [--month 2025-08]
"""
import argparse
import pandas as pd
from google.cloud import firestore

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("output", help="Output .xlsx file")
    ap.add_argument("--uid", required=True, help="User UID to export")
    ap.add_argument("--month", help="Filter month key (YYYY-MM)")
    args = ap.parse_args()

    client = firestore.Client()
    q = client.collection("transactions").where("uid","==",args.uid)
    if args.month:
        q = q.where("month","==",args.month)
    docs = list(q.stream())

    rows = []
    for d in docs:
        x = d.to_dict()
        rows.append({
            "date": x["date"].date().isoformat() if hasattr(x.get("date"), "date") else x.get("date",""),
            "amount": x.get("amount",""),
            "category": x.get("category",""),
            "payee": x.get("payee",""),
            "payer": x.get("payer",""),
            "account": x.get("account",""),
            "notes": x.get("notes",""),
            "month": x.get("month",""),
            "uid": x.get("uid",""),
        })
    df = pd.DataFrame(rows)
    with pd.ExcelWriter(args.output, engine="openpyxl") as w:
        df.to_excel(w, sheet_name="Transactions", index=False)
    print(f"Exported {len(rows)} rows to {args.output}")

if __name__ == "__main__":
    main()
