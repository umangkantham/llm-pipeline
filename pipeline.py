import subprocess

def run(step, cmd):
    print(f"\n🚀 {step}")
    result = subprocess.run(cmd, shell=True)

    if result.returncode != 0:
        raise Exception(f"❌ Failed at {step}")

def main():
    run("Repo Sync", "python scripts/repo_sync.py")
    run("Extract Functions", "python scripts/extract_functions.py")
    run("Clean Data", "python scripts/clean_data.py")
    run("Build Dataset", "python scripts/build_dataset.py")

    # 🔥 DVC versioning step
    run("DVC Track", "dvc add data/processed/instruct_v1")

    run("Upload to Label Studio", "python scripts/upload_labelstudio.py")

    print("\n✅ FULL PIPELINE COMPLETE")

if __name__ == "__main__":
    main()