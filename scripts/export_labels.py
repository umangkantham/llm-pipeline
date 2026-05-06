import requests
import os

BASE_URL = "http://localhost:8080"
PROJECT_FILE = "project_id.txt"
USERNAME = os.getenv("LABEL_STUDIO_EMAIL")
PASSWORD = os.getenv("LABEL_STUDIO_PASSWORD")


def load_project_id():
    if os.path.exists(PROJECT_FILE):
        with open(PROJECT_FILE, "r", encoding="utf-8") as f:
            value = f.read().strip()
            if value:
                return int(value)
    raise FileNotFoundError("project_id.txt missing. Run pipeline.py upload step first.")

def export_labels():
    if not USERNAME or not PASSWORD:
        raise RuntimeError("Set LABEL_STUDIO_EMAIL and LABEL_STUDIO_PASSWORD before exporting labels.")

    project_id = load_project_id()
    session = requests.Session()

    session.get(BASE_URL)
    csrftoken = session.cookies.get("csrftoken")
    login_url = f"{BASE_URL}/user/login/"
    headers = {"X-CSRFToken": csrftoken}
    login_res = session.post(
        login_url,
        data={"email": USERNAME, "password": PASSWORD},
        headers=headers,
    )
    login_res.raise_for_status()

    url = f"{BASE_URL}/api/projects/{project_id}/export?exportType=JSON"
    res = session.get(url, headers={"X-CSRFToken": csrftoken})
    res.raise_for_status()

    with open("labelstudio_export.json", "w", encoding="utf-8") as f:
        f.write(res.text)

    print("✅ Labels exported")

if __name__ == "__main__":
    export_labels()