import json
import os
import torch
from transformers import AutoTokenizer, AutoModel

MODEL_NAME = "microsoft/graphcodebert-base"
EPOCHS = int(os.getenv("TRAIN_EPOCHS", "1"))
MAX_SAMPLES = int(os.getenv("MAX_TRAIN_SAMPLES", "24"))
LOG_EVERY = int(os.getenv("TRAIN_LOG_EVERY", "20"))
MAX_LENGTH = int(os.getenv("MAX_SEQ_LEN", "128"))
BATCH_SIZE = int(os.getenv("TRAIN_BATCH_SIZE", "8"))

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

def train():
    data = json.load(open("final_train.json"))

    optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5)

    model.train()

    data = data[:MAX_SAMPLES]
    print(f"Training on {len(data)} samples for {EPOCHS} epoch(s) on {device}.")

    for epoch in range(EPOCHS):
        total_loss = 0

        for start in range(0, len(data), BATCH_SIZE):
            batch = data[start : start + BATCH_SIZE]
            queries = [
                item.get("query") or item.get("hard_query") or item.get("soft_query", "")
                for item in batch
            ]
            codes = [item["code"] for item in batch]
            labels = torch.tensor([item["label"] for item in batch], dtype=torch.float, device=device)

            q = tokenizer(queries, return_tensors="pt", truncation=True, padding=True, max_length=MAX_LENGTH)
            c = tokenizer(codes, return_tensors="pt", truncation=True, padding=True, max_length=MAX_LENGTH)
            q = {k: v.to(device) for k, v in q.items()}
            c = {k: v.to(device) for k, v in c.items()}

            q_emb = model(**q).last_hidden_state[:, 0, :]
            c_emb = model(**c).last_hidden_state[:, 0, :]

            sim = torch.cosine_similarity(q_emb, c_emb)
            loss = torch.nn.functional.binary_cross_entropy_with_logits(sim, labels)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            step = (start // BATCH_SIZE) + 1
            if step % LOG_EVERY == 0:
                print(f"Epoch {epoch + 1} Step {step} Loss: {loss.item():.4f}")

        print(f"Epoch {epoch} Loss: {total_loss}")

    print("✅ Training complete")

if __name__ == "__main__":
    train()