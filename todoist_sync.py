import threading
from datetime import datetime

import config

try:
    from todoist_api_python.api import TodoistAPI
except ImportError:
    TodoistAPI = None


class TodoistSyncError(Exception):
    pass


def _now_str():
    return datetime.now().isoformat(timespec="seconds")


class TodoistSync:
    """Handles Todoist API token auth + push/pull merge against two projects
    (major/minor). sync() is blocking - callers must run it off the Tk main
    thread.

    Todoist's task-list endpoint only returns ACTIVE (open) tasks - a
    completed task simply disappears from it, unlike Keep's checklist items
    which stay put with a checked flag. So unlike a Keep-style sync, this
    does NOT rebuild each section strictly from the remote list every sync:
    a locally-known task that drops out of the active list is treated as
    completed (by us or via the Todoist app) and kept displayed - with
    done=True - for the rest of the day instead of vanishing."""

    def __init__(self):
        self._api = None
        self._lock = threading.Lock()

    def _ensure_client(self):
        if self._api is not None:
            return
        if TodoistAPI is None:
            raise TodoistSyncError("todoist-api-python is not installed")
        if not config.TODOIST_API_TOKEN:
            raise TodoistSyncError("TODOIST_API_TOKEN not configured")
        self._api = TodoistAPI(config.TODOIST_API_TOKEN)

    def _find_project(self, name):
        for page in self._api.get_projects():
            for p in page:
                if p.name == name:
                    return p
        return None

    def _fetch_active_tasks(self, project_id):
        tasks = []
        for page in self._api.get_tasks(project_id=project_id):
            tasks.extend(page)
        tasks.sort(key=lambda t: t.order)
        return tasks

    def sync(self, state):
        """Push locally-pending done-state changes, then pull fresh task
        lists from the two configured Todoist projects, merging into `state`
        in place. Raises TodoistSyncError on failure; `state` is left as
        far along as it got (partial progress is fine, caller persists
        whatever state comes back either way)."""
        with self._lock:
            try:
                self._ensure_client()

                self._push_pending(state, "major_tasks")
                self._push_pending(state, "minor_tasks")

                major_project = self._find_project(config.TODOIST_MAJOR_PROJECT_NAME)
                minor_project = self._find_project(config.TODOIST_MINOR_PROJECT_NAME)

                self._merge_section(state, "major_tasks", major_project, config.TODO_MAX_MAJOR)
                self._merge_section(state, "minor_tasks", minor_project, config.TODO_MAX_MINOR)

                state["last_synced_at"] = _now_str()
                state["last_sync_error"] = None
                return state
            except Exception as e:
                print(f"[todoist_sync] sync failed: {e}")
                state["last_sync_error"] = str(e)
                raise TodoistSyncError(str(e)) from e

    def _push_pending(self, state, section_key):
        for task in state.get(section_key, []):
            if not task.get("pending_push"):
                continue
            todoist_id = task.get("todoist_task_id")
            if not todoist_id:
                task["pending_push"] = False
                continue
            try:
                if task["done"]:
                    self._api.complete_task(todoist_id)
                else:
                    self._api.uncomplete_task(todoist_id)
                task["pending_push"] = False
            except Exception as e:
                print(f"[todoist_sync] push failed for task {task.get('id')}: {e}")
                # leave pending_push True - retried next cycle

    def _merge_section(self, state, section_key, project, max_items):
        overflow_key = "major_overflow_count" if section_key == "major_tasks" else "minor_overflow_count"

        if project is None:
            # Project missing (renamed/deleted) - leave existing local list untouched.
            return

        active_tasks = self._fetch_active_tasks(project.id)
        active_by_id = {t.id: t for t in active_tasks}

        updated_list = []
        for local in state.get(section_key, []):
            todoist_id = local.get("todoist_task_id")
            remote = active_by_id.get(todoist_id)
            now = _now_str()
            if remote is not None:
                local["text"] = remote.content
                if not local.get("pending_push"):
                    local["done"] = False
                local["updated_at"] = now
            else:
                # No longer active: completed (by us or in the app) or deleted.
                # Either way, stop treating it as active but keep it visible
                # for the rest of today rather than dropping it.
                if not local.get("pending_push"):
                    local["done"] = True
                    local["updated_at"] = now
            updated_list.append(local)

        known_ids = {t.get("todoist_task_id") for t in updated_list}
        slots_left = max_items - len(updated_list)
        overflow = 0
        for remote in active_tasks:
            if remote.id in known_ids:
                continue
            if slots_left > 0:
                now = _now_str()
                task = {
                    "id": f"todoist:{remote.id}",
                    "text": remote.content,
                    "done": False,
                    "todoist_task_id": remote.id,
                    "todoist_project_id": project.id,
                    "pending_push": False,
                    "created_at": now,
                    "updated_at": now,
                }
                if section_key == "major_tasks":
                    task["sessions"] = []
                updated_list.append(task)
                slots_left -= 1
            else:
                overflow += 1

        state[section_key] = updated_list
        state[overflow_key] = overflow


todoist_sync = TodoistSync()
