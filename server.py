import os
import re
import sys
import mimetypes
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
WEB_DIR = os.path.dirname(os.path.abspath(__file__))

mimetypes.add_type("video/mp4", ".mp4")
mimetypes.add_type("audio/mpeg", ".mp3")
mimetypes.add_type("image/webp", ".webp")


class NgrokMediaHandler(SimpleHTTPRequestHandler):
    """
    Multi-threaded HTTP handler with HTTP Range (206 Partial Content) support
    so MP4 videos and MP3 audio stream instantaneously on iOS Safari & Android Chrome over ngrok.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def end_headers(self):
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Access-Control-Allow-Origin", "*")
        if self.path.endswith((".mp4", ".mp3", ".webp", ".jpg", ".png")):
            self.send_header("Cache-Control", "public, max-age=3600")
        super().end_headers()

    def send_head(self):
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            return super().send_head()
        if not os.path.exists(path):
            self.send_error(404, "File not found")
            return None

        range_header = self.headers.get("Range")
        if not range_header:
            return super().send_head()

        try:
            file_size = os.path.getsize(path)
            m = re.match(r"bytes=(\d+)-(\d*)", range_header)
            if not m:
                return super().send_head()

            start = int(m.group(1))
            end = int(m.group(2)) if m.group(2) else file_size - 1
            if start >= file_size:
                self.send_error(416, "Requested Range Not Satisfiable")
                return None

            end = min(end, file_size - 1)
            length = end - start + 1

            f = open(path, "rb")
            f.seek(start)
            self.range_slice = (start, length)

            ctype = self.guess_type(path)
            self.send_response(206)
            self.send_header("Content-type", ctype)
            self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
            self.send_header("Content-Length", str(length))
            self.send_header("Last-Modified", self.date_time_string(os.path.getmtime(path)))
            self.end_headers()
            return f
        except Exception:
            return super().send_head()

    def copyfile(self, source, outputfile):
        if hasattr(self, "range_slice") and self.range_slice:
            _, length = self.range_slice
            self.range_slice = None
            remaining = length
            buf_size = 64 * 1024
            while remaining > 0:
                chunk = source.read(min(buf_size, remaining))
                if not chunk:
                    break
                outputfile.write(chunk)
                remaining -= len(chunk)
        else:
            super().copyfile(source, outputfile)


if __name__ == "__main__":
    os.chdir(WEB_DIR)
    server = ThreadingHTTPServer(("0.0.0.0", PORT), NgrokMediaHandler)
    print(f"Serving Devishri & Chetan Wedding Invitation from: {WEB_DIR}")
    print(f"Local URL: http://localhost:{PORT}")
    print("Ready for ngrok tunnel! Run in another terminal:  ngrok http 8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        server.server_close()
