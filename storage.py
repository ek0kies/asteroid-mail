import json
from pathlib import Path


SAVE_FILE = Path(__file__).resolve().parent / ".asteroid_mail_save.json"


def load_best_score() -> int:
    try:
        payload = json.loads(SAVE_FILE.read_text(encoding="utf-8"))
        score = int(payload.get("best_score", 0))
        return max(score, 0)
    except (FileNotFoundError, ValueError, TypeError, json.JSONDecodeError):
        return 0


def save_best_score(score: int) -> None:
    try:
        SAVE_FILE.write_text(
            json.dumps({"best_score": max(int(score), 0)}, ensure_ascii=True, indent=2),
            encoding="utf-8",
        )
    except OSError:
        # Persist failure should not block gameplay.
        return
