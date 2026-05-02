from __future__ import annotations
from datetime import datetime
from pathlib import Path
import json
from rich.console import Console

console = Console()

class RunLogger:
    def __init__(self, run_dir: str | Path | None = None):
        self.run_dir = Path(run_dir) if run_dir else None
        self.fp = None
        if self.run_dir:
            self.run_dir.mkdir(parents=True, exist_ok=True)
            self.fp = (self.run_dir / "events.jsonl").open("a")

    def log(self, module: str, message: str, **kwargs):
        ts = kwargs.pop("timestamp", None) or datetime(2026, 4, 30, 14, 21, 8).strftime("%Y-%m-%d %H:%M:%S")
        console.print(f"[dim][{ts}][/dim] [bold cyan][{module}][/bold cyan] {message}")
        if self.fp:
            record = {"time": ts, "module": module, "message": message, **kwargs}
            self.fp.write(json.dumps(record, ensure_ascii=False) + "\n")
            self.fp.flush()

    def close(self):
        if self.fp:
            self.fp.close()
