import io
import logging
import os
import stat
import tempfile
import unittest
from unittest import mock

from app_logging import RedactingFormatter, logger as app_logger
from security import (
    ConfirmGate,
    entity_id_ok,
    ha_url_problem,
    redact,
    restrict_owner_only,
    restrict_owner_tree,
    run_power_action,
    system_power_argv,
)


class RedactTests(unittest.TestCase):
    def test_weather_url_loses_api_key(self):
        secret = "wk_test_91f0c0aa"
        previous = os.environ.get("OPENWEATHER_API_KEY")
        os.environ["OPENWEATHER_API_KEY"] = secret
        try:
            message = (
                "401 Client Error: Unauthorized for url: "
                "https://api.openweathermap.org/data/3.0/onecall?lat=59&lon=18"
                f"&exclude=minutely,alerts&appid={secret}&units=metric"
            )
            cleaned = redact(message)
        finally:
            if previous is None:
                os.environ.pop("OPENWEATHER_API_KEY", None)
            else:
                os.environ["OPENWEATHER_API_KEY"] = previous

        self.assertNotIn(secret, cleaned)
        self.assertIn("appid=***", cleaned)
        self.assertIn("lat=59", cleaned)

    def test_bearer_and_json_tokens_are_removed(self):
        text = 'Authorization: Bearer eyJhbGciOi.test.sig {"access_token": "abc123456789"}'
        cleaned = redact(text)
        self.assertNotIn("eyJhbGciOi.test.sig", cleaned)
        self.assertNotIn("abc123456789", cleaned)
        self.assertIn("Bearer ***", cleaned)

    def test_short_env_values_are_not_treated_as_secrets(self):
        os.environ["HA_ACCESS_TOKEN"] = "ab"
        try:
            cleaned = redact("abnormal token")
        finally:
            del os.environ["HA_ACCESS_TOKEN"]
        self.assertEqual(cleaned, "abnormal token")

    def test_formatter_redacts_rendered_traceback_text(self):
        secret = "td_test_aa91f0c0"
        os.environ["TODOIST_API_TOKEN"] = secret
        stream = io.StringIO()
        record_logger = logging.getLogger("redact-test")
        handler = logging.StreamHandler(stream)
        handler.setFormatter(RedactingFormatter("%(message)s"))
        record_logger.handlers = [handler]
        record_logger.propagate = False
        try:
            record_logger.error("sync failed: token %s", secret)
        finally:
            del os.environ["TODOIST_API_TOKEN"]
        self.assertNotIn(secret, stream.getvalue())
        self.assertIn("***", stream.getvalue())

    def test_app_logger_uses_redacting_formatter(self):
        self.assertTrue(app_logger.handlers)
        for handler in app_logger.handlers:
            self.assertIsInstance(handler.formatter, RedactingFormatter)

    def test_log_files_are_owner_only(self):
        from app_logging import LOG_DIR, LOG_FILE
        self.assertEqual(stat.S_IMODE(os.stat(LOG_DIR).st_mode), 0o700)
        self.assertEqual(stat.S_IMODE(os.stat(LOG_FILE).st_mode), 0o600)


class HomeAssistantUrlTests(unittest.TestCase):
    def test_local_http_is_allowed(self):
        for url in (
            "http://homeassistant.local:8123",
            "http://homeassistant:8123",
            "http://192.168.1.20:8123",
            "http://10.0.0.5:8123",
            "http://127.0.0.1:8123",
            "https://example.com",
        ):
            self.assertIsNone(ha_url_problem(url), url)

    def test_public_http_is_refused(self):
        for url in (
            "http://example.com",
            "http://8.8.8.8:8123",
            "http://2130706433",
            "http://0x7f000001",
            "http://169.254.169.254",
        ):
            self.assertIsNotNone(ha_url_problem(url), url)

    def test_override_allows_public_http(self):
        self.assertIsNone(ha_url_problem("http://example.com", allow_insecure_http=True))

    def test_credentials_and_bad_scheme_are_refused(self):
        self.assertIsNotNone(ha_url_problem("http://user:pass@homeassistant.local"))
        self.assertIsNotNone(ha_url_problem("ftp://homeassistant.local"))
        self.assertIsNotNone(ha_url_problem(""))

    def test_entity_ids_cannot_change_the_request_path(self):
        self.assertTrue(entity_id_ok("light.living_room"))
        self.assertTrue(entity_id_ok("sensor.pm2_5"))
        self.assertFalse(entity_id_ok("../etc/passwd"))
        self.assertFalse(entity_id_ok("light.room/../../api"))
        self.assertFalse(entity_id_ok("light.room?x=1"))
        self.assertFalse(entity_id_ok("Light.Room"))
        self.assertFalse(entity_id_ok(""))


class PowerAndPermissionTests(unittest.TestCase):
    def test_power_commands_are_argv_not_a_shell_string(self):
        self.assertEqual(
            system_power_argv("shutdown"),
            ["sudo", "-n", "shutdown", "-h", "now"],
        )
        self.assertEqual(system_power_argv("reboot"), ["sudo", "-n", "reboot"])
        with self.assertRaises(ValueError):
            system_power_argv("rm -rf /")

    def test_failed_sudo_is_reported_and_not_run_for_real(self):
        calls = []

        def runner(argv):
            calls.append(list(argv))
            return 1, "sudo: a password is required"

        ok, message = run_power_action("reboot", runner=runner)
        self.assertFalse(ok)
        self.assertEqual(message, "Needs passwordless sudo")
        self.assertEqual(calls, [["sudo", "-n", "reboot"]])

    def test_confirm_gate_needs_two_presses_of_the_same_action(self):
        gate = ConfirmGate()
        self.assertFalse(gate.arm("shutdown"))
        self.assertFalse(gate.arm("reboot"))
        self.assertTrue(gate.arm("reboot"))
        self.assertFalse(gate.arm("reboot"))
        gate.clear()
        self.assertFalse(gate.arm("shutdown"))

    def test_restrict_owner_only_skips_symlinks(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = os.path.join(tmp, "secret.txt")
            link = os.path.join(tmp, "link.txt")
            with open(target, "w", encoding="utf-8") as handle:
                handle.write("token")
            os.chmod(target, 0o644)
            os.symlink(target, link)
            restrict_owner_only(link)
            self.assertEqual(stat.S_IMODE(os.stat(target).st_mode), 0o644)
            restrict_owner_only(target)
            self.assertEqual(stat.S_IMODE(os.stat(target).st_mode), 0o600)

            nested = os.path.join(tmp, "tree")
            os.mkdir(nested)
            inside = os.path.join(nested, "state.json")
            with open(inside, "w", encoding="utf-8") as handle:
                handle.write("{}")
            os.chmod(nested, 0o755)
            os.chmod(inside, 0o644)
            restrict_owner_tree(nested)
            self.assertEqual(stat.S_IMODE(os.stat(nested).st_mode), 0o700)
            self.assertEqual(stat.S_IMODE(os.stat(inside).st_mode), 0o600)

    def test_home_assistant_client_blocks_bad_urls_and_entity_ids(self):
        import requests
        import config
        import ha_api

        with mock.patch.object(config, "HA_ACCESS_TOKEN", "ha_test_token_91f0"), \
             mock.patch.object(config, "HA_BASE_URL", "http://example.com:8123"), \
             mock.patch.object(config, "HA_ALLOW_INSECURE_HTTP", False):
            blocked = ha_api.HomeAssistantAPI()
        self.assertFalse(blocked.available)
        self.assertIn("example.com", blocked.disabled_reason)
        self.assertIsNone(blocked.session)

        with mock.patch.object(config, "HA_ACCESS_TOKEN", "ha_test_token_91f0"), \
             mock.patch.object(config, "HA_BASE_URL", "http://homeassistant.local:8123"):
            client = ha_api.HomeAssistantAPI()
        self.assertTrue(client.available)
        self.assertFalse(client.session.trust_env)
        self.assertIsNone(client.get_entity_state("../etc/passwd"))

        response = mock.Mock(status_code=200)
        response.json.return_value = {"state": "on"}
        client.session.get = mock.Mock(return_value=response)
        self.assertEqual(client.get_entity_state("light.lamp"), {"state": "on"})
        self.assertFalse(client.session.get.call_args.kwargs["allow_redirects"])

        redirect = mock.Mock(status_code=302)
        client.session.get = mock.Mock(return_value=redirect)
        self.assertIsNone(client.get_entity_state("light.lamp"))
        redirect.json.assert_not_called()
        self.assertIsInstance(client.session, requests.Session)

    def test_settings_buttons_require_a_second_tap(self):
        import tkinter as tk
        import settings_page

        root = tk.Tk()
        root.withdraw()
        try:
            page = settings_page.SettingsPage(root)
            with mock.patch("settings_page.run_power_action", return_value=(False, "Needs passwordless sudo")) as power:
                page.shutdown()
                power.assert_not_called()
                self.assertEqual(page.power_btn.text_str, "Confirm?")
                page.shutdown()
                power.assert_called_once_with("shutdown")
            self.assertEqual(page.power_btn.subtitle, "Needs passwordless sudo")

            with mock.patch("settings_page.sys.exit") as exit_app:
                page.exit_app()
                exit_app.assert_not_called()
                page.exit_app()
                exit_app.assert_called_once_with(0)
        finally:
            root.destroy()

    def test_non_linux_power_action_does_not_call_sudo(self):
        with mock.patch("platform.system", return_value="Windows"):
            ok, message = run_power_action("shutdown", runner=lambda argv: (_ for _ in ()).throw(AssertionError("sudo")))
        self.assertTrue(ok)
        self.assertEqual(message, "")


if __name__ == "__main__":
    unittest.main()
