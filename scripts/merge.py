import json

human = json.load(open("train.json"))
auto = json.load(open("auto.json"))

final = human + auto

json.dump(final, open("final_train.json", "w"), indent=2)

print("✅ Final dataset:", len(final))