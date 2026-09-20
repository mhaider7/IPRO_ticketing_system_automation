from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    seed_file: Path
    webhook_url: str | None = None
    webhook_timeout_seconds: float = 3.0

    @classmethod
    def from_env(cls) -> "Settings":
        sandbox_dir = Path(__file__).resolve().parents[1]
        data_dir = Path(os.getenv("SANDBOX_DATA_DIR", sandbox_dir / "data"))
        seed_file = Path(
            os.getenv("SANDBOX_SEED_FILE", data_dir / "seed_tickets.json")
        )
        webhook_url = os.getenv("PIPELINE_WEBHOOK_URL") or None
        timeout = float(os.getenv("WEBHOOK_TIMEOUT_SECONDS", "3"))
        return cls(
            data_dir=data_dir,
            seed_file=seed_file,
            webhook_url=webhook_url,
            webhook_timeout_seconds=timeout,
        )
