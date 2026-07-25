import http.server
import os
import sys

PORT = 5173
DIRECTORY = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else '.'

class SPALocHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        # Check if the requested path is a file (e.g. assets, images)
        path = self.translate_path(self.path)
        if not os.path.exists(path) or os.path.isdir(path):
            # Fallback to index.html for SPA routes
            self.path = '/index.html'
        return super().do_GET()

if __name__ == '__main__':
    print(f"Serving SPA directory {DIRECTORY} on port {PORT}")
    http.server.test(HandlerClass=SPALocHandler, port=PORT, bind='0.0.0.0')
