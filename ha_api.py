import requests
import config
import threading

class HomeAssistantAPI:
    def __init__(self):
        self.base_url = config.HA_BASE_URL
        self.token = config.HA_ACCESS_TOKEN
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        self.available = bool(self.token)

    def get_entity_state(self, entity_id):
        if not self.available: return None
        try:
            url = f"{self.base_url}/api/states/{entity_id}"
            res = requests.get(url, headers=self.headers, timeout=5)
            if res.status_code == 200:
                return res.json()
        except Exception as e:
            print(f"HA Fetch Error ({entity_id}): {e}")
        return None

    def toggle_entity(self, entity_id, domain="homeassistant"):
        # Domain 'homeassistant' generic toggle works for most switch/light/media_player
        if not self.available: return
        
        # Determine domain if not generic
        if "." in entity_id:
             domain = entity_id.split(".")[0]
             
        service = "toggle"
        # Optional: fine tune service based on domain if needed, but 'toggle' is standard.
        
        def _call():
            try:
                url = f"{self.base_url}/api/services/{domain}/{service}"
                data = {"entity_id": entity_id}
                requests.post(url, headers=self.headers, json=data, timeout=5)
            except Exception as e:
                print(f"HA Service Error: {e}")

        # Fire and forget in background
        threading.Thread(target=_call, daemon=True).start()

# Singleton instance
ha_client = HomeAssistantAPI()
