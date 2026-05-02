from __future__ import annotations
import argparse, json, time
from pathlib import Path
from embodiedmind.system import EmbodiedMindSystem
from embodiedmind.utils.config import load_yaml
from evaluation.metrics import summarize

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/eval_red_block_blue_box.yaml")
    parser.add_argument("--episodes", type=int, default=100)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    cfg = load_yaml(args.config)
    task = json.loads(Path(cfg["task_file"]).read_text())
    run_dir = Path(args.out or f"runs/eval_{int(time.time())}")
    run_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for ep in range(args.episodes):
        system = EmbodiedMindSystem(task, cfg, run_dir=run_dir / f"episode_{ep:03d}")
        results.append(system.run_episode(randomize=True))

    summary = summarize(results)
    payload = {"config": args.config, "episodes": args.episodes, "summary": summary.__dict__, "results": results}
    (run_dir / "summary.json").write_text(json.dumps(payload, indent=2))
    print(json.dumps(summary.__dict__, indent=2))

if __name__ == "__main__":
    main()
