import os, sys, threading, http.server, asyncio, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib
asgi = importlib.import_module("app").app

class Handler(http.server.BaseHTTPRequestHandler):
    def _dispatch(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b""
        scope = {
            "type": "http", "asgi": {"version": "3.0"},
            "http_version": "1.1", "method": self.command,
            "path": self.path.split("?")[0], "query_string": b"",
            "raw_path": self.path.encode(),
            "headers": [(k.lower().encode(), v.encode()) for k, v in self.headers.items()],
            "client": self.client_address, "server": ("127.0.0.1", 8899),
        }
        messages = []
        sent = False
        async def receive():
            nonlocal sent
            if not sent:
                sent = True
                return {"type": "http.request", "body": body, "more_body": False}
            return {"type": "http.disconnect"}
        async def send(msg): messages.append(msg)
        asyncio.run(asgi(scope, receive, send))
        status, hdrs, payload = 500, [], b""
        for m in messages:
            if m["type"] == "http.response.start":
                status = m["status"]; hdrs = m.get("headers", [])
            elif m["type"] == "http.response.body":
                payload += m.get("body", b"")
        self.send_response(status)
        for k, v in hdrs: self.send_header(k.decode(), v.decode())
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)
    do_POST = do_GET = _dispatch
    def log_message(self, *a): pass

http.server.ThreadingHTTPServer(("127.0.0.1", 8899), Handler).serve_forever()
