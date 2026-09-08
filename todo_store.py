import json
import os
import tempfile
from datetime import date, datetime

import config

STATE_PATH = os.path.join(config.TODO_DATA_DIR, "state.json")
HISTORY_DIR = os.path.join(config.TODO_DATA_DIR, "history")


def _today_str():
    return date.today().isoformat()


def _now_str():
    return datetime.now().isoformat(timespec="seconds")


def _new_empty_state(day=None):
    return {
        "date": day or _today_str(),
        "major_tasks": [],
        "minor_tasks": [],
        "major_overflow_count": 0,
        "minor_overflow_count": 0,
        "last_synced_at": None,
        "last_sync_error": None,
    }


def _atomic_write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    dir_name = os.path.dirname(path)
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, prefix=".tmp-", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2)
        os.replace(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def load_state():
    """Reads today's state, archiving+resetting first if the stored day has rolled over.
    Idempotent - safe to call repeatedly."""
    if not os.path.exists(STATE_PATH):
        state = _new_empty_state()
        save_state(state)
        return state

    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            state = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"[todo_store] Failed to read state.json ({e}), starting fresh")
        state = _new_empty_state()
        save_state(state)
        return state

    if state.get("date") != _today_str():
        archive_and_reset(state)
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            state = json.load(f)

    return state


def save_state(state):
    _atomic_write_json(STATE_PATH, state)


def archive_and_reset(state):
    """Archives the given (presumably stale) state into history, then overwrites
    state.json with a fresh empty day. Skips archiving if that day's history
    file already exists (guards against double-archiving)."""
    old_date = state.get("date")
    if old_date:
        history_path = os.path.join(HISTORY_DIR, f"{old_date}.json")
        if not os.path.exists(history_path):
            snapshot = {
                "date": old_date,
                "major_tasks": [
                    {k: v for k, v in t.items() if k != "pending_push"}
                    for t in state.get("major_tasks", [])
                ],
                "minor_tasks": [
                    {k: v for k, v in t.items() if k != "pending_push"}
                    for t in state.get("minor_tasks", [])
                ],
                "archived_at": _now_str(),
            }
            _atomic_write_json(history_path, snapshot)

    fresh = _new_empty_state()
    save_state(fresh)


def list_history_dates():
    if not os.path.isdir(HISTORY_DIR):
        return []
    dates = [
        fname[:-5]
        for fname in os.listdir(HISTORY_DIR)
        if fname.endswith(".json")
    ]
    return sorted(dates, reverse=True)


def load_history(date_str):
    path = os.path.join(HISTORY_DIR, f"{date_str}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
