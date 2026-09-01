import json
import os
from datetime import date

STATE_PATH = "data/state.json"


def _empty_state(today: date) -> dict:
    return {"date": today.isoformat(), "morning": None, "lunch": None, "close": None}


def load_state(today: date) -> dict:
    """오늘 날짜의 상태를 불러온다. 날짜가 바뀌었으면 새로 시작한다."""
    if not os.path.exists(STATE_PATH):
        return _empty_state(today)

    with open(STATE_PATH, encoding="utf-8") as f:
        state = json.load(f)

    if state.get("date") != today.isoformat():
        return _empty_state(today)

    return state


def save_state(state: dict):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
