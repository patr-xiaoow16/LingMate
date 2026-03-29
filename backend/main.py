from __future__ import annotations

import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from data import (
    coach_module,
    complete_module,
    perform_module_action,
    get_analysis,
    get_home,
    get_report,
    get_review,
    get_workspace,
    import_material,
    start_lesson,
)


HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8000"))


class LingMateHandler(BaseHTTPRequestHandler):
    server_version = "LingMateHTTP/1.0"

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        if not raw:
            return {}
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return {}

    def _send_json(self, payload: dict, status: int = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self._send_json({"ok": True})

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/api/health":
            self._send_json({"status": "ok"})
            return
        if path == "/api/home":
            self._send_json(get_home())
            return
        if path == "/api/review":
            self._send_json(get_review())
            return

        parts = [segment for segment in path.split("/") if segment]
        if len(parts) >= 4 and parts[:3] == ["api", "lessons", parts[2]]:
            lesson_id = parts[2]
            if parts[3] == "analysis":
                self._send_json(get_analysis(lesson_id))
                return
            if parts[3] == "workspace":
                module_index = None
                if "module" in query:
                    try:
                        module_index = int(query["module"][0])
                    except (TypeError, ValueError, IndexError):
                        module_index = None
                payload = get_workspace(lesson_id, module_index)
                self._send_json(payload)
                return
            if parts[3] == "report":
                self._send_json(get_report(lesson_id))
                return

        self._send_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        payload = self._read_json()

        if path == "/api/import":
            self._send_json(import_material(payload), status=HTTPStatus.CREATED)
            return

        parts = [segment for segment in path.split("/") if segment]
        if len(parts) >= 4 and parts[:3] == ["api", "lessons", parts[2]]:
            lesson_id = parts[2]
            if parts[3] == "start":
                self._send_json(start_lesson(lesson_id))
                return
            if len(parts) >= 6 and parts[3] == "modules":
                module_key = parts[4]
                action = parts[5]
                if action == "coach":
                    self._send_json(coach_module(lesson_id, module_key, payload))
                    return
                if action == "complete":
                    self._send_json(complete_module(lesson_id, module_key))
                    return
                if action == "action":
                    self._send_json(perform_module_action(lesson_id, module_key, payload))
                    return

        self._send_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)


def run() -> None:
    server = ThreadingHTTPServer((HOST, PORT), LingMateHandler)
    print(f"LingMate backend running at http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping LingMate backend...")
    finally:
        server.server_close()


if __name__ == "__main__":
    run()
