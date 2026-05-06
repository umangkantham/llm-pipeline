import json
import os

INPUT = "data/processed/cleaned.json"
HUMAN = "train.json"
OUTPUT = "auto.json"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
MAX_AUTO = 1000
SIM_THRESHOLD = 0.6
USE_MINILM = os.getenv("USE_MINILM", "0") == "1"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    max_auto = int(os.getenv("MAX_AUTO_SAMPLES", str(MAX_AUTO)))
    all_data = load_json(INPUT)
    human = load_json(HUMAN)

    human_keys = {
        (item.get("query", "").strip(), item.get("code", "").strip()) for item in human
    }
    candidates = []
    for item in all_data:
        query = item.get("query") or item.get("hard_query") or item.get("soft_query", "")
        code = item.get("code", "")
        key = (query.strip(), code.strip())
        if key not in human_keys and query and code:
            candidates.append({"query": query, "code": code})

    if not candidates:
        with open(OUTPUT, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2)
        print("✅ Auto-labeled 0 samples")
        return

    sims = []
    if USE_MINILM:
        from sentence_transformers import SentenceTransformer, util

        model = SentenceTransformer(MODEL_NAME)
        query_embeddings = model.encode([c["query"] for c in candidates], convert_to_tensor=True)
        code_embeddings = model.encode([c["code"] for c in candidates], convert_to_tensor=True)
        sims = util.cos_sim(query_embeddings, code_embeddings).diagonal().tolist()
    else:
        # Fast heuristic mode: overlap between query tokens and code tokens.
        for item in candidates:
            q_tokens = set(item["query"].lower().replace("_", " ").split())
            c_tokens = set(item["code"].lower().replace("_", " ").split())
            if not q_tokens:
                sims.append(0.0)
                continue
            sims.append(len(q_tokens & c_tokens) / max(1, len(q_tokens)))

    auto = []
    for item, sim in zip(candidates, sims):
        label = 1 if sim >= SIM_THRESHOLD else 0
        auto.append({"query": item["query"], "code": item["code"], "label": label})
        if len(auto) >= max_auto:
            break

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(auto, f, indent=2)

    print(f"✅ Auto-labeled {len(auto)} samples")


if __name__ == "__main__":
    main()
