# Home Finance Dashboard (GitHub Pages + Firebase + Python)

Quick, zero-cost stack to track household finances:
- Static web app hosted on GitHub Pages
- Firebase Authentication + Firestore (free tier is enough for light use)
- Python scripts to import from your legacy Excel and export snapshots back to Excel

## 0) What You Get
- `web/` static site (drop into a GitHub Pages repo)
- `firestore.rules` template to secure your data
- `python/` scripts:
  - `import_excel.py` (Excel → Firestore)
  - `export_excel.py` (Firestore → Excel)

## 1) Create Firebase Project
1. Go to https://console.firebase.google.com → Add project (no Analytics needed).
2. Firestore: Build → Firestore Database → Create database (Start in production mode).
3. Authentication: Build → Authentication → Sign-in method → Enable Email/Password.
4. Authentication: Add users → add your and your partner's emails with passwords.
5. Project settings → Your apps → Web app → Register app → **Copy the Web config**.

Create a file `web/firebase-config.js` with your config:
```js
export const firebaseConfig = {
  apiKey: "...",
  authDomain: "...",
  projectId: "...",
  storageBucket: "...",
  messagingSenderId: "...",
  appId: "..."
};
```

## 2) Lock Firestore Rules
In Firebase console → Firestore → Rules: paste `firestore.rules` from this repo.
Replace emails in `isAllowedUser()` with yours. Publish.

## 3) Deploy on GitHub Pages
1. Create a new public/private repo (e.g., `home-finance-dashboard`).
2. Copy everything under `web/` to the repo root (so `index.html` is at root).
3. In GitHub repo → Settings → Pages → Build from a branch → Select `main` branch `/root`.
4. Wait until Pages is active. Visit the URL and log in with your Firebase account.

> Note: Firebase web config is public by design. Your data is protected by Firestore rules.

## 4) Import Legacy Excel
Install deps on Ubuntu:
```bash
sudo apt-get update && sudo apt-get install -y python3-pip
python3 -m pip install pandas openpyxl google-cloud-firestore google-auth
```

Create a Firebase service account key (Project settings → Service accounts → Generate new private key).
Save JSON (e.g., `~/keys/firebase.json`).

Set credentials and run import:
```bash
export GOOGLE_APPLICATION_CREDENTIALS=~/keys/firebase.json
python3 python/import_excel.py /path/to/your.xlsx --uid <YOUR_FIREBASE_UID>
# Or if your Excel already has a 'uid' column per row:
python3 python/import_excel.py /path/to/your.xlsx
```

Expected columns in **Transactions** sheet:
- `date` (YYYY-MM-DD)
- `amount` (negative for expense, positive for income)
- `category`, `payee`, `payer`, `account`, `notes` (optional)
- `uid` (optional if using --uid)

## 5) Export to Excel (backup or auditing)
```bash
python3 -m pip install pandas openpyxl google-cloud-firestore google-auth
export GOOGLE_APPLICATION_CREDENTIALS=~/keys/firebase.json
python3 python/export_excel.py out.xlsx --uid <YOUR_FIREBASE_UID> --month 2025-08
```

## 6) Data Model (simple)
Collection: `transactions`
```json
{
  "uid": "<auth user id>",
  "date": <timestamp>,
  "month": "YYYY-MM",
  "amount": -54000,
  "category": "Food",
  "payee": "Supermarket",
  "payer": "Miguel",
  "account": "Visa ****1234",
  "notes": "weekly groceries",
  "createdAt": <server timestamp>
}
```

You can add more collections later (budgets/categories). Keep each doc tied to `uid`.

## 7) Local Dev
You can open `web/index.html` directly in your browser and it will work.
For a nicer workflow, use a static server:
```bash
sudo apt-get install -y npm
npm -g install serve
serve web
```

## 8) Tips
- Amounts: positive for income, negative for expenses (keeps math trivial).
- Use categories consistently (e.g., Food, Rent, Transport, Utilities, Health, Leisure).
- If a card charge is split, create multiple transactions with same date/payee.
- For privacy, keep the GitHub repo private; Pages still works from private repos for public access with URL. If you need stricter access, consider Netlify with password or deploy the same static site behind your own reverse proxy.

## 9) Troubleshooting
- Blank dashboard after login → Check Firestore rules allow your email and that docs have `uid` equal to your authenticated `uid`.
- Import fails with auth → Ensure `GOOGLE_APPLICATION_CREDENTIALS` points to the service account JSON.
- Timezone/date: App stores a `month` string; adjust logic if you prefer month by local timezone vs. UTC.

Enjoy!
