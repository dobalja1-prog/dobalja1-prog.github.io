import json
import os

HISTORY_PATH = "data/history.json"
MAX_ENTRIES = 3  # 각 브리핑 종류별로 최근 며칠치만 보관


def _load_all() -> dict:
    if not os.path.exists(HISTORY_PATH):
        return {"morning": [], "lunch": [], "close": []}
    with open(HISTORY_PATH, encoding="utf-8") as f:
        return json.load(f)


def get_recent(kind: str, before_date: str) -> list[dict]:
    """kind: "morning"/"lunch"/"close". 오늘(before_date) 이전의 최근 기록만 반환."""
    data = _load_all()
    entries = data.get(kind, [])
    return [e for e in entries if e["date"] < before_date][-MAX_ENTRIES:]


def add_entry(kind: str, date_str: str, text: str):
    data = _load_all()
    entries = data.get(kind, [])
    entries = [e for e in entries if e["date"] != date_str]  # 같은 날 재실행 시 교체
    entries.append({"date": date_str, "text": text})
    data[kind] = entries[-MAX_ENTRIES:]

    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
