import requests
import config
import threading
from app_logging import logger
from security import INSECURE_HTTP_NOTICE, entity_id_ok, ha_url_problem, url_is_http

class HomeAssistantAPI:
    def __init__(self):
        self.base_url = (config.HA_BASE_URL or "").strip().rstrip("/")
        self.token = config.HA_ACCESS_TOKEN
        self.available = False
        self.disabled_reason = None
        self.insecure_http = False
        self.session = None
        if not self.token:
            return

        problem = ha_url_problem(
            self.base_url, allow_insecure_http=config.HA_ALLOW_INSECURE_HTTP
        )
        if problem:
            self.disabled_reason = problem
            logger.error("%s", problem)
            return

        self.insecure_http = url_is_http(self.base_url)
        if self.insecure_http:
            logger.warning("%s", INSECURE_HTTP_NOTICE)

        # trust_env is off so HTTP_PROXY cannot receive the bearer token.
        # Redirects are off so a 30x cannot forward the token to another host.
        self.session = requests.Session()
        self.session.trust_env = False
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        })
        self.available = True

    def get_entity_state(self, entity_id):
        if not self.available:
            return None
        if not entity_id_ok(entity_id):
            logger.error("Refusing HA request for invalid entity id: %s", entity_id)
            return None
        try:
            url = f"{self.base_url}/api/states/{entity_id}"
            res = self.session.get(url, timeout=5, allow_redirects=False)
            if 300 <= res.status_code < 400:
                logger.error("HA returned a redirect (%s). Set HA_BASE_URL to the final URL.", res.status_code)
                return None
            if res.status_code == 200:
                return res.json()
        except Exception as e:
            logger.error(f"HA Fetch Error ({entity_id}): {e}")
        return None

    def toggle_entity(self, entity_id, domain="homeassistant"):
        # Domain 'homeassistant' generic toggle works for most switch/light/media_player
        if not self.available:
            return
        if not entity_id_ok(entity_id):
            logger.error("Refusing HA toggle for invalid entity id: %s", entity_id)
            return

        domain = entity_id.split(".", 1)[0]
        service = "toggle"

        def _call():
            try:
                url = f"{self.base_url}/api/services/{domain}/{service}"
                data = {"entity_id": entity_id}
                res = self.session.post(url, json=data, timeout=5, allow_redirects=False)
                if 300 <= res.status_code < 400:
                    logger.error("HA returned a redirect (%s). Set HA_BASE_URL to the final URL.", res.status_code)
            except Exception as e:
                logger.error(f"HA Service Error: {e}")

        # Fire and forget in background
        threading.Thread(target=_call, daemon=True).start()

# Singleton instance
ha_client = HomeAssistantAPI()
