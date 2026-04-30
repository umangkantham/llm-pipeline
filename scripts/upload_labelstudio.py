import json
import requests

USERNAME = "umang@kantham.ai"
PASSWORD = "Ram@2026"

PROJECT_ID = 1   # ⚠️ make sure this is correct
INPUT = "data/processed/cleaned.json"
BASE_URL = "http://localhost:8080"


def upload_to_labelstudio():
    session = requests.Session()

    # 🟢 Step 1 — Get CSRF
    session.get(BASE_URL)
    csrftoken = session.cookies.get("csrftoken")

    # 🟢 Step 2 — Login
    login_url = f"{BASE_URL}/user/login/"
    headers = {"X-CSRFToken": csrftoken}

    login_data = {
        "email": USERNAME,
        "password": PASSWORD
    }

    login_res = session.post(login_url, data=login_data, headers=headers)

    print("LOGIN STATUS:", login_res.status_code)

    if login_res.status_code != 200:
        print("❌ Login failed")
        print(login_res.text)
        return

    # 🟢 Step 3 — Load dataset
    with open(INPUT, "r", encoding="utf-8") as f:
        data = json.load(f)

    # ✅ Format tasks correctly
    tasks = []
    for item in data:
        tasks.append({
            "data": {
                "query": item.get("query", ""),
                "code": item.get("code", "")
            }
        })

    # 🟢 Step 4 — USE CORRECT IMPORT ENDPOINT
    url = f"{BASE_URL}/api/projects/{PROJECT_ID}/import"

    headers = {
        "X-CSRFToken": csrftoken,
        "Content-Type": "application/json"
    }

    # ✅ IMPORTANT: send as dictionary
    payload = tasks   # this endpoint accepts list directly

    res = session.post(url, json=payload, headers=headers)

    print("\n====== RESULT ======")
    print("UPLOAD STATUS:", res.status_code)
    print("RESPONSE:", res.text[:300])
    print("====================\n")


if __name__ == "__main__":
    upload_to_labelstudio()