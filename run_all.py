import argparse
import os
import subprocess
import sys


def run_step(step_name: str, script_name: str, env: dict) -> None:
    print(f"\n=== {step_name} ===")
    cmd = [sys.executable, script_name]
    result = subprocess.run(cmd, env=env)
    if result.returncode != 0:
        raise RuntimeError(f"Failed at {step_name}")


def build_env(mode: str) -> dict:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"

    if mode == "fast":
        env["MAX_AUTO_SAMPLES"] = env.get("MAX_AUTO_SAMPLES", "80")
        env["MAX_TRAIN_SAMPLES"] = env.get("MAX_TRAIN_SAMPLES", "24")
        env["TRAIN_EPOCHS"] = env.get("TRAIN_EPOCHS", "1")
        env["TRAIN_BATCH_SIZE"] = env.get("TRAIN_BATCH_SIZE", "8")
        env["USE_MINILM"] = env.get("USE_MINILM", "0")
    else:
        env["USE_MINILM"] = env.get("USE_MINILM", "1")

    return env


def main() -> None:
    parser = argparse.ArgumentParser(description="Run full labeling + training pipeline.")
    parser.add_argument(
        "--mode",
        choices=["fast", "full"],
        default="fast",
        help="fast: quick local run, full: slower higher-quality run",
    )
    parser.add_argument(
        "--skip-step1",
        action="store_true",
        help="Skip dataset prep + upload, run training pipeline only",
    )
    args = parser.parse_args()

    env = build_env(args.mode)

    if not args.skip_step1:
        run_step("Step 1: Data + Upload pipeline", "pipeline.py", env)

    run_step("Step 3: Training pipeline", "training_pipeline.py", env)
    print("\nPipeline completed successfully.")


if __name__ == "__main__":
    main()
