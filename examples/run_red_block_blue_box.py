from __future__ import annotations
import json
from pathlib import Path
from embodiedmind.system import EmbodiedMindSystem
from embodiedmind.utils.config import load_yaml

if __name__ == "__main__":
    cfg = load_yaml("configs/tabletop.yaml")
    task = json.loads(Path("tasks/red_block_blue_box.json").read_text())
    system = EmbodiedMindSystem(task, cfg, run_dir="runs/demo_red_block_blue_box")
    result = system.run_episode(randomize=False)
    print("Final result:", result)
