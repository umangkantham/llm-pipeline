import os
import json

INPUT_DIR = "data/raw/repo"
OUTPUT = "data/processed/functions.json"

def main():
    data = []

    for root, _, files in os.walk(INPUT_DIR):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)

                try:
                    with open(path, "r", encoding="utf-8") as f:
                        for line in f:
                            if line.strip().startswith("def "):
                                name = line.split("def ")[1].split("(")[0]

                                data.append({
                                    "query": name,
                                    "code": line.strip()
                                })
                except:
                    pass

    os.makedirs("data/processed", exist_ok=True)

    with open(OUTPUT, "w") as f:
        json.dump(data, f, indent=2)

    print(f"✅ Extracted {len(data)} functions")

if __name__ == "__main__":
    main()
