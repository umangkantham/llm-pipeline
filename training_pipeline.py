import os
import sys

def run(step, command):
    print(f"\n🚀 {step}")
    code = os.system(command)
    if code != 0:
        raise RuntimeError(f"❌ Failed at {step}")

def main():
    py = f"\"{sys.executable}\""
    run("Export Labels", f"{py} scripts/export_labels.py")
    run("Convert Labels", f"{py} scripts/convert_labels.py")
    run("Auto Label", f"{py} scripts/auto_label.py")
    run("Merge Dataset", f"{py} scripts/merge.py")
    run("Train Model", f"{py} scripts/train.py")

if __name__ == "__main__":
    main()