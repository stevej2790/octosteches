#!/usr/bin/env python3
"""Simple local server for the Ensitech website recreation."""

import http.server
import socketserver
import os

DEFAULT_PORT = 8888
DIRECTORY = os.path.dirname(os.path.abspath(__file__))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()


if __name__ == "__main__":
    import sys

    os.chdir(DIRECTORY)
    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    socketserver.TCPServer.allow_reuse_address = True

    for attempt in range(10):
        try:
            with socketserver.TCPServer(("", port), Handler) as httpd:
                print(f"Serving Ensitech website at http://localhost:{port}")
                print("Press Ctrl+C to stop")
                httpd.serve_forever()
            break
        except OSError:
            port += 1
