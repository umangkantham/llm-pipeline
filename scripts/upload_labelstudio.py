import json
import requests
import os

USERNAME = os.getenv("LABEL_STUDIO_EMAIL")
PASSWORD = os.getenv("LABEL_STUDIO_PASSWORD")

INPUT = "data/processed/cleaned.json"
BASE_URL = "http://localhost:8080"

PROJECT_FILE = "project_id.txt"


# 🔥 Load previous project id
def load_project_id():
    if os.path.exists(PROJECT_FILE):
        with open(PROJECT_FILE, "r") as f:
            return f.read().strip()
    return None


# 🔥 Save project id
def save_project_id(pid):
    with open(PROJECT_FILE, "w") as f:
        f.write(str(pid))


# 🔥 DELETE + CREATE PROJECT
def recreate_project(session, csrftoken):
    project_id = load_project_id()

    # 🧨 DELETE OLD PROJECT (if exists)
    if project_id:
        print(f"🧨 Deleting old project: {project_id}")

        delete_url = f"{BASE_URL}/api/projects/{project_id}"
        headers = {"X-CSRFToken": csrftoken}

        res = session.delete(delete_url, headers=headers)
        print("DELETE STATUS:", res.status_code)

    # 🆕 CREATE NEW PROJECT
    print("🆕 Creating new project...")

    create_url = f"{BASE_URL}/api/projects"

    payload = {
        "title": "AutoGPT Fresh Dataset",
        "label_config": """
        <View>
          <Text name="query" value="$query"/>
          <Text name="code" value="$code"/>
          <Choices name="label" toName="code">
            <Choice value="Relevant"/>
            <Choice value="Not Relevant"/>
          </Choices>
        </View>
        """
    }

    headers = {
        "X-CSRFToken": csrftoken,
        "Content-Type": "application/json"
    }

    res = session.post(create_url, json=payload, headers=headers)

    project = res.json()
    new_project_id = project["id"]

    print("✅ New Project ID:", new_project_id)

    # 💾 SAVE for next run
    save_project_id(new_project_id)

    return new_project_id


def upload_to_labelstudio():
    if not USERNAME or not PASSWORD:
        raise RuntimeError("Set LABEL_STUDIO_EMAIL and LABEL_STUDIO_PASSWORD before running upload.")

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
        return

    # 🔥 STEP 3 — FAST RESET
    PROJECT_ID = recreate_project(session, csrftoken)

    # 🟢 Step 4 — Load dataset
    with open(INPUT, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 🔥 LIMIT DATA
    MAX_SAMPLES = 500
    data = data[:MAX_SAMPLES]

    print(f"🚀 Uploading {len(data)} samples")

    # 🟢 Step 5 — Format tasks
    tasks = [
        {
            "data": {
                "query": item.get("query") or item.get("hard_query") or item.get("soft_query", ""),
                "code": item.get("code", "")
            }
        }
        for item in data
    ]

    # 🟢 Step 6 — Upload
    url = f"{BASE_URL}/api/projects/{PROJECT_ID}/import"

    headers = {
        "X-CSRFToken": csrftoken,
        "Content-Type": "application/json"
    }

    res = session.post(url, json=tasks, headers=headers)

    print("\n====== RESULT ======")
    print("UPLOAD STATUS:", res.status_code)
    print("RESPONSE:", res.text[:300])
    print("====================\n")


if __name__ == "__main__":
    upload_to_labelstudio()