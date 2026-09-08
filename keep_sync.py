import threading
from datetime import datetime

import config

try:
    import gkeepapi
    from gkeepapi.node import List as KeepList
except ImportError:
    gkeepapi = None
    KeepList = None


class KeepSyncError(Exception):
    pass


def _now_str():
    return datetime.now().isoformat(timespec="seconds")


class KeepSync:
    """Handles gkeepapi login + push/pull merge against two Keep checklist notes.
    sync() is blocking - callers must run it off the Tk main thread."""

    def __init__(self):
        self._keep = None
        self._logged_in = False
        self._lock = threading.Lock()

    def _ensure_login(self):
        if self._logged_in:
            return True

        if gkeepapi is None:
            raise KeepSyncError("gkeepapi is not installed")
        if not config.GOOGLE_KEEP_EMAIL or not config.GOOGLE_KEEP_MASTER_TOKEN:
            raise KeepSyncError("GOOGLE_KEEP_EMAIL / GOOGLE_KEEP_MASTER_TOKEN not configured")

        self._keep = gkeepapi.Keep()
        self._keep.resume(config.GOOGLE_KEEP_EMAIL, config.GOOGLE_KEEP_MASTER_TOKEN)
        self._logged_in = True
        return True

    def _find_note(self, title):
        matches = list(self._keep.find(func=lambda n: isinstance(n, KeepList) and n.title == title and not n.trashed))
        return matches[0] if matches else None

    def sync(self, state):
        """Push locally-pending done-state changes, then pull fresh task lists
        from the two configured Keep notes, merging into `state` in place.
        Raises KeepSyncError on failure; never leaves `state` half-corrupted -
        on failure the caller should keep serving the state as it was before
        this call (this function returns the same dict on both paths)."""
        with self._lock:
            try:
                self._ensure_login()

                major_note = self._find_note(config.GOOGLE_KEEP_MAJOR_NOTE_TITLE)
                minor_note = self._find_note(config.GOOGLE_KEEP_MINOR_NOTE_TITLE)

                self._push_pending(state, "major_tasks", major_note)
                self._push_pending(state, "minor_tasks", minor_note)

                self._keep.sync()

                self._merge_section(state, "major_tasks", major_note, config.TODO_MAX_MAJOR)
                self._merge_section(state, "minor_tasks", minor_note, config.TODO_MAX_MINOR)

                state["last_synced_at"] = _now_str()
                state["last_sync_error"] = None
                return state
            except Exception as e:
                print(f"[keep_sync] sync failed: {e}")
                state["last_sync_error"] = str(e)
                raise KeepSyncError(str(e)) from e

    def _push_pending(self, state, section_key, note):
        if note is None:
            return
        items_by_id = {item.id: item for item in note.items}
        for task in state.get(section_key, []):
            if not task.get("pending_push"):
                continue
            item = items_by_id.get(task.get("keep_item_id"))
            if item is None:
                # Item vanished from Keep before we could push - drop the flag,
                # the next pull will reconcile (task will simply disappear).
                task["pending_push"] = False
                continue
            try:
                item.checked = task["done"]
                task["pending_push"] = False
            except Exception as e:
                print(f"[keep_sync] push failed for task {task.get('id')}: {e}")
                # leave pending_push True - retried next cycle

    def _merge_section(self, state, section_key, note, max_items):
        if note is None:
            # Note missing (renamed/deleted) - leave existing local list untouched.
            return

        existing_by_id = {t["id"]: t for t in state.get(section_key, [])}
        keep_items = note.items
        overflow_key = "major_overflow_count" if section_key == "major_tasks" else "minor_overflow_count"
        state[overflow_key] = max(0, len(keep_items) - max_items)

        new_list = []
        for keep_item in keep_items[:max_items]:
            local_id = f"keep:{keep_item.id}"
            existing = existing_by_id.get(local_id)
            now = _now_str()

            if existing is None:
                task = {
                    "id": local_id,
                    "text": keep_item.text,
                    "done": bool(keep_item.checked),
                    "keep_item_id": keep_item.id,
                    "keep_note_id": note.id,
                    "pending_push": False,
                    "created_at": now,
                    "updated_at": now,
                }
                if section_key == "major_tasks":
                    task["sessions"] = []
                new_list.append(task)
            else:
                existing["text"] = keep_item.text
                if not existing.get("pending_push"):
                    existing["done"] = bool(keep_item.checked)
                existing["updated_at"] = now
                new_list.append(existing)

        state[section_key] = new_list


keep_sync = KeepSync()
